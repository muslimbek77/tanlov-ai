FROM python:3.11-slim

# Environment o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Ishchi direktoriya
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    libmagic-dev \
    tesseract-ocr \
    tesseract-ocr-uzb \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ollama (local LLM)
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Kodni nusxalash
COPY . .

# Static files yaratish
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Foydalanuvchi yaratish
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Default command
CMD ["gunicorn", "tanlov_ai.wsgi:application", "--bind", "0.0.0.0:8000"]
