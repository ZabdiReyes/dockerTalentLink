# main.py  ────────────────
from fastapi import FastAPI, File, UploadFile
from typing import List
import os
from pymongo import MongoClient
from app import *
from pathlib import Path
import re
import numpy as np
from urllib.parse import unquote_plus

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
def buscar_cv(
    query: str = "",
    tags: str = "",
    top_k: int | None = None,
    min_score: float = 0.5          # ← umbral configurable
):
    query_libre = query.strip()

    # ── Parsear tags ───────────────────────────────────────
    etiquetas: list[tuple[str, str]] = []     # (etiqueta, valor)
    secciones_solo_emb: list[str] = []        # etiquetas sin valor

    if tags:
        for p in [s.strip() for s in tags.split(",") if s.strip()]:
            if ":" in p:
                etq, val = p.split(":", 1)
                etiquetas.append((etq.strip(), unquote_plus(val.strip())))
            else:
                secciones_solo_emb.append(p)

    # ── Filtrado directo (etiqueta + valor) ─────────────── etiqueta:valor
    filtro = {"$and": []}
    for etiqueta, valor in etiquetas:
        if etiqueta in ETIQUETAS_PRIMERA:
            campo = f"cv_concatenado.{etiqueta}"
        elif etiqueta in SECCIONES_VALIDAS:
            campo = f"cv.{etiqueta}"
        else:
            continue
        filtro["$and"].append({campo: {"$regex": valor, "$options": "i"}})

    docs_cv = list(
        db["cvs"].find(filtro if filtro["$and"] else {}, {"_id": 0})
    )
    if not docs_cv:
        return {"query": query, "resultados": [], "puntuaciones": []}

    # ── Ranking por embeddings (si hay query libre) ───────
    puntuaciones: list[float] = []

    if query_libre:
        query_vec = obtener_embedding_texto(query_libre, modelo)
        nombres   = [d["name"] for d in docs_cv]

        emb_docs = db["cv_embeddings"].find(
            {"name": {"$in": nombres}}, {"_id": 0}
        )

        resultados = []
        for emb in emb_docs:
            vectores = []
            if secciones_solo_emb:
                for sec in secciones_solo_emb:
                    vectores.extend(emb["embedding"].get(sec, []))
            else:
                for v in emb["embedding"].values():
                    vectores.extend(v)

            score = cosine_similarity_top_k(query_vec, vectores, k=1)
            if score >= min_score:
                resultados.append((emb["name"], score))

        # Ordenar por score descendente
        resultados.sort(key=lambda x: x[1], reverse=True)

        # Nombres y diccionario {nombre:score}
        nombres_validos = [n for n, _ in resultados]
        orden           = {n: s for n, s in resultados}

        # Mantén solo los CV que pasaron el umbral
        docs_cv = [d for d in docs_cv if d["name"] in nombres_validos]
        docs_cv.sort(key=lambda d: orden[d["name"]], reverse=True)
        puntuaciones = [orden[d["name"]] for d in docs_cv]

    # ── top_k (opcional) ──────────────────────────────────
    if top_k:
        docs_cv      = docs_cv[:top_k]
        puntuaciones = puntuaciones[:top_k]

    return {
        "query": query,
        "resultados": docs_cv,
        "puntuaciones": puntuaciones
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