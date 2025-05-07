"""
Module for generating diagrams from the parsed markdown specification.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional

from src.ai_model import generate_content
from src.prompt_loader import load_prompt
from config import GEMINI_API_KEY

# Configure logging
logger = logging.getLogger(__name__)

def generate_diagrams(parsed_spec: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate various diagrams from the parsed specification
    
    Args:
        parsed_spec (dict): Parsed specification structure
        
    Returns:
        dict: Dictionary with diagram types and their Mermaid code
    """
    logger.info("Generating diagrams from specification")
    
    diagrams = {}
    
    # Generate class diagram
    diagrams['class'] = generate_class_diagram(parsed_spec)
    
    # Generate architecture diagram
    diagrams['architecture'] = generate_architecture_diagram(parsed_spec)
    
    # Generate use case diagrams (list of all use cases)
    diagrams['use_case'] = generate_use_case_diagram(parsed_spec)
    
    # Return all generated diagrams
    return diagrams

def generate_class_diagram(parsed_spec: Dict[str, Any]) -> str:
    """
    Generate a Mermaid class diagram from the domain model in the parsed specification.
    
    If Gemini API is configured, it will use the LLM to generate a more sophisticated diagram.
    Otherwise, it will generate a basic diagram based on the parsed entities.
    
    Args:
        parsed_spec: The parsed specification dictionary
        
    Returns:
        Mermaid code for the class diagram
    """
    if GEMINI_API_KEY:
        try:
            return generate_class_diagram_with_gemini(parsed_spec)
        except Exception as e:
            logger.error(f"Error generating class diagram with Gemini: {e}", exc_info=True)
            # Fall back to basic implementation if Gemini fails
    
    logger.info("Generating class diagram using basic implementation")
    
    mermaid_code = ["classDiagram"]
    
    # Process classes
    for cls in parsed_spec.get('classes', []):
        class_name = cls.get('name', '')
        
        # Add class definition
        mermaid_code.append(f"    class {class_name} {{")
        
        # Add attributes
        for attr in cls.get('attributes', []):
            attr_name = attr.get('name', '')
            attr_type = attr.get('type', '')
            mermaid_code.append(f"        +{attr_name}: {attr_type}")
        
        # Add methods
        for method in cls.get('methods', []):
            method_name = method.get('name', '')
            return_type = method.get('return_type', '')
            
            # Format parameters
            params = []
            for param in method.get('parameters', []):
                param_name = param.get('name', '')
                param_type = param.get('type', '')
                params.append(f"{param_name}: {param_type}")
            
            param_str = ", ".join(params)
            mermaid_code.append(f"        +{method_name}({param_str}): {return_type}")
        
        mermaid_code.append("    }")
    
    # Add relationships (if available in the spec)
    # This is a placeholder for relationships, which would need to be extracted from the spec
    
    # Return the complete diagram
    return "\n".join(mermaid_code)

def generate_architecture_diagram(parsed_spec: Dict[str, Any]) -> str:
    """
    Generate Mermaid architecture diagram code from the specification
    
    Args:
        parsed_spec (dict): Parsed specification structure
        
    Returns:
        str: Mermaid architecture diagram code
    """
    if GEMINI_API_KEY:
        try:
            return generate_architecture_diagram_with_gemini(parsed_spec)
        except Exception as e:
            logger.error(f"Error generating architecture diagram with Gemini: {e}", exc_info=True)
            # Fall back to basic implementation if Gemini fails
    
    logger.info("Generating architecture diagram using basic implementation")
    
    mermaid_code = ["flowchart TD"]
    
    # Process components
    for component in parsed_spec.get('architecture', {}).get('components', []):
        component_name = component.get('name', '')
        component_id = component_name.replace(' ', '_')
        
        # Add component definition
        mermaid_code.append(f"    {component_id}[\"{component_name}\"]")
    
    # Process connections
    for connection in parsed_spec.get('architecture', {}).get('connections', []):
        source = connection.get('source', '').replace(' ', '_')
        target = connection.get('target', '').replace(' ', '_')
        description = connection.get('description', '')
        
        # Add connection with description if available
        if description:
            mermaid_code.append(f"    {source} -->|{description}| {target}")
        else:
            mermaid_code.append(f"    {source} --> {target}")
    
    # Return the complete diagram
    return "\n".join(mermaid_code)

