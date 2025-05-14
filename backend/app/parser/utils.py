
import re
import os
import json

def sanitize_filename(name):
    prohibited_chars = r'[\\/*?:"<>|]'
    cleaned = re.sub(prohibited_chars, '', name).strip()
    return re.sub(r'\s+', ' ', cleaned)

def save_json(name, data, output_dir="./Data/Json/Custom"):
    if not name:
        print("Error: Nombre inválido")
        return
    safe_name = sanitize_filename(name)
    if not safe_name:
        print("Error: Nombre no válido después de sanitizar")
        return
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{safe_name}.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
