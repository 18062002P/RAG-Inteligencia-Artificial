"""
Minimal script to test Chroma on-disk cleanup: index small docs, close engine, and delete directory.
"""
import shutil
from pathlib import Path
from src.rag import RAGEngine
from langchain_core.documents import Document


def run_test():
    docs = [
        Document(page_content="A prueba uno", metadata={"source": "a.txt"}),
        Document(page_content="B prueba dos", metadata={"source": "b.txt"}),
    ]
    tmpdir = Path("./data/tmp_chroma_cleanup")
    if tmpdir.exists():
        shutil.rmtree(tmpdir, ignore_errors=True)

    try:
        with RAGEngine(persist_directory=str(tmpdir)) as engine:
            engine.index_documents(docs)
        print("Engine closed. Intentando borrar directorio...")
        # reintentos para evitar race conditions / locks en Windows
        import time

        success = False
        for attempt in range(1, 11):
            try:
                shutil.rmtree(tmpdir)
                success = True
                print(f"Directorio borrado correctamente (intento {attempt}).")
                break
            except Exception as e:
                print(f"Intento {attempt} fallido, esperando 0.2s: {e}")
                time.sleep(0.2)

        if not success:
            raise RuntimeError("No se pudo borrar el directorio tras varios intentos")
    except Exception as e:
        print("Error durante cleanup test:", e)


if __name__ == "__main__":
    run_test()
