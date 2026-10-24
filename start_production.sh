#!/usr/bin/env bash
# ==============================================================================
# SochnaSetu AI — Production Unified Launcher (Linux / macOS / Cloud)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "          SOCHNASETU AI -- PRODUCTION UNIFIED LAUNCHER"
echo "              Notice-to-Action Accessibility Assistant"
echo "======================================================================"

# 1. Check Python virtual environment or system Python
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    echo "[ERROR] Python 3 not found. Please install Python 3.11+."
    exit 1
fi

# 2. Compile frontend assets if missing
if [ ! -f "frontend/dist/index.html" ]; then
    echo "[1/3] Compiling React 19 production bundle..."
    (cd frontend && npm ci && npm run build)
else
    echo "[1/3] Frontend bundle verified at frontend/dist."
fi

# 3. Verify Ollama inference daemon
echo "[2/3] Checking Ollama AI server..."
if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "      Ollama server is active."
else
    echo "[WARNING] Ollama server is not reachable on http://127.0.0.1:11434."
    echo "          Please run 'ollama serve' in a separate terminal for full local LLM inference."
fi

# 4. Start production ASGI server
PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
WORKERS="${WORKERS:-2}"

echo "[3/3] Starting Unified Production Server on http://${HOST}:${PORT}..."
echo "      - Web Application: http://localhost:${PORT}"
echo "      - REST API:        http://localhost:${PORT}/api"
echo "      - API Docs:        http://localhost:${PORT}/docs"
echo "======================================================================"

exec "$PYTHON" -m uvicorn notice2action.api.server:app \
    --app-dir src \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS"
