# chatbot_logic.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils import GROQ_API_KEY, DOCS_DIR, DB_DIR
import os
import shutil

# Modelos (los mejores y gratuitos/rápidos 2025)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, groq_api_key=GROQ_API_KEY)

def get_vector_db():
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def agregar_pdf(file, etiqueta="Sin etiqueta"):
    path = os.path.join(DOCS_DIR, file.name)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    
    loader = PyPDFLoader(path)
    docs = loader.load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    
    for c in chunks:
        c.metadata["source"] = file.name
        c.metadata["etiqueta"] = etiqueta
    
    db = get_vector_db()
    db.add_documents(chunks)
    return f"✅ {file.name} agregado ({etiqueta})"

def eliminar_pdf(filename):
    os.remove(os.path.join(DOCS_DIR, filename))
    
    # Reconstruimos la base de datos sin ese archivo
    shutil.rmtree(DB_DIR)
    Chroma(persist_directory=DB_DIR, embedding_function=embeddings)  # recrea vacía
    
    for f in os.listdir(DOCS_DIR):
        if f.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_DIR, f))
            docs = loader.load()
            chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
            for c in chunks:
                c.metadata["source"] = f
            get_vector_db().add_documents(chunks)
    return f"🗑️ {filename} eliminado del conocimiento"

# This function handles querying the LLM with context from the PDFs
def query_llm(pregunta: str) -> str:
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 5})  # ← bajamos de 8 a 5
    docs = retriever.invoke(pregunta)
    
    # ←←← AQUÍ ESTÁ LA CLAVE: limitamos el contexto a ~2000 caracteres máximo
    contexto = ""
    for d in docs[:5]:  # máximo 5 chunks
        if len(contexto) + len(d.page_content) < 2800:  # límite seguro
            contexto += d.page_content + "\n\n"
        else:
            break
    
    fuentes = list(set([d.metadata.get("source", "Documento oficial") for d in docs[:5]]))

    es_ingles = any(word in pregunta.lower() for word in ["what","when","how","why","where","who","can","the","is","are"])

    system_prompt = """Eres el Asistente Virtual Oficial bilingüe del Departamento de Estancias Profesionales. 
Solo respondes sobre convocatoria, reglamento y trámites escolares. Sé amable, claro y profesional."""

    prompt = f"""{system_prompt}

Contexto (máximo relevante):
{contexto}

Pregunta: {pregunta}

Respuesta corta y precisa (en español o inglés según la pregunta):"""

    try:
        respuesta = llm.invoke(prompt, max_tokens=600, temperature=0.1).content
    except Exception as e:
        print("Error Groq:", e)
        respuesta = "Disculpa, ocurrió un problema al procesar los documentos. Intenta con una pregunta más específica."

    if fuentes:
        respuesta += f"\n\n**{'Source' if es_ingles else 'Fuente'}(s):** {', '.join(fuentes)}"

    return respuesta