import os
import json
from datetime import datetime
from pymongo import MongoClient

def cargar_json(path):
    with open(path, "r", encoding="UTF-8") as f:
        return json.load(f)

def procesar_directorio_y_subir_a_mongo(
    carpeta_fuente_cv: str,          # ← GPT4omini o Custom
    carpeta_concatenado: str,        # ← JSON concatenado
    carpeta_embeddings: str,         # ← embeddings por palabra
    modo: str = "gpt4omini",             # o "custom"
    mongo_uri: str = "mongodb://mongo:27017",
    db_name: str = "cv_db",
    cv_collection: str = "cvs",
    emb_collection: str = "cv_embeddings"
):
    from pymongo import MongoClient
    from datetime import datetime
    import os, json

    def cargar_json(path):
        with open(path, "r", encoding="UTF-8") as f:
            data = json.load(f)
        # Deserializa si hay JSON embebido como string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                pass
        return data

    client = MongoClient(mongo_uri)
    db = client[db_name]

    archivos = [f for f in os.listdir(carpeta_fuente_cv) if f.endswith(".json")]
    if not archivos:
        print(f"⚠️ No se encontraron JSONs en: {carpeta_fuente_cv}")
        client.close()
        return

    for archivo in archivos:
        nombre_base = archivo.replace(".json", "")

        json_cv_path = os.path.join(carpeta_fuente_cv, archivo)
        json_concat_path = os.path.join(carpeta_concatenado, archivo)
        embedding_path = os.path.join(carpeta_embeddings, f"{nombre_base}_embeddings_palabra.json")

        if not os.path.exists(json_concat_path):
            print(f"⚠️ No se encontró el JSON concatenado: {json_concat_path}")
            continue

        if not os.path.exists(embedding_path):
            print(f"⚠️ Embedding no encontrado: {embedding_path}")
            continue

        try:
            # Cargar partes
            cv_data = cargar_json(json_cv_path)                # confiable
            cv_concat = cargar_json(json_concat_path)          # heurístico
            embedding_data = cargar_json(embedding_path)       # embedding

            # Extraer nombre desde el CV confiable
            contact = cv_data.get("contact")
            if not isinstance(contact, dict) or "name" not in contact:
                print(f"❌ No se pudo extraer el nombre desde: {json_cv_path}")
                continue

            nombre = contact["name"]

            doc_cv = {
                "name": nombre,
                "cv": cv_data,
                "cv_concatenado": cv_concat,
                "metadatos": {
                    "fecha_creacion": datetime.now().isoformat(),
                    "fuente_cv": json_cv_path,
                    "fuente_concatenado": json_concat_path,
                    "modelo_usado": "custom" if modo == "custom" else "gpt-4o-mini"
                }
            }

            doc_embedding = {
                "name": nombre,
                "embedding": embedding_data,
                "metadatos": {
                    "fecha_creacion": datetime.now().isoformat(),
                    "modelo_embedding": "miniLM",
                    "fuente_embedding": embedding_path
                }
            }

            db[cv_collection].update_one({"name": nombre}, {"$set": doc_cv}, upsert=True)
            db[emb_collection].update_one({"name": nombre}, {"$set": doc_embedding}, upsert=True)

            print(f"✅ Insertado en Mongo: {nombre} ({modo})")

        except Exception as e:
            print(f"❌ Error procesando {nombre_base}: {e}")

    client.close()