def generate_use_case_diagram(parsed_spec: Dict[str, Any]) -> str:
    """
    Generate Mermaid use case diagram code from the specification
    
    Args:
        parsed_spec (dict): Parsed specification structure
        
    Returns:
        str: Mermaid use case diagram code
    """
    logger.info("Generating use case diagram")
    
    mermaid_code = ["flowchart LR"]
    
    # Collect unique actors
    actors = set()
    for use_case in parsed_spec.get('use_cases', []):
        for actor in use_case.get('actors', []):
            actors.add(actor)
    
    # Add actors
    for i, actor in enumerate(actors):
        actor_id = f"actor{i+1}"
        mermaid_code.append(f"    {actor_id}((\"{actor}\"))")
    
    # Add use cases
    for i, use_case in enumerate(parsed_spec.get('use_cases', [])):
        use_case_id = use_case.get('id', f"UC{i+1}")
        use_case_name = use_case.get('name', '')
        mermaid_code.append(f"    {use_case_id}[\"{use_case_name}\"]")
        
        # Connect actors to use cases
        for actor in use_case.get('actors', []):
            # Find actor id
            actor_id = None
            for j, a in enumerate(actors):
                if a == actor:
                    actor_id = f"actor{j+1}"
                    break
            
            if actor_id:
                mermaid_code.append(f"    {actor_id} --- {use_case_id}")
    
    # Return the complete diagram
    return "\n".join(mermaid_code)

