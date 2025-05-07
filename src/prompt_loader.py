#!/usr/bin/env python3
"""
Prompt Loader Module

Este módulo se encarga de cargar los archivos de prompts desde la estructura
de directorios y proporcionar una interfaz para acceder a ellos.
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Ruta base para los prompts
PROMPTS_DIR = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts'))

def load_prompt(category, prompt_name):
    """
    Carga un prompt desde su archivo correspondiente.
    
    Args:
        category (str): Categoría del prompt (markdown_parser, diagram_generator, etc.)
        prompt_name (str): Nombre del archivo de prompt sin extensión
        
    Returns:
        str: Contenido del archivo de prompt
    """
    prompt_path = PROMPTS_DIR / category / f"{prompt_name}.txt"
    
    try:
        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_path}")
            return None
            
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        logger.debug(f"Loaded prompt: {category}/{prompt_name}")
        return content
    except Exception as e:
        logger.error(f"Error loading prompt {category}/{prompt_name}: {e}")
        return None

def get_prompt_path(category, prompt_name):
    """
    Obtiene la ruta completa a un archivo de prompt.
    
    Args:
        category (str): Categoría del prompt
        prompt_name (str): Nombre del archivo de prompt sin extensión
        
    Returns:
        Path: Ruta al archivo de prompt
    """
    return PROMPTS_DIR / category / f"{prompt_name}.txt" 