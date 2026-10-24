# ==============================================================================
# SochnaSetu AI — Notice-to-Action Accessibility Assistant (PS02)
# Multi-Stage Production Dockerfile (React 19 Frontend + FastAPI Python Backend)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build the React 19 + TypeScript + Vite Frontend
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies first for optimal Docker layer caching
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source code and compile production bundles
COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python 3.11 Runtime Environment
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

# Metadata
LABEL maintainer="SochnaSetu AI Engineering Team"
LABEL description="Production container for SochnaSetu AI Notice-to-Action Assistant"
LABEL version="2.0.0"

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src" \
    APP_ENV="production" \
    PORT=8000 \
    HOST="0.0.0.0" \
    OLLAMA_BASE_URL="http://ollama:11434" \
    OLLAMA_MODEL="gemma4:latest"

# Install system dependencies (Tesseract OCR with Hindi and OSD models, Poppler, and curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-osd \
    poppler-utils \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and install Python packages
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code and essential assets
COPY src/ /app/src/
COPY assets/ /app/assets/
COPY data/ /app/data/
COPY tests/fixtures/demo_library/ /app/tests/fixtures/demo_library/

# Copy compiled frontend production assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Create dedicated non-root application user for defense-in-depth security
RUN useradd -m -u 1001 suchnasetu && \
    mkdir -p /app/data/uploads && \
    chown -R suchnasetu:suchnasetu /app

USER suchnasetu

# Expose HTTP port
EXPOSE 8000

# Docker health check endpoint
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch production ASGI server
CMD ["python", "-m", "uvicorn", "notice2action.api.server:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
