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
    LLM_PROVIDER: str    = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str       = os.getenv("LLM_MODEL", "gpt-4o")
    OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ── Embeddings ───────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

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

    def validate(self):
        """Lanza error si falta alguna clave obligatoria."""
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("Falta OPENAI_API_KEY en el .env")
        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError("Falta ANTHROPIC_API_KEY en el .env")


config = Config()
