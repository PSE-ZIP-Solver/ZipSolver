FROM python:3.12-slim

WORKDIR /app

# System-Bibliotheken für OpenCV (headless) und Tesseract OCR installieren
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    tesseract-ocr \
    tesseract-ocr-deu \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt aus dem Root kopieren und installieren
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den gesamten Projektcode in den Container kopieren
COPY .. .

# Port 8090 freigeben
EXPOSE 8090

# Startbefehl für Uvicorn
CMD ["uvicorn", "run_api:app", "--host", "0.0.0.0", "--port", "8090"]