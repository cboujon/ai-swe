#!/usr/bin/env python3
import re
import json
import logging

from src.ai_model import generate_content
from src.prompt_loader import load_prompt
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def parse_markdown_spec(markdown):
    """
    Parse markdown specification into structured data
    
    Args:
        markdown (str): Markdown formatted specification text
    
    Returns:
        dict: Structured specification data
    """
    logger.debug("Parsing markdown specification")
    
    # Try to use Gemini first if available
    if GEMINI_API_KEY:
        try:
            spec = parse_with_gemini(markdown)
            if spec:
                return spec
        except Exception as e:
            logger.error(f"Error using Gemini to parse markdown: {e}", exc_info=True)
            logger.info("Falling back to regex-based parsing")
    
    # Fallback to regex parsing
    return parse_with_regex(markdown)

def parse_with_gemini(markdown):
    """
    Use Gemini to interpret the markdown and generate structured data
    
    Args:
        markdown (str): Markdown formatted specification text
    
    Returns:
        dict: Structured specification data or None if parsing failed
    """
    logger.info("Using Gemini to parse markdown")
    
    # Define the JSON schema separately to avoid nested f-string issues
    json_schema = '''{
  "title": "string",
  "description": "string",
  "classes": [
    {
      "name": "string",
      "attributes": [
        {
          "name": "string",
          "type": "string",
          "default": null or "string",
          "comment": null or "string"
        }
      ],
      "methods": [
        {
          "name": "string",
          "parameters": [
            {
              "name": "string",
              "type": "string"
            }
          ],
          "return_type": "string",
          "comment": null or "string"
        }
      ]
    }
  ],
  "architecture": {
    "components": [
      {
        "name": "string",
        "description": "string",
        "responsibilities": ["string"]
      }
    ],
    "connections": [
      {
        "source": "string",
        "target": "string",
        "description": "string"
      }
    ]
  },
  "use_cases": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "actors": ["string"],
      "preconditions": ["string"],
      "flow": [
        {
          "step": 1,
          "actor": "string",
          "action": "string",
          "message": "string"
        }
      ],
      "postconditions": ["string"]
    }
  ]
}'''
    
    # Cargar el prompt desde el archivo
    prompt_template = load_prompt('markdown_parser', 'parse_markdown')
    if not prompt_template:
        logger.error("Failed to load markdown parser prompt")
        return None
    
    # Rellenar el template con los datos
    prompt = prompt_template.format(
        markdown=markdown,
        json_schema=json_schema
    )
    
    # Get response from Gemini
    response = generate_content(prompt)
    
    if not response:
        logger.warning("No response from Gemini")
        return None
    
    try:
        # Extract JSON from response
        response_text = response.text
        
        # Look for JSON content
        if '```json' in response_text:
            # Extract code between Markdown code blocks
            start = response_text.find("```json")
            end = response_text.find("```", start + 7)
            if end > start:
                json_str = response_text[start + 7:end].strip()
        elif '```' in response_text:
            # Try any code block
            start = response_text.find("```")
            end = response_text.find("```", start + 3)
            if end > start:
                json_str = response_text[start + 3:end].strip()
        else:
            # Just use the whole response
            json_str = response_text.strip()
        
        # Parse the JSON
        spec = json.loads(json_str)
        
        # Ensure the spec has the expected structure
        ensure_spec_structure(spec)
        
        logger.info(f"Successfully parsed specification with Gemini: {spec['title']} with " 
                  f"{len(spec.get('classes', []))} classes, "
                  f"{len(spec.get('architecture', {}).get('components', []))} components, and "
                  f"{len(spec.get('use_cases', []))} use cases")
        
        return spec
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error in Gemini parsing: {e}", exc_info=True)
        return None

