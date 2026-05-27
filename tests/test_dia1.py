"""
tests/test_dia1.py

Pruebas rápidas del Día 1: verifica loaders sin necesitar API key.
Usa datos de ejemplo generados en el momento.

Ejecutar:
    python tests/test_dia1.py
"""
import tempfile
import os
from pathlib import Path


def test_excel_loader():
    """Crea un Excel de prueba y verifica que se cargue correctamente."""
    print("\n[TEST] Excel Loader...")
    import openpyxl

    # Crear Excel de prueba
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Diccionario_Clientes"
    ws.append(["Tabla", "Campo", "Tipo", "Descripcion"])
    ws.append(["CLIENTES", "id_cliente", "INT", "Identificador único del cliente"])
    ws.append(["CLIENTES", "nombre", "VARCHAR(100)", "Nombre completo del cliente"])
    ws.append(["CLIENTES", "email", "VARCHAR(200)", "Correo electrónico"])
    ws.append(["PEDIDOS", "id_pedido", "INT", "Identificador del pedido"])
    ws.append(["PEDIDOS", "id_cliente", "INT", "FK → CLIENTES.id_cliente"])
    wb.save(tmp_path)

    # Cargar
    from src.loaders.excel_loader import load_excel
    docs = load_excel(tmp_path)

    assert len(docs) == 5, f"Se esperaban 5 docs, se obtuvieron {len(docs)}"
    assert docs[0].metadata["sheet_name"] == "Diccionario_Clientes"
    assert docs[0].metadata["row_number"] == 2
    assert "id_cliente" in docs[0].page_content

    os.unlink(tmp_path)
    print(f"  ✅ Excel: {len(docs)} filas cargadas con metadata correcta")
    print(f"  Ejemplo: {docs[0].page_content[:80]}...")
    print(f"  Fuente:  {docs[0].metadata['source']} | Hoja: {docs[0].metadata['sheet_name']} | Fila: {docs[0].metadata['row_number']}")


def test_drawio_loader():
    """Crea un Draw.io de prueba y verifica que se parsee."""
    print("\n[TEST] Draw.io Loader...")

    drawio_content = """<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="API Gateway" style="rounded=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="3" value="Servicio de Autenticación" style="rounded=1;" vertex="1" parent="1">
      <mxGeometry x="300" y="100" width="160" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="4" value="Base de Datos" style="shape=cylinder;" vertex="1" parent="1">
      <mxGeometry x="300" y="240" width="160" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="5" value="autenticar" edge="1" source="2" target="3" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="6" value="consultar" edge="1" source="3" target="4" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>"""

    with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False, mode="w") as tmp:
        tmp.write(drawio_content)
        tmp_path = tmp.name

    from src.loaders.drawio_loader import load_drawio
    docs = load_drawio(tmp_path)

    assert len(docs) >= 4, f"Se esperaban al menos 4 docs, se obtuvieron {len(docs)}"
    types = {d.metadata["element_type"] for d in docs}
    assert "summary" in types
    assert "node" in types
    assert "edge" in types

    os.unlink(tmp_path)
    print(f"  ✅ Draw.io: {len(docs)} elementos cargados")
    for doc in docs[:3]:
        print(f"  [{doc.metadata['element_type']}] {doc.page_content[:70]}...")


def test_config():
    """Verifica que config.py carga sin errores."""
    print("\n[TEST] Configuración...")
    from src.config import config
    assert config.CHUNK_SIZE > 0
    assert config.CHUNK_OVERLAP >= 0
    print(f"  ✅ Config OK | CHUNK_SIZE={config.CHUNK_SIZE} | PROVIDER={config.LLM_PROVIDER}")


def test_chunking():
    """Verifica que el text splitter preserve metadata."""
    print("\n[TEST] Chunking...")
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    doc = Document(
        page_content="def suma(a, b):\n    return a + b\n\n" * 50,
        metadata={"source": "math.py", "type": "code", "start_line": 1},
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50, add_start_index=True)
    chunks = splitter.split_documents([doc])

    assert len(chunks) > 1, "El documento debería haber generado múltiples chunks"
    assert all("source" in c.metadata for c in chunks), "Metadata perdida en chunks"
    print(f"  ✅ Chunking: 1 doc → {len(chunks)} chunks, metadata preservada")


if __name__ == "__main__":
    print("=" * 50)
    print("  TESTS DÍA 1 — RAG Sistema Trazabilidad")
    print("=" * 50)

    test_config()
    test_excel_loader()
    test_drawio_loader()
    test_chunking()

    print("\n" + "=" * 50)
    print("  ✅ Todos los tests del Día 1 pasaron")
    print("=" * 50)
