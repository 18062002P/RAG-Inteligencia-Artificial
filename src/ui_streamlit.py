"""
Interfaz rápida con Streamlit para consultar el RAG.

Uso:
    streamlit run src/ui_streamlit.py

Características:
- Input de pregunta
- Toggle `preview` para no llamar al LLM
- Selector `top_k` y botón enviar
- Muestra respuesta y fuentes (deduplicadas)
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so `from src...` imports work when
# running this file directly (e.g. `streamlit run src/ui_streamlit.py`).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from typing import List

from src.rag import RAGEngine
from src.config import config


def dedupe_sources(sources: List[dict]) -> List[dict]:
    seen = set()
    out = []
    for s in sources:
        key = (s.get("citation"), s.get("source"))
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def main():
    st.set_page_config(page_title="RAG Chat", layout="wide")
    st.title("RAG Chat — Día 2")

    with st.sidebar:
        st.header("Ajustes")
        top_k = st.slider("Top K retriever", 1, 10, 4)
        preview = st.checkbox("Preview (no llamar LLM)", value=False)
        st.markdown(f"**LLM provider:** {config.LLM_PROVIDER} — **modelo:** {config.LLM_MODEL}")
        st.markdown("---")
        st.markdown("Cambia `GROQ_API_KEY` en `.env` para permitir llamadas reales al modelo.")

    question = st.text_area("Pregunta", value="¿Cómo se relacionan clientes y pedidos?", height=120)
    col1, col2 = st.columns([1, 4])
    with col1:
        send = st.button("Enviar")

    if send and question.strip():
        with st.spinner("Recuperando contexto y consultando el modelo..."):
            try:
                with RAGEngine() as engine:
                    if preview:
                        result = engine.preview_question(question, top_k=top_k)
                        st.info("Preview: no se llamó al LLM")
                    else:
                        result = engine.answer_question(question, top_k=top_k)

                answer = result.get("answer") or "(sin respuesta)"
                st.subheader("Respuesta")
                st.write(answer)

                st.subheader("Fuentes")
                sources = dedupe_sources(result.get("sources", []))
                if sources:
                    for s in sources:
                        st.write(f"- {s.get('citation')}")
                else:
                    st.write("(sin fuentes recuperadas)")

                with st.expander("Contexto y mensajes (debug)"):
                    st.write(result.get("context", ""))
                    st.write(result.get("messages", []))

            except Exception as exc:
                st.error(f"Error: {exc}")


if __name__ == "__main__":
    main()
