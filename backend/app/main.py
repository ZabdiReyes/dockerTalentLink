# main.py  ────────────────
from fastapi import FastAPI, File, UploadFile
from typing import List
import os
from app import *
from pathlib import Path
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
# ───────────────────────────────────────────────────────────────────────────

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
        
        # ────────────────────────────
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
        )


        '''# ────────────────────────────
        # PASO 3b: Convertir TXT → JSON con GPT-4o-mini
        # ────────────────────────────
        txt_ok, txt_err = convert_txts_with_gpt4omini(
            input_dir=TXT_PROCESADO_FOLDER,
            output_dir=JSON_GPT4OMINI_FOLDER,
        )
        procesados.extend(txt_ok)
        errores.extend(txt_err)'''


        # ────────────────────────────
        # PASO 4: Convertir JSON → JSON (Concatenado para cada etiqueta)
        # ────────────────────────────
        colapsar_json_y_normalizar(
            #input_folder=JSON_GPT4OMINI_FOLDER, # Usar JSON_GPT4OMINI_FOLDER si se quiere usar GPT-4o-mini
            input_folder=JSON_CUSTOM_FOLDER,     # Usar JSON_CUSTOM_FOLDER si se quiere usar reglas propias propia
            output_folder=JSON_CONCATENADO_FOLDER,
            log=True
        )

        # ────────────────────────────
        # PASO 5: Convertir JSON (concatenado) → JSON (embeddings)
        # ────────────────────────────
        






    except Exception as e:
        errores.append({"error": str(e)})
        print(f"Error: {e}")

    return {"procesados": procesados, "errores": errores}


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
