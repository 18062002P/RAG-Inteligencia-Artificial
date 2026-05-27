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
│   ├── config.py         ← Configuración central (lee .env)
│   ├── ingest.py         ← Script de ingesta (Día 1)
│   ├── rag.py            ← Motor RAG (Día 2)
│   ├── app.py            ← Interfaz Streamlit (Día 2)
│   └── loaders/
│       ├── git_loader.py
│       ├── excel_loader.py
│       └── drawio_loader.py
└── tests/
    └── test_dia1.py
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

# Editar con tu editor favorito y agregar tu API key
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
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

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Orquestador RAG | LangChain 0.2 |
| LLM | OpenAI GPT-4o / Anthropic Claude |
| Embeddings | text-embedding-3-small |
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
