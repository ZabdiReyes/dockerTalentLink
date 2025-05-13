from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

from app.utils.procesamiento import *
from app.search.bm25 import BM25SearchEngine

# Crear instancia de la API
app = FastAPI()

# CORS middleware (útil en desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas internas
BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "Data", "Original")
TXT_RAW_FOLDER = os.path.join(BASE_DIR, "Data", "TxT_Raw")
JSON_GPT4OMINI_FOLDER = os.path.join(BASE_DIR, "Data", "Json", "GPT4omini")

# Asegurar existencia de carpetas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TXT_RAW_FOLDER, exist_ok=True)
os.makedirs(JSON_GPT4OMINI_FOLDER, exist_ok=True)

# Declarar motor de búsqueda (inicialmente None)
bm25_engine = None

@app.on_event("startup")
def inicializar_buscador():
    global bm25_engine
    print("🔎 Inicializando motor de búsqueda BM25...")
    bm25_engine = BM25SearchEngine(directory_path=JSON_GPT4OMINI_FOLDER, section_key="profile")
    try:
        bm25_engine.index()
        if not bm25_engine.bm25:
            print("⚠️ Corpus vacío o sin documentos válidos. Índice no construido.")
    except Exception as e:
        print(f"❌ Error al construir el índice BM25: {e}")
        bm25_engine = None


# Ruta para subir PDFs
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Procesar el archivo cargado
        lista_pdf_paths = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.pdf')]
        procesar_pdfs(
            lista_pdf_paths,
            directorio_origen=UPLOAD_FOLDER,
            directorio_Raw=TXT_RAW_FOLDER,
            procesar_todo=True,
            n=3,
            m=4,
            dividir=True,
            log=False
        )

        return {"exitoso": True, "mensaje": f"PDF guardado y procesado: {file.filename}"}

    except Exception as e:
        return {"exitoso": False, "error": str(e)}

# Ruta para buscar CVs
@app.get("/buscar/")
def buscar_cv(query: str = "", top_k: int = 5):
    if not query.strip():
        return {"error": "Debes proporcionar una consulta (query)."}

    if not bm25_engine or not bm25_engine.bm25:
        return {"error": "El índice de búsqueda no está disponible (posiblemente vacío)."}

    jsons, scores = bm25_engine.search(query.strip(), top_n=top_k)

    return {
        "query": query,
        "resultados": jsons,
        "puntuaciones": scores
    }
