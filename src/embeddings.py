"""
src/embeddings.py

Construye el proveedor de embeddings según la configuración activa.
Se comparte entre la ingesta y la capa RAG para que ambos usen el mismo
espacio vectorial.
"""
from src.config import config


class _KeywordEmbeddings:
    """Fallback ligero para desarrollo: vectores binarios por palabras clave."""
    def __init__(self, keywords=None):
        self.keywords = keywords or ["cliente", "pedido", "api"]

    def _vector(self, text: str):
        lower = text.lower()
        return [float(k in lower) for k in self.keywords]

    def embed_documents(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)


def build_embeddings():
    """Devuelve una instancia de embeddings compatible con Chroma.

    Si `sentence-transformers` no está instalado y el proveedor es
    `huggingface`, devolvemos un fallback ligero para que la UI y el
    preview funcionen sin romperse.
    """
    provider = config.EMBEDDING_PROVIDER.lower()

    if provider in {"huggingface", "local"}:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        except Exception as exc:
            # Fallback suave para desarrollo y preview cuando falta sentence-transformers
            print("[Warning] HuggingFace embeddings no disponibles, usando fallback ligero:", exc)
            return _KeywordEmbeddings()

    if provider == "openai":
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                openai_api_key=config.OPENAI_API_KEY,
            )
        except Exception as exc:
            raise

    raise ValueError(f"EMBEDDING_PROVIDER no soportado: {config.EMBEDDING_PROVIDER}")