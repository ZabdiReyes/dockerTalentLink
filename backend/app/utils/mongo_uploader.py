import os
import json
from pymongo import MongoClient, UpdateOne

def cargar_jsons_en_mongo(directorio="Data/Json/Mongo_enviar", db_name="cv_db", collection_name="cvs"):
    client = MongoClient("mongodb://mongo:27017")
    db = client[db_name]
    coleccion = db[collection_name]

    operaciones = []
    for archivo in os.listdir(directorio):
        if archivo.endswith(".json"):
            ruta = os.path.join(directorio, archivo)
            with open(ruta, "r", encoding="UTF-8") as f:
                try:
                    doc = json.load(f)
                    name = doc.get("name")
                    if not name:
                        print(f"⚠️ Saltado {archivo}: no tiene campo 'name'")
                        continue

                    operaciones.append(
                        UpdateOne(
                            {"name": name},
                            {"$set": doc},
                            upsert=True
                        )
                    )
                except Exception as e:
                    print(f"❌ Error al procesar {archivo}: {e}")

    if operaciones:
        resultado = coleccion.bulk_write(operaciones)
        print(f"\n📥 {len(operaciones)} operaciones procesadas.")
        print(f"🆕 Insertados: {resultado.upserted_count}")
        print(f"🔁 Actualizados: {resultado.modified_count}")
    else:
        print("📂 No se encontraron archivos válidos para insertar.")

    client.close()
