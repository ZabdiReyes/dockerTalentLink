import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.utils.construir_json_para_mongo import construir_y_guardar_en_mongo
import os

modo = "frase"  # o "palabra"
dir_gpt = "Data/Json/GPT4omini"
dir_emb = f"Data/Json/Embeddings_{modo}"

for archivo in os.listdir(dir_gpt):
    if archivo.endswith(".json"):
        base = archivo.replace(".json", "")
        path_gpt = os.path.join(dir_gpt, archivo)

        sufijo = f"_colapsado_embeddings_{modo}.json"
        candidatos = [f for f in os.listdir(dir_emb) if f.startswith(base) and f.endswith(sufijo)]

        if candidatos:
            path_emb = os.path.join(dir_emb, candidatos[0])
            construir_y_guardar_en_mongo(path_gpt, path_emb)
        else:
            print(f"⚠️ No se encontró embedding para: {archivo}")
