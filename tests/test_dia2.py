"""
tests/test_dia2.py

Prueba rápida del motor RAG sin llamar a la API externa.
Construye un índice temporal, recupera contexto y verifica citación.
"""
import tempfile
import os
import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class KeywordEmbeddings(Embeddings):
    def _vector(self, text: str):
        lower = text.lower()
        return [
            float("cliente" in lower or "clientes" in lower),
            float("pedido" in lower or "pedidos" in lower),
            float("api" in lower or "gateway" in lower),
        ]

    def embed_documents(self, texts):
        return [self._vector(text) for text in texts]

    def embed_query(self, text):
        return self._vector(text)


def test_rag_preview_and_citations():
    print("\n[TEST] RAG Día 2...")
    from src.rag import RAGEngine

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

    captured_messages = {}

    def fake_responder(messages):
        captured_messages["messages"] = messages
        return "respuesta simulada"

    # Evitamos crear un ChromaDB en disco para que la prueba sea local y rápida.
    class FakeVectorStore:
        def __init__(self, docs):
            self.docs = docs

        def similarity_search(self, query, k=4):
            q = query.lower()
            results = []
            if "cliente" in q or "clientes" in q:
                results.extend([self.docs[0], self.docs[1]])
            if "pedido" in q or "pedidos" in q:
                results.append(self.docs[1])
            if "api" in q:
                results.append(self.docs[2])
            # deduplicate while preserving order
            seen = set()
            out = []
            for d in results:
                fid = d.metadata.get("source", "") + d.page_content[:30]
                if fid not in seen:
                    seen.add(fid)
                    out.append(d)
            return out[:k]

    engine = RAGEngine(
        persist_directory=None,
        embeddings=KeywordEmbeddings(),
        responder=fake_responder,
    )
    # injectamos el vector store falso
    engine._vector_store = FakeVectorStore(docs)

    result = engine.answer_question("¿Cómo se relacionan clientes y pedidos?", top_k=2)

    assert result["answer"] == "respuesta simulada"
    assert len(result["documents"]) >= 1
    assert any("Clientes" in source["citation"] or "Pedidos" in source["citation"] for source in result["sources"])
    assert "Contexto disponible" in captured_messages["messages"][1]["content"]
    assert "CLIENTES" in captured_messages["messages"][1]["content"]

    print("  ✅ RAG preview, contexto y citación OK")


if __name__ == "__main__":
    test_rag_preview_and_citations()
    print("\n✅ Test Día 2 completado")