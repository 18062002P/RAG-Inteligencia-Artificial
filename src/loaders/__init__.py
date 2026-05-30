try:
    from .git_loader import load_git
except ImportError as exc:
    _git_loader_import_error = exc

    def load_git(*args, **kwargs):
        raise ImportError(
            "GitPython is required to use load_git. Install the project dependencies first."
        ) from _git_loader_import_error

from .excel_loader import load_excel, load_excel_folder
from .drawio_loader import load_drawio, load_drawio_folder

__all__ = [
    "load_git",
    "load_excel", "load_excel_folder",
    "load_drawio", "load_drawio_folder",
]
