# Asistente de Ingeniería de Software

Herramienta que traduce especificaciones textuales en formato Markdown a diagramas visuales y código Python.

## Características

- Interpreta especificaciones de software en formato Markdown semi-estructurado
- Genera diagramas visuales (de clases, secuencia y arquitectura) usando Mermaid
- Produce código Python inicial (scaffolding) basado en la especificación

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/yourusername/AsistenteIngenieriaSoftware.git
cd AsistenteIngenieriaSoftware
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar las variables de entorno:
```bash
cp .env.example .env
```
Editar el archivo .env y añadir tu clave API para Gemini (o el LLM que uses).

## Uso

1. Iniciar la aplicación:
```bash
python app.py
```

2. Abrir http://localhost:5000 en tu navegador
3. Introducir tu especificación en formato Markdown siguiendo la estructura definida
4. Visualizar los diagramas generados
5. Generar el código Python cuando estés satisfecho con los diagramas

## Formato de Especificación

Consultar el archivo `product-definition.ml` para ver los detalles del formato de entrada esperado. 