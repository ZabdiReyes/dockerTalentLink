import os
import json
from sentence_transformers import SentenceTransformer
from app.utils.text_utils import limpiar_texto

# Ruta del modelo
MODELO_PATH = "app/models/miniLM"
modelo = SentenceTransformer(MODELO_PATH)


def texto_a_embeddings(texto: str, modo: str = "palabra"):
    """
    Convierte texto a embeddings.
    - modo='palabra': genera un embedding por palabra (sin stopwords)
    - modo='frase': genera un solo embedding para todo el texto
    """
    if not texto:
        return [] if modo == "palabra" else None

    if modo == "palabra":
        texto_limpio = limpiar_texto(texto)
        palabras = texto_limpio.strip().split()
        return modelo.encode(palabras, convert_to_numpy=True).tolist()
    elif modo == "frase":
        return modelo.encode(texto, convert_to_numpy=True).tolist()
    else:
        raise ValueError("Modo inválido. Usa 'palabra' o 'frase'.")


def json_a_embeddings(data: dict, modo: str = "palabra") -> dict:
    """Convierte los campos de un JSON a embeddings según el modo elegido."""
    return {
        campo: texto_a_embeddings(texto, modo)
        for campo, texto in data.items()
    }

def procesar_archivo_json(input_path: str, output_path: str, modo: str = "palabra"):
    """Procesa un JSON, genera embeddings y guarda el resultado."""
    with open(input_path, "r", encoding="UTF-8") as f:
        data = json.load(f)

    embeddings = json_a_embeddings(data, modo)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="UTF-8") as f:
        json.dump(embeddings, f, ensure_ascii=False, indent=2)

    print(f"✅ Embeddings ({modo}) guardados en: {output_path}")

def procesar_directorio_jsons(input_dir: str, output_dir: str, modo: str = "palabra"):
    """Procesa todos los JSON en un directorio y guarda sus embeddings."""
    archivos = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    if not archivos:
        print(f"⚠️ No se encontraron archivos .json en: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    for archivo in archivos:
        input_path = os.path.join(input_dir, archivo)
        output_name = archivo.replace(".json", f"_embeddings_{modo}.json")
        output_path = os.path.join(output_dir, output_name)
        procesar_archivo_json(input_path, output_path, modo)

'''
# Embeddings por palabra
procesar_directorio_jsons("Data/Json/Limpios", "Data/Json/Embeddings_palabra", modo="palabra")

# Embeddings por frase
procesar_directorio_jsons("Data/Json/Limpios", "Data/Json/Embeddings_frase", modo="frase")

'''