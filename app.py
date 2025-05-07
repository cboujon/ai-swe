#!/usr/bin/env python3
import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory

from config import GEMINI_API_KEY, LOG_LEVEL, DEBUG_MODE
from src.ai_model import initialize_model
from src.markdown_parser import parse_markdown_spec
from src.diagram_generator import generate_diagrams, generate_sequence_diagram_for_use_case
from src.code_generator import generate_code

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize AI model
if GEMINI_API_KEY:
    initialize_model()
    logger.info("Gemini API initialized")
else:
    logger.warning("No Gemini API key found. Running in basic mode without AI features.")

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/api/generate-diagrams', methods=['POST'])
def api_generate_diagrams():
    """API endpoint to generate diagrams from markdown specification."""
    try:
        logger.info("Received request to generate diagrams")
        markdown_content = request.json.get('markdown', '')
        
        # Parse the markdown specification
        parsed_spec = parse_markdown_spec(markdown_content)
        logging.debug("Parsed specification: %s", parsed_spec)

        # Generate diagrams
        diagrams = generate_diagrams(parsed_spec)
        
        # Include the parsed specification in the response
        diagrams['parsed_spec'] = parsed_spec
        
        return jsonify(diagrams)
    except Exception as e:
        logger.error(f"Error generating diagrams: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/generate-sequence-diagram', methods=['POST'])
def api_generate_sequence_diagram():
    """API endpoint to generate a sequence diagram for a specific use case."""
    try:
        use_case_id = request.json.get('use_case_id')
        use_case_data = request.json.get('use_case_data')
        markdown_content = request.json.get('markdown', '')
        
        logger.info(f"Generating sequence diagram for use case {use_case_id}")
        
        # Parse the markdown if not already done
        parsed_spec = None
        if 'parsed_spec' in request.json:
            parsed_spec = request.json.get('parsed_spec')
        else:
            parsed_spec = parse_markdown_spec(markdown_content)
        
        # Generate sequence diagram
        mermaid_code = generate_sequence_diagram_for_use_case(use_case_id, use_case_data, parsed_spec)
        
        return jsonify({
            'mermaid': mermaid_code
        })
    except Exception as e:
        logger.error(f"Error generating sequence diagram: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/generate-code', methods=['POST'])
def api_generate_code():
    """API endpoint to generate Python code from parsed specification and diagrams."""
    try:
        parsed_spec = request.json.get('parsed_spec', {})
        diagrams = request.json.get('diagrams', {})
        
        # If we have been given the diagrams object but not the parsed_spec,
        # extract it from the diagrams
        if not parsed_spec and 'parsed_spec' in diagrams:
            parsed_spec = diagrams.pop('parsed_spec')
        
        code = generate_code(parsed_spec, diagrams)
        return jsonify(code)
    except Exception as e:
        logger.error(f"Error generating code: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/config/status', methods=['GET'])
def api_config_status():
    """API endpoint to check configuration status."""
    try:
        return jsonify({
            'gemini_api': bool(GEMINI_API_KEY),
            'model': 'gemini-2.0-flash-lite',
            'debug_mode': DEBUG_MODE,
            'log_level': LOG_LEVEL
        })
    except Exception as e:
        logger.error(f"Error checking configuration: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE) 