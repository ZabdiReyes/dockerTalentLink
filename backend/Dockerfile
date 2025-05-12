FROM python:3.11-slim

# Instalar pdftotext (viene con poppler-utils)
RUN apt-get update && apt-get install -y poppler-utils

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código y dependencias
COPY ./app /app/app
COPY requirements.txt .

# Instalar paquetes de Python
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar la app con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
