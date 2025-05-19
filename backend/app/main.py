# main.py  ────────────────
from fastapi import FastAPI, File, UploadFile
from typing import List
import os
from pymongo import MongoClient
from app import *
from pathlib import Path
import re
import numpy as np

# Helpers del pipeline
from app.utils.pipeline import (
    clear_workdirs,               # Paso 0
    save_uploaded_pdfs,           # Paso 1
    convert_pdfs_to_txt,          # Paso 2
    convert_txts_to_json_custom,  # Paso 3a
    postprocess_json_custom,      # Paso 3a
    convert_txts_with_gpt4omini,  # Paso 3b
    colapsar_json_y_normalizar   # Paso 4
    


)

from app.parser.jsonembeddings import procesar_directorio_jsons # Paso 5
from app.utils.construir_json_para_mongo import procesar_directorio_y_subir_a_mongo # Paso 6
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# ─── Carpetas base ─────────────────────────────────────────────────────────
APP_DIR   = Path(__file__).resolve().parent        #   …/backend/app
BASE_DIR  = APP_DIR.parent                         #   …/backend
DATA_DIR  = BASE_DIR / "Data"                      #   …/backend/Data

UPLOAD_FOLDER         = DATA_DIR / "Original"
TXT_RAW_FOLDER        = DATA_DIR / "TxT_Raw"
TXT_PROCESADO_FOLDER  = DATA_DIR / "TxT_Procesado"
JSON_CUSTOM_FOLDER    = DATA_DIR / "Json" / "Custom"
JSON_GPT4OMINI_FOLDER = DATA_DIR / "Json" / "GPT4omini"
JSON_CONCATENADO_FOLDER = DATA_DIR / "Json" / "Concatenado"
EMBEDDINGS_PALABRA_FOLDER = DATA_DIR / "Json" / "Embeddings_palabra"
EMBEDDINGS_FRASE_FOLDER   = DATA_DIR / "Json" / "Embeddings_frase"

modelo = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

client = MongoClient("mongodb://mongo:27017")
db = client["cv_db"]

ETIQUETAS_PRIMERA = {
    "profile", "title", "skills", "languages",
    "experience", "education", "achievements", "others"
}

SECCIONES_VALIDAS = {
    "contact.name", "contact.linkedin", "contact.website",
    "contact.location", "contact.company",
    "achievements.certifications", "achievements.awards_honors",
    "achievements.publications", "others.additional_information"
}

# ───────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para permitir todo durante pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-pdf/")
async def upload_pdf(files: List[UploadFile] = File(...)):
    procesados: List[str] = []
    errores:    List[dict] = []

    try:
        # ────────────────────────────
        # PASO 0: Limpiar/crear carpetas de trabajo
        # ────────────────────────────
        clear_workdirs([
            UPLOAD_FOLDER,
            TXT_RAW_FOLDER,
            TXT_PROCESADO_FOLDER,
            JSON_CUSTOM_FOLDER,
            #JSON_GPT4OMINI_FOLDER,
        ])

        # ────────────────────────────
        # PASO 1: Guardar los PDFs subidos
        # ────────────────────────────
        procesados = await save_uploaded_pdfs(files, UPLOAD_FOLDER)

        # ────────────────────────────
        # PASO 2: Convertir PDF → TXT
        # ────────────────────────────
        convert_pdfs_to_txt(
            pdf_names=procesados,
            directorio_origen=UPLOAD_FOLDER,
            directorio_destino=TXT_RAW_FOLDER,
            txt_proc_folder=TXT_PROCESADO_FOLDER,
        )
        
        '''# ────────────────────────────
        # PASO 3a: Convertir TXT → JSON (heurística propia)
        # ────────────────────────────
        convert_txts_to_json_custom(
            txt_proc_folder=TXT_PROCESADO_FOLDER,
            json_custom_folder=JSON_CUSTOM_FOLDER,
        )
        
        # ─────────────────────────────────────────────
        # PASO 3a  ─ POST-PROCESADO JSON Custom
        # Etiquetas tratadas:
        #   ▸ Education      ▸ Certifications      ▸ Languages
        # ─────────────────────────────────────────────
        postprocess_json_custom(
            json_custom_folder=JSON_CUSTOM_FOLDER,
            log=True
        )'''


        # ────────────────────────────
        # PASO 3b: Convertir TXT → JSON con GPT-4o-mini
        # ────────────────────────────
        txt_ok, txt_err = convert_txts_with_gpt4omini(
            input_dir=TXT_PROCESADO_FOLDER,
            output_dir=JSON_GPT4OMINI_FOLDER,
        )
        procesados.extend(txt_ok)
        errores.extend(txt_err)


        # ────────────────────────────
        # PASO 4: Convertir JSON → JSON (Concatenado para cada etiqueta)
        # ────────────────────────────
        colapsar_json_y_normalizar(
            input_folder=JSON_GPT4OMINI_FOLDER, # Usar JSON_GPT4OMINI_FOLDER si se quiere usar GPT-4o-mini
            #input_folder=JSON_CUSTOM_FOLDER,     # Usar JSON_CUSTOM_FOLDER si se quiere usar reglas propias propia
            output_folder=JSON_CONCATENADO_FOLDER,
            log=True
        )

        # ────────────────────────────
        # PASO 5: Convertir JSON (concatenado) → JSON (embeddings)
        # ────────────────────────────

        # Generar embeddings por palabra
        procesar_directorio_jsons(
            input_dir=JSON_CONCATENADO_FOLDER,
            output_dir=EMBEDDINGS_PALABRA_FOLDER,
            modo="palabra"
        )

        '''# Generar embeddings por frase
        procesar_directorio_jsons(
            input_dir=JSON_CONCATENADO_FOLDER,
            output_dir=EMBEDDINGS_FRASE_FOLDER,
            modo="frase"
        )'''

        # ────────────────────────────
        # PASO 6: Cargar JSONs procesados a MongoDB
        # ────────────────────────────

        procesar_directorio_y_subir_a_mongo(
            carpeta_fuente_cv="Data/Json/GPT4omini",
            #carpeta_fuente_cv="Data/Json/Custom", 
            carpeta_concatenado="Data/Json/Concatenado",
            carpeta_embeddings="Data/Json/Embeddings_palabra",
            modo="gpt4omini"
        )

    except Exception as e:
        errores.append({"error": str(e)})
        print(f"Error: {e}")

    return {"procesados": procesados, "errores": errores}


