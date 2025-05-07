#!/usr/bin/env python3
"""
Configuration settings for the Software Engineering Assistant.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-lite"  # Model to use for all generations

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Application Configuration
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'True').lower() == 'true' 