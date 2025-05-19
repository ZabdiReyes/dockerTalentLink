#!/bin/bash

MODELPATH="/app/app/models/miniLM"

if [ ! -d "$MODELPATH" ]; then
  echo "📦 Modelo no encontrado. Descargando..."
  python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model.save('$MODELPATH')
"
else
  echo "✅ Modelo ya existe en $MODELPATH. No se descarga."
fi

# Ejecuta el comando original
exec "$@"
