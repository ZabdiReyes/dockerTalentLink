import os
import sys

# Agregar la raíz del proyecto (/app) al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.parser.jsontxt import *

# Script principal
if __name__ == "__main__":
    input_dir = "Data/Json/GPT4omini"
    output_dir = "Data/Json/Concatenado"

    for archivo in os.listdir(input_dir):
        if archivo.endswith(".json"):
            ruta_entrada = os.path.join(input_dir, archivo)
            dic = colapsar_json_para_embeddings(ruta_entrada)

            nombre_salida = archivo.replace(".json", "_colapsado.json")
            guardar_diccionario_como_json(dic, output_dir, nombre_salida)
