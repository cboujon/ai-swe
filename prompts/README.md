# Sistema de Prompts

Este directorio contiene los prompts utilizados por los diferentes módulos de la aplicación para interactuar con el modelo de IA Gemini. 

## Estructura de directorios

```
prompts/
├── markdown_parser/      # Prompts para parsear markdown
│   └── parse_markdown.txt
├── diagram_generator/    # Prompts para generar diagramas
│   ├── class_diagram.txt
│   ├── architecture_diagram.txt
│   └── sequence_diagram.txt
└── code_generator/       # Prompts para generar código
    └── generate_code.txt
```

## Formato de los prompts

Cada archivo de prompt es un archivo de texto que contiene plantillas con marcadores de posición que serán reemplazados con datos contextuales cuando se utilicen. Los marcadores de posición se indican utilizando la sintaxis de formato de Python: `{nombre_variable}`.

## Uso de los prompts

Los prompts se cargan utilizando el módulo `src/prompt_loader.py`, que proporciona funciones para cargar prompts desde los archivos correspondientes:

```python
from src.prompt_loader import load_prompt

# Cargar un prompt
prompt_template = load_prompt('categoria', 'nombre_prompt')

# Rellenar el template con datos
prompt = prompt_template.format(
    variable1=valor1,
    variable2=valor2
)
```

## Modificación de prompts

Para modificar el comportamiento de la IA, simplemente edite los archivos de texto en este directorio. Esto permite ajustar el comportamiento sin modificar el código de la aplicación.

### Ventajas

- **Separación de preocupaciones**: El código se centra en la lógica, mientras que los prompts se centran en la comunicación con la IA.
- **Fácil mantenimiento**: Los prompts pueden ser modificados sin cambiar el código.
- **Iteración rápida**: Permite experimentar con diferentes formulaciones de prompts sin recompilar o reiniciar la aplicación.
- **Versionado**: Los prompts pueden ser versionados junto con el código.

## Directrices para escribir prompts efectivos

1. **Sé específico**: Proporciona instrucciones claras y específicas sobre lo que se espera.
2. **Proporciona contexto**: Incluye toda la información relevante que la IA necesita para generar una respuesta útil.
3. **Estructura el prompt**: Usa títulos, enumeraciones y formato para hacer que el prompt sea fácil de seguir.
4. **Especifica el formato de salida**: Indica claramente el formato en el que deseas la respuesta. 