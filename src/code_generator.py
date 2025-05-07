#!/usr/bin/env python3
import logging
import os
import re
import json
from typing import Dict, Any, List

from src.ai_model import generate_content
from src.prompt_loader import load_prompt
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Check if Google Gemini API is available
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
use_gemini = False

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        use_gemini = True
        logger.info("Google Gemini API configured successfully for code generation")
    except ImportError:
        logger.warning("Google Generative AI package not installed. Using basic code generation.")
    except Exception as e:
        logger.warning(f"Failed to configure Gemini API: {e}")
else:
    logger.info("Gemini API key not found. Using basic code generation.")


def generate_code(spec: Dict[str, Any], diagrams: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate Python code scaffolding from the parsed specification and diagrams
    
    Args:
        spec (dict): Parsed specification structure
        diagrams (dict): Generated diagrams
        
    Returns:
        dict: Dictionary with filenames as keys and generated code as values
    """
    logger.info("Generating code from specification")
    
    if GEMINI_API_KEY:
        try:
            return generate_code_with_gemini(spec, diagrams)
        except Exception as e:
            logger.error(f"Error generating code with Gemini: {e}", exc_info=True)
            # Fall back to basic implementation if Gemini fails
    
    # Basic implementation without LLM
    code_files = {}
    
    # Generate code for each class
    for cls in spec.get('classes', []):
        class_name = cls.get('name', '')
        if not class_name:
            continue
            
        file_name = f"{class_name.lower()}.py"
        
        code = generate_class_code(cls)
        code_files[file_name] = code
    
    # Generate main application file
    main_py = generate_main_file(spec)
    code_files['main.py'] = main_py
    
    # Generate README
    readme = generate_readme(spec)
    code_files['README.md'] = readme
    
    # Generate requirements.txt
    requirements = generate_requirements(spec)
    code_files['requirements.txt'] = requirements
    
    return code_files


def generate_class_code(cls: Dict[str, Any]) -> str:
    """Generate Python code for a single class"""
    class_name = cls.get('name', '')
    attributes = cls.get('attributes', [])
    methods = cls.get('methods', [])
    
    code = [
        '#!/usr/bin/env python3',
        'from typing import List, Dict, Any, Optional',
        '',
        '',
        f'class {class_name}:',
        f'    """{class_name} class"""',
        '',
        '    def __init__(self'
    ]
    
    # Add constructor parameters
    init_params = []
    init_body = ['']
    
    for attr in attributes:
        attr_name = attr.get('name', '')
        attr_type = attr.get('type', 'str')
        default = attr.get('default', None)
        
        if default is not None:
            init_params.append(f"{attr_name}: {attr_type} = {default}")
        else:
            init_params.append(f"{attr_name}: {attr_type} = None")
        
        init_body.append(f"        self.{attr_name} = {attr_name}")
    
    code.append(', ' + ', '.join(init_params) + '):')
    code.extend(init_body)
    
    # Add methods
    for method in methods:
        method_name = method.get('name', '')
        params = method.get('parameters', [])
        return_type = method.get('return_type', 'None')
        comment = method.get('comment', '')
        
        # Add an empty line between methods
        code.append('')
        
        # Method parameters (always include self)
        method_params = ['self']
        for param in params:
            param_name = param.get('name', '')
            param_type = param.get('type', 'Any')
            method_params.append(f"{param_name}: {param_type}")
        
        # Method signature
        code.append(f'    def {method_name}({", ".join(method_params)}) -> {return_type}:')
        
        # Method docstring
        if comment:
            code.append(f'        """{comment}"""')
        else:
            code.append(f'        """{method_name} method"""')
        
        # Method body (placeholder)
        code.append('        # TODO: Implement this method')
        if return_type != 'None':
            code.append(f'        return None  # Change to return appropriate {return_type}')
    
    # Return the complete class code
    return '\n'.join(code)


def generate_main_file(spec: Dict[str, Any]) -> str:
    """Generate the main application file"""
    app_name = spec.get('title', 'MyApplication')
    classes = [cls.get('name', '') for cls in spec.get('classes', [])]
    
    code = [
        '#!/usr/bin/env python3',
        'import logging',
        'from typing import List, Dict, Any, Optional',
        ''
    ]
    
    # Import classes
    for class_name in classes:
        if class_name:
            code.append(f'from {class_name.lower()} import {class_name}')
    
    code.extend([
        '',
        '# Configure logging',
        'logging.basicConfig(',
        '    level=logging.INFO,',
        '    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"',
        ')',
        'logger = logging.getLogger(__name__)',
        '',
        '',
        'def main():',
        f'    """Main entry point for {app_name}"""',
        '    logger.info("Starting application")',
        '',
        '    # TODO: Add application initialization and startup code',
        '',
        '    logger.info("Application running")',
        '',
        '',
        'if __name__ == "__main__":',
        '    main()',
        ''
    ])
    
    return '\n'.join(code)


def generate_readme(spec: Dict[str, Any]) -> str:
    """Generate a README file for the project"""
    title = spec.get('title', 'My Application')
    description = spec.get('description', 'A Python application')
    
    readme = [
        f'# {title}',
        '',
        f'{description}',
        '',
        '## Installation',
        '',
        '```bash',
        'pip install -r requirements.txt',
        '```',
        '',
        '## Usage',
        '',
        '```bash',
        'python main.py',
        '```',
        '',
        '## Features',
        ''
    ]
    
    # Add classes as features
    for cls in spec.get('classes', []):
        class_name = cls.get('name', '')
        if class_name:
            readme.append(f'- {class_name}')
    
    # Add architecture components
    readme.extend([
        '',
        '## Architecture',
        ''
    ])
    
    for component in spec.get('architecture', {}).get('components', []):
        component_name = component.get('name', '')
        if component_name:
            readme.append(f'- {component_name}')
    
    return '\n'.join(readme)


def generate_requirements(spec: Dict[str, Any]) -> str:
    """Generate a requirements.txt file"""
    # Basic requirements
    requirements = [
        'python-dotenv>=0.19.0',
        'typing-extensions>=4.0.0'
    ]
    
    # Add other requirements based on the specification
    # Here we could analyze the spec to determine what packages are needed
    
    return '\n'.join(requirements)


def generate_code_with_gemini(spec: Dict[str, Any], diagrams: Dict[str, Any]) -> Dict[str, str]:
    """Generate code using the Gemini API"""
    logger.info("Generating code with Gemini API")
    
    # Cargar el prompt desde archivo
    prompt_template = load_prompt('code_generator', 'generate_code')
    if not prompt_template:
        logger.error("Failed to load code generator prompt")
        raise ValueError("Failed to load code generator prompt")
    
    # Rellenar el template con los datos
    prompt = prompt_template.format(
        spec=spec,
        diagrams=diagrams
    )
    
    # Call Gemini API using centralized model
    response = generate_content(prompt)
    
    if not response:
        logger.error("Failed to get a response from Gemini API")
        raise ValueError("No response from Gemini API")
    
    # Extract the JSON response
    response_text = response.text
    
    # Look for JSON content
    matches = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
    if matches:
        json_str = matches.group(1)
    else:
        # Try to find anything that looks like JSON
        matches = re.search(r'({.*})', response_text, re.DOTALL)
        if matches:
            json_str = matches.group(1)
        else:
            # Just use the whole response and hope for the best
            json_str = response_text
    
    try:
        code_files = json.loads(json_str)
        return code_files
    except json.JSONDecodeError:
        logger.error("Failed to parse Gemini API response as JSON", exc_info=True)
        raise ValueError("Gemini API response was not valid JSON")


if __name__ == "__main__":
    # For testing
    sample_spec = {
        "title": "Task Manager",
        "description": "A simple task management application",
        "classes": [
            {
                "name": "Task",
                "attributes": [
                    {"name": "id", "type": "int"},
                    {"name": "title", "type": "str"},
                    {"name": "description", "type": "str"},
                    {"name": "done", "type": "bool", "default": "False"}
                ],
                "methods": [
                    {
                        "name": "complete",
                        "parameters": [],
                        "return_type": "None",
                        "comment": "Mark the task as complete"
                    }
                ]
            }
        ]
    }
    
    sample_diagrams = {
        "class": "classDiagram\n    class Task {\n        +id: int\n        +title: str\n        +description: str\n        +done: bool\n        +complete(): None\n    }\n"
    }
    
    code = generate_code(sample_spec, sample_diagrams)
    for filename, content in code.items():
        print(f"=== {filename} ===")
        print(content)
        print("\n\n") 