"""
src/loaders/git_loader.py

Clona o usa un repositorio Git local, filtra archivos de código relevantes
y retorna LangChain Documents con metadata de archivo + número de línea.
"""
import os
from pathlib import Path
from typing import List

import git
from langchain_core.documents import Document

from src.config import config

# Extensiones de código que nos interesan
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cs", ".go", ".rb", ".php",
    ".cpp", ".c", ".h", ".sql", ".sh", ".yaml", ".yml",
    ".json", ".xml", ".md", ".txt", ".dockerfile",
}

# Carpetas que ignoramos siempre
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv",
    "venv", "env", "dist", "build", ".idea", ".vscode",
}


def clone_or_load_repo(repo_url_or_path: str, repo_name: str = None) -> str:
    """
    Si 'repo_url_or_path' es una URL remota, clona el repo.
    Si es un path local, lo usa directamente.
    Retorna el path local del repositorio.
    """
    base_dir = Path(config.GIT_REPOS_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Detectar si es URL remota
    is_remote = repo_url_or_path.startswith(("http://", "https://", "git@"))

    if is_remote:
        name = repo_name or repo_url_or_path.rstrip("/").split("/")[-1].replace(".git", "")
        local_path = base_dir / name

        if local_path.exists():
            print(f"[Git] Repo ya existe en {local_path}, haciendo pull...")
            repo = git.Repo(local_path)
            repo.remotes.origin.pull()
        else:
            print(f"[Git] Clonando {repo_url_or_path} → {local_path}")
            git.Repo.clone_from(repo_url_or_path, local_path)

        return str(local_path)
    else:
        # Path local
        if not Path(repo_url_or_path).exists():
            raise FileNotFoundError(f"Path no encontrado: {repo_url_or_path}")
        return repo_url_or_path


def load_repo_documents(repo_path: str) -> List[Document]:
    """
    Recorre el repositorio y genera un Document por archivo de código.
    Metadata incluye: source (path relativo), repo_path, language, start_line.
    """
    repo_path = Path(repo_path)
    documents = []

    for file_path in repo_path.rglob("*"):
        # Saltar directorios y carpetas ignoradas
        if file_path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue
        if file_path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        # Saltar archivos muy grandes (> 500 KB)
        if file_path.stat().st_size > 500_000:
            print(f"[Git] Saltando archivo grande: {file_path.name}")
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[Git] No se pudo leer {file_path}: {e}")
            continue

        relative_path = str(file_path.relative_to(repo_path))

        doc = Document(
            page_content=content,
            metadata={
                "source": relative_path,
                "repo_path": str(repo_path),
                "language": file_path.suffix.lstrip("."),
                "start_line": 1,
                "total_lines": content.count("\n") + 1,
                "type": "code",
            },
        )
        documents.append(doc)

    print(f"[Git] Cargados {len(documents)} archivos desde {repo_path.name}")
    return documents


def load_git(repo_url_or_path: str, repo_name: str = None) -> List[Document]:
    """Función principal: clona/carga y retorna Documents."""
    local_path = clone_or_load_repo(repo_url_or_path, repo_name)
    return load_repo_documents(local_path)
