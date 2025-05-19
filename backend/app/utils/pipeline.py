# utils/pipeline.py

import os
import re
import json
from typing import List, Dict, Tuple, Any
from fastapi import UploadFile

# ─── Proyecto: helpers específicos ─────────────────────────────────────────
# Ajusta estos imports al nombre real de tus módulos
from app.utils.procesamiento import process_txt, save_json,normalize_final_txt_headers,procesar_pdfs
from app.parser.gpt4omini import extract_info_from_txt
# ───────────────────────────────────────────────────────────────────────────

# ─── NUEVOS PARSERS DE POST‑PROCESADO ────────────────────────────────────────
# Cada módulo se encarga de una etiqueta de primera indentación:
#   • Education       → parser.educacion.process
#   • Certifications  → parser.certificaciones.procesar_certificaciones
#   • Languages       → parser.idiomas.parse_languages
from app.parser.educacion import process as parse_education
from app.parser.certificaciones import procesar_certificaciones as parse_certs
from app.parser.idiomas import parse_languages

# ──────────────────────────────────────────────────────────────────────────────
from app.utils.procesamiento import normalizar_texto




def clear_workdirs(folders: List[str], log: bool = True) -> None:
    """Vacía (y crea si no existen) las carpetas proporcionadas."""
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                os.unlink(fpath)
                if log:
                    print(f"🗑️  Archivo eliminado: {fpath}")


async def save_uploaded_pdfs(
    files: List[UploadFile],
    upload_folder: str,
    log: bool = True,
) -> List[str]:
    """Guarda los PDFs subidos y devuelve la lista de nombres."""
    pdf_names: List[str] = []
    for file in files:
        dst = os.path.join(upload_folder, file.filename)
        with open(dst, "wb") as buf:
            buf.write(await file.read())
        pdf_names.append(file.filename)
        if log:
            print(f"📁 PDF guardado en: {dst}")
    return pdf_names


def convert_pdfs_to_txt(
    pdf_names: List[str],
    directorio_origen: str,
    directorio_destino: str,
    txt_proc_folder: str,
    log: bool = True,
) -> None:
    """Ejecuta `procesar_pdfs` y normaliza encabezados en *_final.txt"""
    procesar_pdfs(
        pdf_names,
        directorio_origen=directorio_origen,
        directorio_destino=directorio_destino,
        procesar_todo=True,
        n=0,
        m=None,
        dividir=True,
        log=log,
    )

    for fname in os.listdir(txt_proc_folder):
        if fname.endswith("_final.txt"):
            full = os.path.join(txt_proc_folder, fname)
            normalize_final_txt_headers(full, log=log)


def convert_txts_to_json_custom(
    txt_proc_folder: str,
    json_custom_folder: str,
    log: bool = True,
) -> None:
    """Convierte cada *_final.txt a JSON usando heurísticas propias."""
    os.makedirs(json_custom_folder, exist_ok=True)

    for fname in os.listdir(txt_proc_folder):
        if not fname.endswith(".txt"):
            continue

        txt_path = os.path.join(txt_proc_folder, fname)
        base_name = os.path.splitext(fname)[0]

        name, json_data = process_txt(txt_path, log=log)
        final_name = (name or base_name).replace("_final", "").strip()
        json_data["Name"] = final_name
        save_json(final_name, json_data, output_dir=json_custom_folder)

        if log:
            print(f"📝 JSON generado: {final_name}.json")


