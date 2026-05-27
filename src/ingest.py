"""
src/ingest.py

Script de ingesta del Día 1.
Carga todos los artefactos (Git, Excel, Draw.io, docs),
los divide en chunks y los indexa en ChromaDB.

Uso:
    python -m src.ingest
    python -m src.ingest --git https://github.com/usuario/repo
    python -m src.ingest --reset   # borra y re-indexa todo
"""
import argparse
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from src.config import config
from src.loaders import (
    load_git,
    load_excel_folder,
    load_drawio_folder,
)


# ── Cargadores adicionales (Markdown / PDF) ─────────────────

def load_docs_folder() -> List[Document]:
    """Carga .md y .pdf de la carpeta de documentación."""
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    docs_path = Path(config.DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    documents = []

    # Markdown
    md_loader = DirectoryLoader(
        str(docs_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        silent_errors=True,
    )
    md_docs = md_loader.load()
    for doc in md_docs:
        doc.metadata["type"] = "documentation"
    documents.extend(md_docs)

    # PDFs
    try:
        from langchain_community.document_loaders import PyPDFDirectoryLoader
        pdf_loader = PyPDFDirectoryLoader(str(docs_path))
        pdf_docs = pdf_loader.load()
        for doc in pdf_docs:
            doc.metadata["type"] = "documentation"
        documents.extend(pdf_docs)
    except Exception as e:
        print(f"[Docs] No se cargaron PDFs: {e}")

    print(f"[Docs] {len(documents)} documentos cargados")
    return documents


# ── Chunking ────────────────────────────────────────────────

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Divide los documentos en chunks.
    Estrategia: RecursiveCharacterTextSplitter preserva contexto semántico.
    Los metadatos se heredan en cada chunk (crucial para la citación).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
        add_start_index=True,   # agrega 'start_index' a metadata
    )

    chunks = splitter.split_documents(documents)
    print(f"[Ingest] {len(documents)} docs → {len(chunks)} chunks")
    return chunks


# ── Indexación en ChromaDB ──────────────────────────────────

def build_vector_store(chunks: List[Document], reset: bool = False):
    """Crea o actualiza el vector store ChromaDB."""
    persist_dir = config.CHROMA_PERSIST_DIR
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        openai_api_key=config.OPENAI_API_KEY,
    )

    if reset:
        print("[Ingest] Reseteando vector store...")
        import shutil
        shutil.rmtree(persist_dir, ignore_errors=True)
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

    print(f"[Ingest] Indexando {len(chunks)} chunks en ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name="rag_software",
    )

    print(f"[Ingest] ✅ Vector store listo en {persist_dir}")
    return vector_store


# ── Main ────────────────────────────────────────────────────

def run_ingestion(git_url: str = None, reset: bool = False):
    """Orquesta toda la ingesta del Día 1."""
    config.validate()

    all_documents: List[Document] = []

    # 1. Código fuente Git
    if git_url:
        print(f"\n=== Cargando repositorio Git: {git_url} ===")
        all_documents.extend(load_git(git_url))
    else:
        # Cargar repos ya clonados en la carpeta
        repos_dir = Path(config.GIT_REPOS_DIR)
        if repos_dir.exists():
            for repo_dir in repos_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    print(f"\n=== Cargando repo local: {repo_dir.name} ===")
                    all_documents.extend(load_git(str(repo_dir)))

    # 2. Diccionarios de datos Excel
    print("\n=== Cargando archivos Excel ===")
    all_documents.extend(load_excel_folder())

    # 3. Diagramas Draw.io
    print("\n=== Cargando diagramas Draw.io ===")
    all_documents.extend(load_drawio_folder())

    # 4. Documentación Markdown / PDF
    print("\n=== Cargando documentación ===")
    all_documents.extend(load_docs_folder())

    print(f"\n[Ingest] Total documentos cargados: {len(all_documents)}")

    # 5. Chunking
    chunks = chunk_documents(all_documents)

    # 6. Indexar
    build_vector_store(chunks, reset=reset)

    print("\n✅ Ingesta completa. El RAG está listo para el Día 2.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingesta para el RAG")
    parser.add_argument("--git", help="URL del repositorio Git a clonar")
    parser.add_argument("--reset", action="store_true", help="Borra y re-indexa todo")
    args = parser.parse_args()

    run_ingestion(git_url=args.git, reset=args.reset)
