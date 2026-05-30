"""
src/config.py
Lee el archivo .env y expone la configuración central del proyecto.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carga el .env desde la raíz del proyecto
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    # ── LLM ─────────────────────────────────────────────────
    LLM_PROVIDER: str    = os.getenv("LLM_PROVIDER", "groq")
    LLM_MODEL: str       = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ── Embeddings ───────────────────────────────────────────
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # ── Vector Store ────────────────────────────────────────
    VECTOR_STORE: str       = os.getenv("VECTOR_STORE", "chroma")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # ── Rutas ────────────────────────────────────────────────
    GIT_REPOS_DIR: str = os.getenv("GIT_REPOS_DIR", "./data/git_repos")
    EXCEL_DIR: str     = os.getenv("EXCEL_DIR", "./data/excel")
    DRAWIO_DIR: str    = os.getenv("DRAWIO_DIR", "./data/drawio")
    DOCS_DIR: str      = os.getenv("DOCS_DIR", "./data/docs")

    # ── Chunking ─────────────────────────────────────────────
    CHUNK_SIZE: int    = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))

    def validate_llm(self):
        """Lanza error si falta la clave del proveedor de LLM activo."""
        if self.LLM_PROVIDER == "groq" and not self.GROQ_API_KEY:
            raise ValueError("Falta GROQ_API_KEY en el .env")
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("Falta OPENAI_API_KEY en el .env")
        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError("Falta ANTHROPIC_API_KEY en el .env")

    def validate_ingestion(self):
        """Valida solo lo necesario para ingesta y chunking local."""
        if self.EMBEDDING_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("Falta OPENAI_API_KEY para embeddings de OpenAI")


config = Config()
