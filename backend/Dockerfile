FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero (mejor para cache de capas)
COPY requirements.txt .

# Instalar dependencias del sistema en dos pasos para minimizar uso de espacio
RUN apt-get update && apt-get install -y poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    gcc libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 🧠 Instalar torch para CPU (evita CUDA y NVIDIA drivers pesados)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.1.2+cpu

# Instalar el resto de las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY ./app /app/app

# 👇 Copiar el entrypoint y darle permisos
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 👉 Reemplazar CMD con ENTRYPOINT + CMD separados
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
