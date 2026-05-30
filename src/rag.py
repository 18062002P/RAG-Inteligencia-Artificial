"""
src/rag.py

Motor RAG del proyecto.
Recupera contexto desde ChromaDB y genera respuestas con Groq.
"""
import argparse
from pathlib import Path
from typing import Callable, Dict, List, Optional

import requests
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import config
from src.embeddings import build_embeddings


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _citation_for_document(document: Document) -> str:
    metadata = document.metadata or {}
    source = metadata.get("source", "desconocido")

    if metadata.get("sheet_name") and metadata.get("row_number"):
        return f"{source} | hoja={metadata['sheet_name']} | fila={metadata['row_number']}"

    if metadata.get("element_type"):
        detail = metadata.get("label") or metadata.get("element_id") or metadata.get("element_type")
        return f"{source} | elemento={metadata['element_type']} | detalle={detail}"

    if metadata.get("language"):
        return f"{source} | lenguaje={metadata['language']}"

    return source


def _context_block(documents: List[Document]) -> str:
    parts = []
    for index, document in enumerate(documents, start=1):
        citation = _citation_for_document(document)
        snippet = document.page_content.strip()
        parts.append(f"[{index}] {snippet}\nFuente: {citation}")
    return "\n\n".join(parts)


def _source_summary(documents: List[Document]) -> List[Dict[str, str]]:
    return [
        {
            "source": document.metadata.get("source", "desconocido"),
            "citation": _citation_for_document(document),
            "type": document.metadata.get("type", "desconocido"),
        }
        for document in documents
    ]


class RAGEngine:
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "rag_software",
        embeddings=None,
        responder: Optional[Callable[[List[Dict[str, str]]], str]] = None,
    ):
        self.persist_directory = persist_directory or config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self.embeddings = embeddings or build_embeddings()
        self.responder = responder
        self._vector_store: Optional[Chroma] = None

    @property
    def vector_store(self) -> Chroma:
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
        return self._vector_store

    def index_documents(self, documents: List[Document]) -> Chroma:
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        self._vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )
        return self._vector_store

    def close(self):
        """Persiste y cierra recursos asociados al vector store para evitar locks en Windows."""
        try:
            if self._vector_store is None:
                return

            try:
                # intenta persistir el store
                persist = getattr(self._vector_store, "persist", None)
                if callable(persist):
                    persist()
            except Exception:
                pass

            # intenta cerrar cliente subyacente si existe
            client = getattr(self._vector_store, "_client", None)
            if client is not None:
                close_fn = getattr(client, "close", None) or getattr(client, "shutdown", None)
                if callable(close_fn):
                    try:
                        close_fn()
                    except Exception:
                        pass

        finally:
            # libera la referencia para permitir GC y cierre de handles
            self._vector_store = None
            try:
                import gc, time

                for _ in range(8):
                    gc.collect()
                    time.sleep(0.05)
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def retrieve(self, question: str, top_k: int = 4) -> List[Document]:
        return self.vector_store.similarity_search(question, k=top_k)

    def build_messages(self, question: str, context: str) -> List[Dict[str, str]]:
        system_prompt = (
            "Eres un asistente RAG para trazabilidad de software. "
            "Responde en español, usa solo el contexto entregado y cita las fuentes. "
            "Si el contexto no alcanza, dilo con claridad."
        )
        user_prompt = (
            f"Contexto disponible:\n{context}\n\n"
            f"Pregunta:\n{question}\n\n"
            "Responde con una explicación breve y agrega las fuentes al final."
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _invoke_responder(self, messages: List[Dict[str, str]]) -> str:
        if self.responder is not None:
            return self.responder(messages)

        provider = config.LLM_PROVIDER.lower()
        if provider != "groq":
            raise NotImplementedError("Por ahora este motor está preparado para Groq.")

        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.LLM_MODEL,
            "messages": messages,
            "temperature": 0,
        }
        response = requests.post(GROQ_CHAT_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def answer_question(self, question: str, top_k: int = 4) -> Dict[str, object]:
        documents = self.retrieve(question, top_k=top_k)
        context = _context_block(documents)
        messages = self.build_messages(question, context)
        answer = self._invoke_responder(messages)

        return {
            "question": question,
            "answer": answer,
            "documents": documents,
            "sources": _source_summary(documents),
            "context": context,
            "messages": messages,
        }


def answer_question(question: str, top_k: int = 4) -> Dict[str, object]:
    engine = RAGEngine()
    return engine.answer_question(question, top_k=top_k)


def preview_question(question: str, top_k: int = 4) -> Dict[str, object]:
    engine = RAGEngine()
    documents = engine.retrieve(question, top_k=top_k)
    return {
        "question": question,
        "documents": documents,
        "sources": _source_summary(documents),
        "context": _context_block(documents),
        "messages": engine.build_messages(question, _context_block(documents)),
    }


def main():
    parser = argparse.ArgumentParser(description="Motor RAG con Groq y ChromaDB")
    parser.add_argument("question", nargs="?", help="Pregunta para consultar el RAG")
    parser.add_argument("--top-k", type=int, default=4, help="Cantidad de documentos a recuperar")
    parser.add_argument("--preview", action="store_true", help="Muestra solo contexto y fuentes sin llamar al LLM")
    args = parser.parse_args()

    if not args.question:
        parser.print_help()
        return

    result = preview_question(args.question, top_k=args.top_k) if args.preview else answer_question(args.question, top_k=args.top_k)

    print("\n=== RESPUESTA ===")
    print(result["answer"] if "answer" in result else "[preview] sin llamada al modelo")
    print("\n=== FUENTES ===")
    for source in result["sources"]:
        print(f"- {source['citation']}")


if __name__ == "__main__":
    main()