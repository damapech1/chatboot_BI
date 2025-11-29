import os

# ←←← AQUÍ PEGAS TU API KEY DE GROQ (así queda oculta del main)
GROQ_API_KEY = ""   # ¡Pégala aquí!

# Carpetas
DOCS_DIR = "documents"
DB_DIR = "chroma_db"
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Mensaje de bienvenida para el bot
WELCOME_MESSAGE = "¡Hola! Soy el asistente de Estancias y Reglamento Escolar. Sube los PDFs y pregúntame lo que necesites."