def generate_sequence_diagram_for_use_case(use_case_id: str, use_case_data: Dict[str, Any], 
                                          spec: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a sequence diagram for a specific use case
    
    Args:
        use_case_id (str): ID of the use case
        use_case_data (dict): Data for the specific use case
        spec (dict, optional): Complete parsed specification
        
    Returns:
        str: Mermaid sequence diagram code
    """
    logger.info(f"Generating sequence diagram for use case: {use_case_id}")
    
    if GEMINI_API_KEY and spec:
        try:
            return generate_sequence_diagram_with_gemini(use_case_id, use_case_data, spec)
        except Exception as e:
            logger.error(f"Error generating sequence diagram with Gemini: {e}", exc_info=True)
            # Fall back to basic implementation if Gemini fails
    
    # Basic sequence diagram generation
    mermaid_code = ["sequenceDiagram"]
    
    # Add title
    use_case_name = use_case_data.get('name', '')
    mermaid_code.append(f"    title {use_case_name}")
    
    # Add participants (actors)
    actors = use_case_data.get('actors', [])
    for actor in actors:
        mermaid_code.append(f"    participant {actor}")
    
    # Add system components/participants
    # Add components that might be involved (from architecture)
    if spec:
        components = spec.get('architecture', {}).get('components', [])
        for component in components:
            component_name = component.get('name', '')
            mermaid_code.append(f"    participant {component_name.replace(' ', '_')}")
    
    # Add flow as messages
    for step in use_case_data.get('flow', []):
        source = step.get('actor', '').replace(' ', '_')
        target = step.get('action', '').replace(' ', '_')
        message = step.get('message', '')
        
        if source and target:
            if message:
                mermaid_code.append(f"    {source}->>+{target}: {message}")
            else:
                mermaid_code.append(f"    {source}->>+{target}: step {step.get('step', '')}")
        
        # Add return messages where appropriate
        if target and source and step.get('step', 0) % 2 == 0:
            mermaid_code.append(f"    {target}-->>-{source}: response")
    
    # Return the complete diagram
    return "\n".join(mermaid_code)

# Gemini API-based diagram generation
def generate_class_diagram_with_gemini(parsed_spec: Dict[str, Any]) -> str:
    """Generate a class diagram using Gemini AI assistance"""
    logger.info("Generating class diagram with Gemini API")
    
    # Cargar el prompt desde archivo
    prompt_template = load_prompt('diagram_generator', 'class_diagram')
    if not prompt_template:
        logger.error("Failed to load class diagram prompt")
        return generate_class_diagram(parsed_spec)  # Fallback to basic implementation
    
    # Rellenar el template con los datos
    prompt = prompt_template.format(spec=parsed_spec)
    
    # Call Gemini API using centralized model
    response = generate_content(prompt)
    
    if response:
        # Process and clean the response
        mermaid_code = clean_mermaid_response(response.text, 'classDiagram')
        return mermaid_code
    else:
        # Fallback to basic implementation if API call fails
        return generate_class_diagram(parsed_spec)

def generate_architecture_diagram_with_gemini(parsed_spec: Dict[str, Any]) -> str:
    """Generate an architecture diagram using Gemini AI assistance"""
    logger.info("Generating architecture diagram with Gemini API")
    
    # Cargar el prompt desde archivo
    prompt_template = load_prompt('diagram_generator', 'architecture_diagram')
    if not prompt_template:
        logger.error("Failed to load architecture diagram prompt")
        return generate_architecture_diagram(parsed_spec)  # Fallback to basic implementation
    
    # Rellenar el template con los datos
    prompt = prompt_template.format(spec=parsed_spec)
    
    # Call Gemini API using centralized model
    response = generate_content(prompt)
    
    if response:
        # Process and clean the response
        mermaid_code = clean_mermaid_response(response.text, 'flowchart TD')
        return mermaid_code
    else:
        # Fallback if API call fails
        return generate_architecture_diagram(parsed_spec)

def generate_sequence_diagram_with_gemini(use_case_id: str, use_case_data: Dict[str, Any], 
                                         spec: Dict[str, Any]) -> str:
    """Generate a sequence diagram for a use case using Gemini AI assistance"""
    logger.info(f"Generating sequence diagram for use case {use_case_id} with Gemini API")
    
    # Cargar el prompt desde archivo
    prompt_template = load_prompt('diagram_generator', 'sequence_diagram')
    if not prompt_template:
        logger.error("Failed to load sequence diagram prompt")
        return "sequenceDiagram\n    title Failed to generate sequence diagram with AI"  # Basic fallback
    
    # Preparar los datos para el template
    use_case_name = use_case_data.get('name', '')
    use_case_description = use_case_data.get('description', '')
    actors = ', '.join(use_case_data.get('actors', []))
    flow = str(use_case_data.get('flow', []))
    classes = str(spec.get('classes', []))
    architecture_components = str(spec.get('architecture', {}).get('components', []))
    
    # Rellenar el template con los datos
    prompt = prompt_template.format(
        use_case_name=use_case_name,
        use_case_description=use_case_description,
        actors=actors,
        flow=flow,
        classes=classes,
        architecture_components=architecture_components
    )
    
    # Call Gemini API using centralized model
    response = generate_content(prompt)
    
    if response:
        # Process and clean the response
        mermaid_code = clean_mermaid_response(response.text, 'sequenceDiagram')
        return mermaid_code
    else:
        # Create a simple sequence diagram if API call fails
        return "sequenceDiagram\n    title Failed to generate sequence diagram with AI"

def clean_mermaid_response(response: str, diagram_type: str) -> str:
    """Clean and format the Mermaid code from the LLM response"""
    # Extract just the Mermaid code
    if "```mermaid" in response:
        # Extract code between Markdown code blocks
        start = response.find("```mermaid")
        end = response.find("```", start + 10)
        if end > start:
            response = response[start + 10:end].strip()
    
    # Ensure it starts with the correct diagram type
    if not response.startswith(diagram_type):
        response = f"{diagram_type}\n{response}"
    
    return response 