# VocalIQ Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# App-Code kopieren
COPY . /app

# Berechtigungen setzen
RUN chmod +x scripts/*.py 2>/dev/null || true

EXPOSE 8000

# Health Check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 