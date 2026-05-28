"""
run_groq_example.py

Indexa un conjunto pequeño de documentos de ejemplo usando embeddings ligeros
y realiza una consulta real contra Groq. Usa la clave en `.env`.
"""
from pathlib import Path
import tempfile
import traceback

from langchain_core.documents import Document

from src.rag import RAGEngine


class KeywordEmbeddings:
    """Embeddings muy simples para pruebas: vector binario por presencia de palabras."""
    def embed_documents(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)

    def _vector(self, text: str):
        lower = text.lower()
        return [
            float("cliente" in lower or "clientes" in lower),
            float("pedido" in lower or "pedidos" in lower),
            float("api" in lower or "gateway" in lower),
        ]


def main():
    docs = [
        Document(
            page_content="La tabla CLIENTES almacena el identificador y nombre del cliente.",
            metadata={"source": "diccionario.xlsx", "sheet_name": "Clientes", "row_number": 2, "type": "data_dictionary"},
        ),
        Document(
            page_content="La tabla PEDIDOS referencia CLIENTES mediante id_cliente.",
            metadata={"source": "diccionario.xlsx", "sheet_name": "Pedidos", "row_number": 5, "type": "data_dictionary"},
        ),
        Document(
            page_content="API Gateway autentica y redirige al servicio de pedidos.",
            metadata={"source": "arquitectura.drawio", "element_type": "node", "label": "API Gateway", "type": "architecture_diagram"},
        ),
    ]

    tmpdir = Path("./data/tmp_groq_test")
    try:
        with RAGEngine(persist_directory=str(tmpdir), embeddings=KeywordEmbeddings()) as engine:
            print(f"Indexando {len(docs)} documentos en {tmpdir}...")
            engine.index_documents(docs)

            question = "¿Cómo se relacionan clientes y pedidos?"
            print(f"Consultando Groq: '{question}'")
            result = engine.answer_question(question, top_k=3)

            print("\n--- RESPUESTA ---\n")
            print(result.get("answer"))
            print("\n--- FUENTES ---\n")
            for s in result.get("sources", []):
                print(f"- {s['citation']}")

    except Exception as exc:
        print("Error durante la prueba Groq:")
        # Si es un HTTPError de requests, mostramos el cuerpo de la respuesta si está disponible
        try:
            import requests

            if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
                print("HTTP error response body:")
                try:
                    print(exc.response.text)
                except Exception:
                    print(repr(exc.response))
            else:
                traceback.print_exc()
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    main()
