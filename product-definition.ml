---
project: AsistenteIngenieriaSoftware
version: 1.0.0
description: Herramienta que traduce especificaciones textuales a diagramas visuales y código.
---

# Especificación del Producto: Asistente de Ingeniería de Software Basado en Especificación Textual

## 1. Visión General

El producto es una herramienta de software diseñada para asistir a ingenieros en las fases iniciales del desarrollo, automatizando la traducción de una especificación de requisitos y diseño en **lenguaje natural (semi-estructurado)** a artefactos técnicos como **diagramas de diseño visuales** y código fuente básico (scaffolding). El objetivo principal es acelerar la transición desde la conceptualización a la implementación, permitiendo al ingeniero visualizar y generar código directamente desde su descripción textual.

## 2. Usuario Objetivo

Ingenieros de Software que necesitan una forma rápida y eficiente de generar modelos de diseño (visuales) y estructura de código a partir de descripciones textuales detalladas.

## 3. Idea Central y Flujo (MVP - Producto Mínimo Viable)

La herramienta toma como entrada una **especificación detallada y semi-estructurada escrita en formato Markdown**. Un módulo de procesamiento (basado en un Large Language Model - LLM) interpreta esta especificación para identificar los elementos clave del diseño. A partir de esta interpretación, la herramienta genera:

*   **Diagramas de diseño visuales** (que el usuario puede ver y comprender gráficamente en una interfaz).
*   **Código fuente** en un lenguaje de programación objetivo (Python para el MVP).

El flujo de trabajo previsto para el MVP es:

1.  El ingeniero escribe la especificación en el formato Markdown definido.
2.  Internamente, se realiza una API Call un LLM (Comoo Gemini) que, basandose en la especificación, genera el código Mermeraid.
3.  Con la respuesta del paso anterior, el producto **renderiza** este texto para mostrar el **diagrama visual** al usuario en su interfaz utilizando la librería "https://cdn.jsdelivr.net/npm/mermaid@11.6.0/+esm"
4.  El ingeniero revisa estos diagramas visuales. Si es necesario realizar ajustes finos, el ingeniero puede tener la opción de **editar la representación textual subyacente** del diagrama (el código Mermaid) a través de una vista de código dentro de la herramienta. La herramienta volverá a renderizar el diagrama visual basado en la edición textual.
5.  Cuando el ingeniero lo solicita ("on-demand"), la herramienta genera el código fuente, tomando como base la especificación original y la versión actual de los diagramas (ya sean los generados automáticamente o los modificados a través de su representación textual).

*(Nota: Como modelo de lenguaje, mi capacidad se limita a generar las *representaciones textuales* de los diagramas - el código Mermaid - y ayudar a definir el formato y la lógica. La herramienta completa conceptualizada incluiría la interfaz gráfica para mostrar los diagramas visuales y el módulo de renderizado).*

## 4. Alcance del MVP

*   **Entrada:** Especificación en formato Markdown semi-estructurado (ver sección 5 para detalles).
*   **Artefactos Generados:**
    *   **Diagrama de Clases (Visual)**, generado a partir de su representación textual (Mermaid).
    *   **Diagrama de Secuencia (Visual)**, generado a partir de su representación textual (Mermaid).
    *   **Diagrama de Arquitectura Simple (Visual)** (ej: basado en componentes o flujo simple), generado a partir de su representación textual (Mermaid).
    *   Código Python: Scaffolding básico del proyecto, definiciones de clases con atributos y métodos (esqueletos), e intento de generar lógica básica inferida de los casos de uso y secuencias descritas.
*   **Funcionalidad Clave:** Traducción unidireccional Spec (Markdown) -> Diagramas (Visuales, generados via Texto Interno) -> Código (Python, on-demand). Posibilidad de ajustar diagramas editando su representación textual subyacente.
*   **Fuera del Alcance del MVP:**
    *   Sincronización bidireccional compleja (editar diagrama visual o código actualiza automáticamente la especificación en lenguaje natural).
    *   Edición directa de diagramas visuales mediante drag-and-drop o herramientas gráficas avanzadas (en lugar de editar el texto subyacente).
    *   Generación de documentación técnica completa más allá de la especificación inicial.
    *   Soporte para múltiples lenguajes de programación (más allá de Python).
    *   Generación de lógica de negocio compleja o algoritmos sofisticados.

## 5. Formato de Especificación de Entrada (Markdown Semi-estructurado)

Este formato busca equilibrar la legibilidad humana con la estructura necesaria para el procesamiento automatizado. Utiliza Markdown estándar con convenciones y secciones definidas:

