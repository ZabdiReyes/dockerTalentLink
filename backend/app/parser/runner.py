
import os
import json
from parser import utils, idiomas, certificaciones, educacion, experiencia

def process_all(directory="./Data/Json/Custom"):
    for archivo in os.listdir(directory):
        if archivo.endswith(".json"):
            path = os.path.join(directory, archivo)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for module in [idiomas, certificaciones, educacion, experiencia]:
                data = module.process(data)

            utils.save_json(data.get("Name", archivo.replace(".json", "")), data, output_dir=directory)

if __name__ == "__main__":
    process_all()