def ensure_spec_structure(spec):
    """
    Ensure the spec dictionary has the expected structure by initializing missing fields
    
    Args:
        spec (dict): The specification to validate and fix
    """
    if 'title' not in spec:
        spec['title'] = ''
    
    if 'description' not in spec:
        spec['description'] = ''
    
    if 'classes' not in spec:
        spec['classes'] = []
    
    if 'entities' not in spec:
        spec['entities'] = []
    
    if 'architecture' not in spec:
        spec['architecture'] = {}
    
    if 'components' not in spec['architecture']:
        spec['architecture']['components'] = []
    
    if 'connections' not in spec['architecture']:
        spec['architecture']['connections'] = []
    
    if 'use_cases' not in spec:
        spec['use_cases'] = []
    
    # Add IDs to use cases if not present
    for i, use_case in enumerate(spec['use_cases']):
        if 'id' not in use_case:
            use_case['id'] = f"UC{i+1}"

def parse_with_regex(markdown):
    """
    Parse markdown specification into structured data using regex
    
    Args:
        markdown (str): Markdown formatted specification text
    
    Returns:
        dict: Structured specification data
    """
    logger.info("Using regex to parse markdown")
    
    # Initialize the structured specification
    spec = {
        'title': '',
        'description': '',
        'classes': [],
        'entities': [],
        'architecture': {
            'components': [],
            'connections': []
        },
        'use_cases': []
    }
    
    # Extract title (first H1)
    title_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
    if title_match:
        spec['title'] = title_match.group(1).strip()
    
    # Extract general description
    desc_match = re.search(r'^##\s+Description\s*\n+(.*?)(?=^##|\Z)', markdown, re.MULTILINE | re.DOTALL)
    if desc_match:
        spec['description'] = desc_match.group(1).strip()
    
    # Extract classes
    classes_section = extract_section(markdown, 'Classes')
    if classes_section:
        class_blocks = re.findall(r'###\s+(.+?)\s*\n+(.*?)(?=###|\Z)', classes_section, re.DOTALL)
        for class_name, class_content in class_blocks:
            cls = {
                'name': class_name.strip(),
                'attributes': [],
                'methods': []
            }
            
            # Extract attributes
            attr_section = extract_subsection(class_content, 'Attributes')
            if attr_section:
                attrs = re.findall(r'-\s+(.+?)(?:\s*:\s*(.+?))?(?:\s+=\s+(.+?))?(?:\s+//\s*(.+?))?$', attr_section, re.MULTILINE)
                for attr in attrs:
                    name = attr[0].strip()
                    attr_type = attr[1].strip() if len(attr) > 1 and attr[1] else 'str'
                    default = attr[2].strip() if len(attr) > 2 and attr[2] else None
                    comment = attr[3].strip() if len(attr) > 3 and attr[3] else None
                    
                    cls['attributes'].append({
                        'name': name,
                        'type': attr_type,
                        'default': default,
                        'comment': comment
                    })
            
            # Extract methods
            method_section = extract_subsection(class_content, 'Methods')
            if method_section:
                methods = re.findall(r'-\s+(.+?)(?:\((.*?)\))?(?:\s*->\s*(.+?))?(?:\s+//\s*(.+?))?$', method_section, re.MULTILINE)
                for method in methods:
                    name = method[0].strip()
                    params = method[1].strip() if len(method) > 1 and method[1] else ''
                    return_type = method[2].strip() if len(method) > 2 and method[2] else 'None'
                    comment = method[3].strip() if len(method) > 3 and method[3] else None
                    
                    parsed_params = []
                    if params:
                        param_list = params.split(',')
                        for param in param_list:
                            param = param.strip()
                            param_parts = param.split(':')
                            param_name = param_parts[0].strip()
                            param_type = param_parts[1].strip() if len(param_parts) > 1 else 'Any'
                            parsed_params.append({
                                'name': param_name,
                                'type': param_type
                            })
                    
                    cls['methods'].append({
                        'name': name,
                        'parameters': parsed_params,
                        'return_type': return_type,
                        'comment': comment
                    })
            
            spec['classes'].append(cls)
    
    # Extract architecture components
    arch_section = extract_section(markdown, 'Architecture')
    if arch_section:
        component_blocks = re.findall(r'###\s+(.+?)\s*\n+(.*?)(?=###|\Z)', arch_section, re.DOTALL)
        for component_name, component_content in component_blocks:
            comp = {
                'name': component_name.strip(),
                'description': '',
                'responsibilities': []
            }
            
            # Extract description
            desc_match = re.search(r'^(.*?)(?=####|\Z)', component_content, re.DOTALL)
            if desc_match:
                comp['description'] = desc_match.group(1).strip()
            
            # Extract responsibilities
            resp_section = extract_subsection(component_content, 'Responsibilities')
            if resp_section:
                responsibilities = re.findall(r'-\s+(.+)$', resp_section, re.MULTILINE)
                comp['responsibilities'] = [r.strip() for r in responsibilities]
            
            # Extract interactions (connections)
            interact_section = extract_subsection(component_content, 'Interactions')
            if interact_section:
                interactions = re.findall(r'-\s+(.+?)\s*->\s*(.+?)(?:\s*:\s*(.+?))?$', interact_section, re.MULTILINE)
                for interaction in interactions:
                    source = component_name.strip()
                    target = interaction[0].strip()
                    description = interaction[2].strip() if len(interaction) > 2 and interaction[2] else ''
                    
                    spec['architecture']['connections'].append({
                        'source': source,
                        'target': target,
                        'description': description
                    })
            
            spec['architecture']['components'].append(comp)
    
    # Extract use cases
    use_cases_section = extract_section(markdown, 'Use Cases')
    if use_cases_section:
        use_case_blocks = re.findall(r'###\s+(.+?)\s*\n+(.*?)(?=###|\Z)', use_cases_section, re.DOTALL)
        for i, (use_case_name, use_case_content) in enumerate(use_case_blocks):
            use_case = {
                'id': f"UC{i+1}",
                'name': use_case_name.strip(),
                'description': '',
                'actors': [],
                'preconditions': [],
                'flow': [],
                'postconditions': []
            }
            
            # Extract description
            desc_match = re.search(r'^(.*?)(?=####|\Z)', use_case_content, re.DOTALL)
            if desc_match:
                use_case['description'] = desc_match.group(1).strip()
            
            # Extract actors
            actors_section = extract_subsection(use_case_content, 'Actors')
            if actors_section:
                actors = re.findall(r'-\s+(.+)$', actors_section, re.MULTILINE)
                use_case['actors'] = [a.strip() for a in actors]
            
            # Extract preconditions
            pre_section = extract_subsection(use_case_content, 'Preconditions')
            if pre_section:
                preconditions = re.findall(r'-\s+(.+)$', pre_section, re.MULTILINE)
                use_case['preconditions'] = [p.strip() for p in preconditions]
            
            # Extract flow
            flow_section = extract_subsection(use_case_content, 'Flow')
            if flow_section:
                flow_steps = re.findall(r'(\d+)\.\s+(.+?)\s*(?:->\s*(.+?))?(?:\s*:\s*(.+?))?$', flow_section, re.MULTILINE)
                for step in flow_steps:
                    step_num = int(step[0])
                    actor = step[1].strip()
                    action = step[2].strip() if len(step) > 2 and step[2] else ''
                    message = step[3].strip() if len(step) > 3 and step[3] else ''
                    
                    use_case['flow'].append({
                        'step': step_num,
                        'actor': actor,
                        'action': action,
                        'message': message
                    })
            
            # Extract postconditions
            post_section = extract_subsection(use_case_content, 'Postconditions')
            if post_section:
                postconditions = re.findall(r'-\s+(.+)$', post_section, re.MULTILINE)
                use_case['postconditions'] = [p.strip() for p in postconditions]
            
            spec['use_cases'].append(use_case)
    
    logger.debug(f"Parsed specification: {spec['title']} with {len(spec['classes'])} classes, "
                f"{len(spec['architecture']['components'])} components, and {len(spec['use_cases'])} use cases")
    
    return spec

def extract_section(markdown, section_name):
    """Extract a section from the markdown by its heading"""
    pattern = rf'^##\s+{section_name}\s*\n+(.*?)(?=^##|\Z)'
    match = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ''

def extract_subsection(content, subsection_name):
    """Extract a subsection from content by its heading"""
    pattern = rf'^####\s+{subsection_name}\s*\n+(.*?)(?=^####|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return '' 