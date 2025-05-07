#!/usr/bin/env python3
"""
Centralized module for managing AI model instances.
This ensures we use a single model instance across the application.
"""
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# Initialize model singleton
_model_instance = None

def initialize_model():
    """Initialize the Gemini model if API key is available."""
    global _model_instance
    
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not found. AI features will be unavailable.")
        return False
    
    try:
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create model instance
        _model_instance = genai.GenerativeModel(GEMINI_MODEL)
        
        logger.info(f"Successfully initialized Gemini model: {GEMINI_MODEL}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}", exc_info=True)
        return False

def get_model():
    """
    Get the Gemini model instance.
    
    Returns:
        The initialized model instance or None if initialization failed.
    """
    global _model_instance
    
    # Initialize if not already done
    if _model_instance is None:
        initialize_model()
    
    return _model_instance

def generate_content(prompt):
    """
    Generate content using the Gemini model.
    
    Args:
        prompt (str): The prompt to send to the model
        
    Returns:
        The model response or None if generation failed
    """
    model = get_model()
    
    if model is None:
        logger.warning("Cannot generate content: Model not initialized")
        return None
    
    try:
        response = model.generate_content(prompt)
        return response
    except Exception as e:
        logger.error(f"Error generating content: {e}", exc_info=True)
        return None

# Initialize the model when the module is imported
initialize_model() 