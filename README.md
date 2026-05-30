# Sistema RAG — Arquitecto de Software Senior Virtual
> Universidad Mariano Gálvez | Inteligencia Artificial | Noveno Ciclo

## Estructura del Proyecto

```
rag_project/
├── .env.example          ← Copia como .env y pon tus API keys
├── .gitignore
├── requirements.txt
├── data/
│   ├── git_repos/        ← Repositorios clonados automáticamente
│   ├── excel/            ← Diccionarios de datos (.xlsx)
│   ├── drawio/           ← Diagramas de arquitectura (.drawio, .xml)
│   └── docs/             ← Documentación (.md, .pdf)
├── src/
│   ├── __init__.py
│   ├── config.py         ← Configuración central (lee .env)
│   ├── embeddings.py     ← Fábrica de embeddings (HuggingFace / fallback)
│   ├── ingest.py         ← Script de ingesta (Día 1)
│   ├── rag.py            ← Motor RAG (Día 2) + RAGEngine
│   ├── run_groq_example.py ← Ejemplo que llama a Groq
│   ├── groq_list_models.py ← Helper para listar modelos Groq
│   ├── test_chroma_cleanup.py ← Prueba de cleanup de Chroma (Windows)
│   ├── ui_streamlit.py   ← Interfaz Streamlit (chat)
│   └── loaders/
│       ├── git_loader.py
│       ├── excel_loader.py
│       └── drawio_loader.py
└── tests/
    ├── test_dia1.py
    └── test_dia2.py
```

---

## Instalación (Día 1)

### 1. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tu editor favorito y agregar tu API key de Groq
# LLM_PROVIDER=groq
# GROQ_API_KEY=gsk-...
```

### 4. Verificar que todo funciona (sin API key necesaria)
```bash
python tests/test_dia1.py
```

---

## Ingesta de datos (Día 1)

### Cargar un repositorio Git remoto
```bash
python -m src.ingest --git https://github.com/usuario/repositorio
```

### Cargar todos los archivos locales
Coloca tus archivos en las carpetas correspondientes:
- `data/excel/` → archivos .xlsx (diccionarios de datos)
- `data/drawio/` → archivos .drawio o .xml (diagramas)
- `data/docs/` → archivos .md o .pdf (documentación)

Luego ejecuta:
```bash
python -m src.ingest
```

### Re-indexar desde cero
```bash
python -m src.ingest --reset
```

---

## Motor RAG (Día 2)

### Probar una consulta sin llamar al modelo
```bash
python -m src.rag "¿Cómo se relacionan clientes y pedidos?" --preview
```

### Consultar con Groq
```bash
python -m src.rag "¿Cómo se relacionan clientes y pedidos?"
```

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Orquestador RAG | LangChain 0.2 |
| LLM | Groq Llama 3.1 / OpenAI / Anthropic |
| Embeddings | sentence-transformers (local) |
| Vector Store | ChromaDB (local) |
| UI | Streamlit |
| Archivos | openpyxl, lxml, GitPython |

---

## Criterios de Evaluación cubiertos

| Criterio | Peso | Estado |
|---|---|---|
| Ingesta Multiformato (Git + Excel + Draw.io) | 20% | ✅ Día 1 |
| Integración Git (clonación + limpieza) | 15% | ✅ Día 1 |
| Arquitectura del sistema + chunking | 15% | ✅ Día 1 |
| Seguridad (.env) | 10% | ✅ Día 1 |
| Cadena RAG + citación | 10% | 🔄 Día 2 |
| 3 Casos de uso | 30% | 🔄 Día 3 |
| Bonus voz | +10% | 🔄 Día 3 |

---

## Penalizaciones a evitar
- ❌ **-10 pts**: No citar fuentes → el sistema SIEMPRE incluye `source`, `sheet_name`, `row_number` en metadata
- ❌ **-15 pts**: Alucinaciones → el prompt del RAG prioriza los documentos sobre conocimiento general

---

**Instrucciones Rápidas de Uso**

- **Archivo de configuración**: edita tu clave en [/.env](.env) o copia [/.env.example](.env.example) → [/.env](.env)
- **Script de ingesta**: revisa la orquestación en [src/ingest.py](src/ingest.py)
- **Motor RAG**: la lógica principal está en [src/rag.py](src/rag.py)
- **UI (Streamlit)**: interfaz de chat en [src/ui_streamlit.py](src/ui_streamlit.py)

**Ejemplos rápidos**

- Ejecutar la ingesta (usa `--reset` para borrar y reindexar):

```bash
python -m src.ingest
# o para reindexar desde cero
python -m src.ingest --reset
```

- Probar una consulta sin consumir la API (preview):

```bash
python -m src.rag "¿Cómo se relacionan clientes y pedidos?" --preview
```

- Hacer una consulta real (consume tu `GROQ_API_KEY`):

```bash
python -m src.rag "¿Cómo se relacionan clientes y pedidos?"
```

- Levantar la UI de chat con Streamlit:

```bash
streamlit run src/ui_streamlit.py
```

Nota importante: si `streamlit run` falla por dependencias (por ejemplo no encuentra `sentence-transformers`), asegúrate de ejecutar Streamlit con el intérprete del `venv`. Por ejemplo en Windows:

```powershell
# activa el venv primero
\.venv\Scripts\activate
streamlit run src/ui_streamlit.py

# o directamente usando el ejecutable del venv
.venv\Scripts\streamlit.exe run src/ui_streamlit.py
```

Si no quieres instalar `sentence-transformers` inmediatamente, la UI ahora usa un "fallback" ligero para embeddings que permite probar `preview` y funcionalidades básicas sin la dependencia pesada.

Al abrir Streamlit verás un panel lateral con `top_k` y `preview` (útil para probar sin consumir la API).

**Notas sobre ChromaDB y Locks en Windows**

En Windows puede ocurrir que el directorio persistente de Chroma quede bloqueado por el proceso (file handles abiertos), lo que impide borrarlo inmediatamente. Recomendaciones:

- Para pruebas unitarias usa un `FakeVectorStore` o la opción de `preview` para evitar crear DB en disco.
- Para pipelines que necesiten borrar el directorio, elimina la carpeta desde otro proceso (por ejemplo un script externo con retardo) o reinicia el proceso Python que creó la DB.
- El proyecto incluye un método `close()` y soporte de contexto en `RAGEngine` (`src/rag.py`) que intenta persistir y liberar recursos; sin embargo, en algunos casos es necesario un pequeño retraso y reintentos antes de borrar.

Si quieres, puedo añadir una utilería `safe_remove_dir.py` que ejecuta el borrado en un subproceso tras una espera configurable.

**Siguientes pasos recomendados**

- Si ya tienes datos: ejecutar `python -m src.ingest` y luego probar con `streamlit run src/ui_streamlit.py`.
- Si necesitas correr muchas pruebas que crean y borran DB: te recomiendo que agregue la utilería de borrado seguro y adapte los tests para usar `FakeVectorStore` donde sea práctico.

---

Si quieres que añada la utilería de borrado seguro o una versión alternativa de UI con Gradio, dime cuál prefieres y lo implemento.
