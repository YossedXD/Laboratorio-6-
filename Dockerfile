# Imagen base con Python 3.10
FROM python:3.10

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalación de dependencias del sistema para cámara + OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Carpeta del proyecto
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
COPY detector_de_gestos.py .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Streamlit
EXPOSE 8501

# Ejecutar Streamlit
CMD ["streamlit", "run", "detector_de_gestos.py", "--server.address=0.0.0.0"]