*   **Base:** Archivo de texto plano formateado con sintaxis Markdown.
*   **Metadata Inicial:** Uso opcional de YAML Front Matter (`---` al inicio y final) para metadatos clave del proyecto (nombre, versión, descripción, lenguaje objetivo).
*   **Estructura de Secciones:** El documento se organiza con headers Markdown (`#` para el título principal, `##` para secciones mayores, `###` para subsecciones):
    *   `# Especificación del Software: [Nombre del Proyecto]`
    *   `## 1. Visión General` (Descripción general del sistema y objetivos)
    *   `## 2. Actores Principales` (Lista de actores con descripción, usando marcadores si son componentes/entidades)
    *   `## 3. Casos de Uso` (Detalle de funcionalidades clave)
        *   Subsecciones `### CU-XXX: Nombre del Caso de Uso`
        *   Campos estructurados: `Actor(es):`, `Descripción:`, `Precondiciones:` (opcional), `Flujo Principal:` (lista numerada), `Flujos Alternativos:` (opcional), `Postcondiciones:`.
        *   Importante: **Mencionar explícitamente *entidades* y **componentes** en las descripciones y flujos** para vincular casos de uso con el modelo y la arquitectura.
    *   `## 4. Modelo de Dominio (Entidades)` (Definición detallada de las estructuras de datos y su comportamiento)
        *   Subsecciones `### *NombreEntidad*` (El header usa el marcador de entidad)
        *   Campo `Descripción:` del propósito de la entidad.
        *   Lista `Atributos:`: Usar sintaxis `- [visibilidad] nombre: tipo`.
            *   Visibilidad: `+` (público), `-` (privado), `#` (protegido).
            *   Tipo: Tipos primitivos (`int`, `str`, `bool`, `float`, `datetime`, etc.), otras entidades (`*OtraEntidad*`), colecciones (`list[*Tipo*]`, `dict[KeyType, ValueType]`).
        *   Lista `Métodos:`: Usar sintaxis `- [visibilidad] nombre(parametros...) -> tipo_retorno`.
            *   Parámetros: `nombre: tipo` (múltiples separados por coma). Opcional incluir nombres de parámetros en el MVP.
            *   Tipo de retorno: `-> tipo` (o `-> void` si no retorna).
        *   Lista `Relaciones:` (opcional pero recomendado): Definir explícitamente relaciones.
            *   Tipos: `ASOCIACION CON`, `AGREGACION DE`, `COMPOSICION DE`, `HEREDA DE`, `USA`.
            *   Formato: `TIPO_RELACION *EntidadDestino* (Cardinalidad)` donde cardinalidad es opcional (ej: `(1..1)`, `(0..*)`, `(1..*)`). Ejemplo: `ASOCIACION CON *Pedido* (0..*)`.
    *   `## 5. Arquitectura del Sistema` (Descripción de los componentes de alto nivel y sus interacciones)
        *   Campo `Descripción:` de la arquitectura general.
        *   Lista `Componentes:`: Usar `**NombreComponente**` con descripción.
        *   Lista `Conexiones:`: Describir las interacciones entre componentes. Formato simple: `**Origen** -> **Destino** (Protocolo/Notas)`.
    *   `## 6. Detalles de Secuencia` (Opcional: Para especificar flujos de interacción complejos si el caso de uso no es suficiente)
        *   Subsecciones `### DS-XXX: Descripción`
        *   Lista `Participantes:`: Listar `*Entidades*`, `**Componentes**` y Actores involucrados.
        *   Lista `Mensajes:` (numerada): Describir los mensajes usando una sintaxis simple `Origen -> Destino: mensaje(parametros)`. Se puede indicar ASYNC si aplica.

*   **Marcadores de Elementos Clave:** El uso consistente de `*Entidad*` y `**Componente**` a lo largo del documento es crucial para que la herramienta los identifique y vincule en diagramas y código.

## 6. Generación de Artefactos a partir del Formato

El módulo basado en LLM procesará este archivo Markdown, utilizando la estructura de secciones, headers, marcadores (`*`, `**`) y las convenciones sintácticas definidas (visibilidad, tipos, formato de relaciones y flujos) para extraer la información relevante del diseño.

*   Para los **diagramas**: Identificará las clases, atributos, métodos, relaciones, participantes y mensajes. Generará la correspondiente representación textual en PlantUML o Mermaid. La herramienta **renderizará** este texto para presentar los diagramas **visuales** al usuario.
*   Para el **código Python**: Utilizará la estructura de clases, atributos y métodos definidos en la sección "Modelo de Dominio", junto con la información de los casos de uso y secuencias, para generar el scaffolding del proyecto, las definiciones de clases con sus miembros (esqueletos) y un intento de añadir lógica básica inferida directamente de las descripciones o flujos simples. La información de las relaciones puede usarse para generar atributos de relación o métodos de acceso.

---