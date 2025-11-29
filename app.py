import streamlit as st
from chatbot_logic import agregar_pdf, eliminar_pdf, query_llm
from utils import DOCS_DIR
import os

# ───────────────────── CONFIGURACIÓN ─────────────────────
st.set_page_config(page_title="Asistente UPY - Vinculación", layout="centered")
st.title("Asistente Virtual • Universidad Politécnica de Yucatán")
st.markdown("**Departamento de Vinculación y Estancias Profesionales**")

# ───────────────────── GESTIÓN DE DOCUMENTOS ─────────────────────
st.markdown("### Documentos oficiales cargados (opcional)")

documentos = [f for f in os.listdir(DOCS_DIR) if f.endswith((".pdf", ".docx", ".doc"))]

if documentos:
    cols = st.columns(min(len(documentos), 5))
    for i, doc in enumerate(documentos):
        with cols[i % len(cols)]:
            st.markdown(f"**{doc}**")
            if st.button("Eliminar", key=f"del_{doc}"):
                # Borrar archivo físico
                os.remove(os.path.join(DOCS_DIR, doc))
                st.success(f"Eliminado {doc}")
                st.rerun()
else:
    st.info("No hay documentos cargados. Puedes usar el asistente igual para preguntas generales de la UPY.")

# Drag & drop (PDF y Word)
st.markdown("#### Subir documentos oficiales (PDF o Word)")
uploaded_files = st.file_uploader(
    "Arrastra PDFs o archivos Word aquí (opcional)",
    type=["pdf", "docx", "doc"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
    for file in uploaded_files:
        with st.chat_message("user"):
            st.markdown(f"Subiste: **{file.name}**")
        
        etiqueta = st.text_input(
            "Etiqueta (opcional)", 
            value=os.path.splitext(file.name)[0],
            key=f"tag_{file.name}"
        )
        
        if st.button("Agregar al sistema", key=f"add_{file.name}"):
            msg = agregar_pdf(file, etiqueta)
            st.success(msg)
            st.rerun()

# ───────────────────── CHAT (SIEMPRE ACTIVO) ─────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "¡Hola! / Hello!\n\n"
                   "Soy el asistente oficial de **Vinculación y Estancias Profesionales** de la **Universidad Politécnica de Yucatán**.\n\n"
                   "Puedes preguntarme:\n"
                   "• Información general de la UPY\n"
                   "• Trámites de titulación, servicio social, estancias\n"
                   "• Convocatorias, calendarios, requisitos\n"
                   "• O subir documentos oficiales para consultas específicas\n\n"
                   "¿En qué te ayudo hoy?"
    }]

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input del usuario
if pregunta := st.chat_input("Escribe tu duda en español o inglés..."):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..." if not documentos else "Consultando documentos..."):
            respuesta = query_llm(pregunta)  # ← ya detecta solo si hay documentos
        st.markdown(respuesta)

    st.session_state.messages.append({"role": "assistant", "content": respuesta})