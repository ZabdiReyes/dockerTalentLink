import json
import os

def colapsar_json_para_embeddings(ruta_json):
    """
    Aplana un JSON anidado en forma de texto sin aplicar limpieza.
    Devuelve un diccionario con los mismos campos y los textos concatenados.
    """
    with open(ruta_json, "r", encoding="UTF-8") as f:
        data = json.load(f)

    resultado = {}

    def procesar_valor(valor):
        if isinstance(valor, dict):
            return " ".join(str(v) for v in valor.values() if v)
        elif isinstance(valor, list):
            return " ".join(
                procesar_valor(item) if isinstance(item, (dict, list)) else str(item)
                for item in valor if item
            )
        else:
            return str(valor)

    for key, value in data.items():
        resultado[key] = procesar_valor(value)

    return resultado

def guardar_diccionario_como_json(diccionario, carpeta_salida, nombre_archivo="resultado.json"):
    """
    Guarda un diccionario como archivo JSON en una carpeta dada.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

    with open(ruta_completa, "w", encoding="UTF-8") as f:
        json.dump(diccionario, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON guardado en: {ruta_completa}")
