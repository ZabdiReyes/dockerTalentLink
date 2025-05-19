import sys
import os
# Asegura que /app esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.parser.gpt4omini import convert_txts_with_gpt4omini

if __name__ == "__main__":
    convert_txts_with_gpt4omini(
        input_dir="/app/Data/TxT_Raw",
        output_dir="/app/Data/Json/GPT4omini"
    )