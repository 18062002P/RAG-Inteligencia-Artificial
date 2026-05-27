"""
src/loaders/drawio_loader.py

Parsea archivos Draw.io (.drawio o .xml) y extrae:
  - Nodos (shapes): id, label, estilo
  - Conexiones (edges): source → target con etiqueta
Retorna Documents con metadata de archivo y elemento para citación exacta.
"""
from pathlib import Path
from typing import List, Dict, Any
import base64
import zlib

from bs4 import BeautifulSoup
from langchain_core.documents import Document

from src.config import config


def _decode_drawio_xml(raw_xml: str) -> str:
    """
    Draw.io puede comprimir el contenido con deflate+base64.
    Esta función detecta y descomprime si es necesario.
    """
    soup = BeautifulSoup(raw_xml, "lxml-xml")
    diagram_tag = soup.find("diagram")

    if not diagram_tag:
        return raw_xml  # Ya está en XML plano

    content = diagram_tag.get_text(strip=True)

    if not content:
        return raw_xml

    # Si empieza con '<' ya es XML plano dentro del tag
    if content.strip().startswith("<"):
        return content

    # Intentar decodificar base64 + inflate (formato comprimido de Draw.io)
    try:
        decoded = base64.b64decode(content)
        decompressed = zlib.decompress(decoded, -15).decode("utf-8")
        return decompressed
    except Exception:
        return raw_xml


def _parse_drawio(xml_content: str) -> Dict[str, Any]:
    """Extrae nodos y edges del XML de Draw.io."""
    xml_content = _decode_drawio_xml(xml_content)
    soup = BeautifulSoup(xml_content, "lxml-xml")

    nodes = []
    edges = []

    for cell in soup.find_all("mxCell"):
        cell_id    = cell.get("id", "")
        label      = cell.get("value", "").strip()
        style      = cell.get("style", "")
        source     = cell.get("source", "")
        target     = cell.get("target", "")
        is_edge    = cell.get("edge") == "1"
        is_vertex  = cell.get("vertex") == "1"

        if is_edge:
            edges.append({
                "id": cell_id,
                "label": label,
                "source": source,
                "target": target,
            })
        elif is_vertex and label:
            nodes.append({
                "id": cell_id,
                "label": label,
                "style": style,
            })

    return {"nodes": nodes, "edges": edges}


def load_drawio(file_path: str) -> List[Document]:
    """
    Procesa un archivo Draw.io y retorna:
    - Un Document con el resumen completo del diagrama
    - Un Document por nodo importante
    - Un Document por conexión
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Draw.io no encontrado: {file_path}")

    raw_xml = file_path.read_text(encoding="utf-8", errors="ignore")
    parsed  = _parse_drawio(raw_xml)
    nodes   = parsed["nodes"]
    edges   = parsed["edges"]
    documents = []

    # ── Document 1: Resumen del diagrama ─────────────────────
    node_labels = [n["label"] for n in nodes if n["label"]]
    summary_text = (
        f"Diagrama de arquitectura: {file_path.stem}\n"
        f"Componentes ({len(nodes)}): {', '.join(node_labels)}\n"
        f"Conexiones ({len(edges)} relaciones entre componentes)."
    )
    documents.append(Document(
        page_content=summary_text,
        metadata={
            "source": file_path.name,
            "full_path": str(file_path),
            "type": "architecture_diagram",
            "element_type": "summary",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        },
    ))

    # ── Document por nodo ────────────────────────────────────
    for node in nodes:
        documents.append(Document(
            page_content=f"Componente en diagrama '{file_path.stem}': {node['label']}",
            metadata={
                "source": file_path.name,
                "full_path": str(file_path),
                "type": "architecture_diagram",
                "element_type": "node",
                "element_id": node["id"],
                "label": node["label"],
            },
        ))

    # ── Document por edge ────────────────────────────────────
    # Construir mapa id → label para referencias
    id_to_label = {n["id"]: n["label"] for n in nodes}

    for edge in edges:
        src_label = id_to_label.get(edge["source"], edge["source"])
        tgt_label = id_to_label.get(edge["target"], edge["target"])
        rel_label = edge["label"] or "→"
        text = (
            f"Relación en diagrama '{file_path.stem}': "
            f"{src_label} {rel_label} {tgt_label}"
        )
        documents.append(Document(
            page_content=text,
            metadata={
                "source": file_path.name,
                "full_path": str(file_path),
                "type": "architecture_diagram",
                "element_type": "edge",
                "source_node": src_label,
                "target_node": tgt_label,
                "relation": rel_label,
            },
        ))

    print(f"[Draw.io] {len(documents)} elementos cargados desde {file_path.name}")
    return documents


def load_drawio_folder(folder_path: str = None) -> List[Document]:
    """Carga todos los .drawio y .xml de una carpeta."""
    folder = Path(folder_path or config.DRAWIO_DIR)
    folder.mkdir(parents=True, exist_ok=True)

    all_docs = []
    for ext in ("*.drawio", "*.xml"):
        for f in folder.glob(ext):
            all_docs.extend(load_drawio(str(f)))

    if not all_docs:
        print(f"[Draw.io] No se encontraron diagramas en {folder}")
    return all_docs
