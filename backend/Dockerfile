# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile for the Wikipedia RAG FastAPI backend
# Build:  docker build -t rag-backend .
# Run:    docker run -p 8000:8000 --env-file .env rag-backend
# ─────────────────────────────────────────────────────────────────────────────

# Use a slim Python 3.11 base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required by sentence-transformers / chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy and install Python dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Copy the vector store data
COPY data/ ./data/

# Expose the default uvicorn port
EXPOSE 8000

# Health-check so Docker / Kubernetes knows when the app is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/wikipedia/status')"

# Run the API with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
