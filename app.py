#!/usr/bin/env python3
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Render the main application page."""
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

@app.post("/api/generate-diagrams")
async def api_generate_diagrams(request: Request):
    """API endpoint to generate diagrams from markdown specification."""
    try:
        body = await request.json()
        markdown_content = body.get('markdown', '')
        
        # Parse the markdown specification
        parsed_spec = parse_markdown_spec(markdown_content)
        logger.debug("Parsed specification: %s", parsed_spec)

        # Generate diagrams
        diagrams = generate_diagrams(parsed_spec)
        
        # Include the parsed specification in the response
        diagrams['parsed_spec'] = parsed_spec
        
        return diagrams
    except Exception as e:
        logger.error(f"Error generating diagrams: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate-sequence-diagram")
async def api_generate_sequence_diagram(request: Request):
    """API endpoint to generate a sequence diagram for a specific use case."""
    try:
        body = await request.json()
        use_case_id = body.get('use_case_id')
        use_case_data = body.get('use_case_data')
        markdown_content = body.get('markdown', '')
        
        logger.info(f"Generating sequence diagram for use case {use_case_id}")
        
        # Parse the markdown if not already done
        parsed_spec = body.get('parsed_spec') or parse_markdown_spec(markdown_content)
        
        # Generate sequence diagram
        mermaid_code = generate_sequence_diagram_for_use_case(use_case_id, use_case_data, parsed_spec)
        
        return {"mermaid": mermaid_code}
    except Exception as e:
        logger.error(f"Error generating sequence diagram: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate-code")
async def api_generate_code(request: Request):
    """API endpoint to generate Python code from parsed specification and diagrams."""
    try:
        body = await request.json()
        parsed_spec = body.get('parsed_spec', {})
        diagrams = body.get('diagrams', {})
        
        # If we have been given the diagrams object but not the parsed_spec,
        # extract it from the diagrams
        if not parsed_spec and 'parsed_spec' in diagrams:
            parsed_spec = diagrams.pop('parsed_spec')
        
        code = generate_code(parsed_spec, diagrams)
        return code
    except Exception as e:
        logger.error(f"Error generating code: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/config/status")
async def api_config_status():
    """API endpoint to check configuration status."""
    try:
        return {
            'gemini_api': bool(GEMINI_API_KEY),
            'model': 'gemini-2.0-flash-lite',
            'debug_mode': DEBUG_MODE,
            'log_level': LOG_LEVEL
        }
    except Exception as e:
        logger.error(f"Error checking configuration: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=port)