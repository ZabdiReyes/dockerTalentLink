import json
import sys

sys.path.append("/workspaces/dockerTalentLink/backend")

def imprimir_estructura(data, indent=0):
    espacio = '  ' * indent
    if isinstance(data, dict):
        for clave, valor in data.items():
            tipo = type(valor).__name__
            print(f"{espacio}{clave} ({tipo})")
            imprimir_estructura(valor, indent + 1)
    elif isinstance(data, list):
        print(f"{espacio}- lista [{len(data)} elementos]")
        if data:
            imprimir_estructura(data[0], indent + 1)
    else:
        pass  # No imprime contenido base

def test_estructura_esther_andres():
    ruta = "Data/Json/Mongo_enviar/Esther Andrés Pérez.json"
    with open(ruta, "r", encoding="UTF-8") as f:
        data = json.load(f)

    print("\n🧩 Estructura del JSON de Esther Andrés Pérez:")
    imprimir_estructura(data)

if __name__ == "__main__":
    test_estructura_esther_andres()