@app.get("/buscar/")
def buscar_cv(query: str = "", top_k: int = 5):
    if not query.strip():
        return {"error": "Debes proporcionar una consulta (query)."}

    query = query.strip()

    # 🧩 Extraer todas las etiquetas con valores
    etiquetas = re.findall(r'([a-zA-Z.]+):"([^"]+)"', query)
    query_libre = re.sub(r'[a-zA-Z.]+:"[^"]+"', '', query).strip()

    # 🧱 Construir filtro Mongo con $and
    filtro_mongo = {"$and": []}
    for etiqueta, valor in etiquetas:
        if etiqueta in ETIQUETAS_PRIMERA:
            campo = f"cv_concatenado.{etiqueta}"
            filtro_mongo["$and"].append({campo: {"$regex": valor, "$options": "i"}})
        elif etiqueta in SECCIONES_VALIDAS:
            campo = f"cv.{etiqueta}"
            filtro_mongo["$and"].append({campo: {"$regex": valor, "$options": "i"}})

    # Si no hubo etiquetas válidas, buscar todo
    if not filtro_mongo["$and"]:
        documentos_filtrados = list(db["cvs"].find({}))
    else:
        documentos_filtrados = list(db["cvs"].find(filtro_mongo))

    if not documentos_filtrados:
        return {"query": query, "resultados": [], "puntuaciones": []}

    # 🔍 Obtener nombres para buscar embeddings
    nombres_filtrados = [doc["name"] for doc in documentos_filtrados]
    embedding_docs = list(db["cv_embeddings"].find({ "name": { "$in": nombres_filtrados } }))

    # Si no hay query libre, solo devuelve los nombres filtrados
    if not query_libre:
        return {"query": query, "resultados": nombres_filtrados, "puntuaciones": []}

    # 🔄 Embedding de la query libre
    query_vector = obtener_embedding_texto(query_libre, modelo)

    resultados = []
    for doc in embedding_docs:
        vectores = []

        # Si hay etiquetas de 1ra categoría, usar solo esas secciones
        secciones_a_usar = [et[0] for et in etiquetas if et[0] in ETIQUETAS_PRIMERA]
        if secciones_a_usar:
            for seccion in secciones_a_usar:
                vectores.extend(doc["embedding"].get(seccion, []))
        else:
            # Si no se especificó sección, usar todas
            for v in doc["embedding"].values():
                vectores.extend(v)

        score = cosine_similarity_top_k(query_vector, vectores, k=3)
        resultados.append((doc["name"], score))

    resultados.sort(key=lambda x: x[1], reverse=True)

    cvs_completos = []
    for nombre, score in resultados[:top_k]:
        cv_doc = db["cvs"].find_one({"name": nombre})
        if cv_doc:
            cv_doc.pop("_id", None)
            cvs_completos.append(cv_doc)

    return {
        "query": query,
        "resultados": cvs_completos,
        "puntuaciones": [r[1] for r in resultados[:top_k]]
    }

def obtener_embedding_texto(texto: str, modelo) -> list:
    return modelo.encode(texto, convert_to_numpy=True).tolist()

def cosine_similarity_top_k(query_vec: list, vectors: list, k: int = 3) -> float:
    if not vectors:
        return 0.0
    query = np.array(query_vec)
    vectores = np.array(vectors)
    norm_query = np.linalg.norm(query)
    norm_vectors = np.linalg.norm(vectores, axis=1)
    sims = vectores @ query / (norm_vectors * norm_query + 1e-8)
    top_k_sims = sorted(sims, reverse=True)[:k]
    return float(np.mean(top_k_sims))