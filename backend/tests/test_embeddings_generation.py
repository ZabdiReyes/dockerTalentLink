import os
import json
import sys
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.parser.jsonembeddings import *

def main():

    # Embeddings por palabra
    procesar_directorio_jsons("Data/Json/Concatenado", "Data/Json/Embeddings_palabra", modo="palabra")

    # Embeddings por frase
    #procesar_directorio_jsons("Data/Json/Concatenado", "Data/Json/Embeddings_frase", modo="frase")

if __name__ == "__main__":
    main()
