import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.mongo_uploader import cargar_jsons_en_mongo

if __name__ == "__main__":
    cargar_jsons_en_mongo()
