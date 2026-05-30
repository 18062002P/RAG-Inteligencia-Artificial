# Casos de uso de prueba — Sistema RAG de trazabilidad de software

Este documento sirve como información adicional para que el RAG pueda responder durante la demostración.  
La demostración se limita a un lenguaje principal: **Python**, porque el repositorio del proyecto está desarrollado en Python.

## Objetivo del dataset

El dataset de prueba conecta tres fuentes:

1. Código fuente del repositorio Git.
2. Excel `datos_generales_rag.xlsx`, que contiene diccionario de datos, variables, funciones y casos de prueba.
3. Diagrama `arquitectura_rag.drawio`, que contiene componentes y relaciones del sistema.

## Caso 1: Trazabilidad de campo del diccionario hacia código

Pregunta sugerida:

> ¿En qué archivos de código se usa el campo `source` definido en el diccionario de datos?

Respuesta esperada:

El campo `source` se utiliza como metadato para identificar el origen de la información cargada.  
Debe aparecer en cargadores como `excel_loader.py`, `drawio_loader.py` y `git_loader.py`, y también en `rag.py`, donde se usa para construir citas de fuentes.

## Caso 2: Explicación de arquitectura usando Draw.io y código

Pregunta sugerida:

> Según el diagrama, ¿cómo fluye una pregunta desde la interfaz hasta la respuesta final?

Respuesta esperada:

La pregunta inicia en `Streamlit UI`, pasa al `Motor RAG`, el motor recupera contexto desde `ChromaDB`, arma un prompt con documentos citables y luego llama a `Groq LLM`.  
La respuesta final debe regresar con fuentes: archivo de origen, hoja/fila de Excel o elemento del diagrama.

## Caso 3: Análisis de impacto

Pregunta sugerida:

> ¿Qué impacto tendría cambiar `CHROMA_PERSIST_DIR` en el archivo de configuración?

Respuesta esperada:

Cambiar `CHROMA_PERSIST_DIR` modifica la carpeta donde se guarda la base vectorial.  
Si se cambia sin reindexar, el sistema podría no encontrar los documentos previamente cargados.  
Para corregirlo, se debe ejecutar nuevamente la ingesta con `python -m src.ingest --reset`.

## Nota para evitar alucinaciones

El asistente debe responder usando únicamente los documentos recuperados.  
Si no encuentra suficiente información, debe indicarlo claramente en lugar de inventar archivos o funciones.