def convert_txts_with_gpt4omini(
    input_dir: str,
    output_dir: str,
    log: bool = True,
) -> Tuple[List[str], List[Dict[str, str]]]:
    """Convierte .txt a JSON usando GPT‑4o‑mini, ignorando los que terminan en número."""
    processed: List[str] = []
    errors: List[Dict[str, str]] = []

    os.makedirs(output_dir, exist_ok=True)

    txt_files = [
        f for f in os.listdir(input_dir)
        if f.endswith(".txt") and not re.search(r"\d+(?=\.txt$)", f)
    ]

    for fname in txt_files:
        txt_path = os.path.join(input_dir, fname)
        if log:
            print(f"🧠 Procesando: {fname}")

        try:
            json_str = extract_info_from_txt(txt_path)
            json_data = json.loads(json_str)

            out_fname = os.path.splitext(fname)[0].lstrip() + ".json"
            out_path = os.path.join(output_dir, out_fname)

            with open(out_path, "w", encoding="UTF-8") as fout:
                json.dump(json_data, fout, indent=2, ensure_ascii=False)

            if log:
                print(f"✅ Guardado en: {out_path}")

            processed.append(fname)
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            errors.append({"archivo": fname, "error": msg})
            if log:
                print(f"❌ Error en {fname}: {msg}")

    return processed, errors

# ─── POST‑PROCESS JSON CUSTOM ────────────────────────────────────────────────

def postprocess_json_custom(
    json_custom_folder: str,
    log: bool = True,
) -> None:
    """Aplica parseos especializados a los archivos JSON de `json_custom_folder`.

    Etiquetas procesadas:
      ▸ Education       → parser.educacion.process
      ▸ Certifications  → parser.certificaciones.procesar_certificaciones
      ▸ Languages       → parser.idiomas.parse_languages
    """

    for fname in os.listdir(json_custom_folder):
        if not fname.endswith(".json"):
            continue

        fpath = os.path.join(json_custom_folder, fname)
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        if log:
            print(f"📂 Procesando archivo: {fname}")

        changed = False  # flag para saber si re‑escribir

        # ── Education ────────────────────────────────────────────────────
        if "Education" in data and isinstance(data["Education"], str):
            parsed = parse_education({"Education": data["Education"]})
            data["Education"] = parsed.get("Education", data["Education"])
            changed = True
            if log:
                print("✅ Education procesado")

        # ── Certifications ──────────────────────────────────────────────
        if "Certifications" in data and isinstance(data["Certifications"], list):
            cleaned = [line for line in data["Certifications"] if str(line).strip()]
            data["Certifications"] = parse_certs(cleaned)
            changed = True
            if log:
                print("✅ Certifications procesadas")

        # ── Languages ───────────────────────────────────────────────────
        if "Languages" in data and isinstance(data["Languages"], list):
            original = data["Languages"]
            parsed = parse_languages(original)
            data["Languages"] = parsed
            changed = True
            if log:
                print("🧠 Languages antes:", original)
                print("✅ Languages después:", parsed)

        if changed:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            if log:
                print(f"🔄 Post‑procesado: {fname}")
        elif log:
            print(f"⏭️  Sin cambios: {fname}")

# ─── Paso: Colapsar y normalizar JSON ─────────────────────────────────────
def colapsar_json_y_normalizar(
    input_folder: str,
    output_folder: str,
    log: bool = True,
) -> None:
    """
    Colapsa el contenido de los JSON en `input_folder` agrupado por etiquetas
    de primer nivel, normaliza el texto de cada etiqueta y guarda en `output_folder`.
    """
    os.makedirs(output_folder, exist_ok=True)

    def procesar_valor(valor: Any) -> str:
        if isinstance(valor, dict):
            return " ".join(str(v) for v in valor.values() if v)
        elif isinstance(valor, list):
            return " ".join(
                procesar_valor(item) if isinstance(item, (dict, list)) else str(item)
                for item in valor if item
            )
        else:
            return str(valor)

    for fname in os.listdir(input_folder):
        if not fname.endswith(".json"):
            continue

        ruta_json = os.path.join(input_folder, fname)
        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        resultado = {}
        for key, value in data.items():
            raw = procesar_valor(value)
            resultado[key] = normalizar_texto(raw)

        nombre_salida = fname.replace(".json", ".json")
        ruta_salida = os.path.join(output_folder, nombre_salida)

        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        if log:
            print(f"🧼 Colapsado y normalizado por etiquetas: {nombre_salida}")




