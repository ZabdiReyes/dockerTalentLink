import os
import json
from datetime import datetime
from pymongo import MongoClient

def cargar_json(path):
    with open(path, "r", encoding="UTF-8") as f:
        return json.load(f)

def construir_y_guardar_en_mongo(gpt4o_path, embedding_path, mongo_uri="mongodb://mongo:27017", db_name="cv_db", cv_collection="cvs", emb_collection="cv_embeddings"):
    # Conectar a Mongo
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Cargar datos
    gpt4o = cargar_json(gpt4o_path)
    embedding = cargar_json(embedding_path)

    nombre = gpt4o.get("contact", {}).get("name", "desconocido")

    # Documento para colección de CVs
    doc_cv = {
        "name": nombre,
        "cv": gpt4o,
        "metadatos": {
            "fecha_creacion": datetime.now().isoformat(),
            "fuente_cv": gpt4o_path,
            "modelo_usado": "gpt-4o-mini"
        }
    }

    # Documento para colección de embeddings
    doc_embedding = {
        "name": nombre,
        "embedding": embedding
    }

    # Upsert en Mongo
    db[cv_collection].update_one({"name": nombre}, {"$set": doc_cv}, upsert=True)
    db[emb_collection].update_one({"name": nombre}, {"$set": doc_embedding}, upsert=True)

    print(f"✅ Insertado en Mongo: {nombre}")

    client.close()
