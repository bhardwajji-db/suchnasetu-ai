# SuchnaSetu AI — Development Guide

This guide describes development workflows, coding standards, environment setup, and contribution practices for SochnaSetu AI.

---

## 1. Local Environment Setup

### Prerequisites
- Python 3.11.x (installed and added to PATH)
- Node.js 18+ LTS or 20+ LTS (with npm)
- Tesseract OCR v5.3+ (`C:\Program Files\Tesseract-OCR\tesseract.exe`)
- Ollama (installed locally with `gemma4:latest` model downloaded)

### Virtual Environment Setup
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -e .
```

### Frontend Setup
```powershell
cd frontend
npm install
```

---

## 2. Running Services Locally

### All-in-One Launcher
```powershell
.\start_all.bat
```

### Manual Individual Commands
```powershell
# Terminal 1: Ollama Server
ollama serve

# Terminal 2: FastAPI Backend
.venv\Scripts\uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000

# Terminal 3: React Frontend
cd frontend && npm run dev
```

---

## 3. Code Standards & Quality Checks

### Frontend
```powershell
# TypeScript verification
npm --prefix frontend run build

# Unit & component tests
npm --prefix frontend test -- --run

# Linter
npx --prefix frontend oxlint
```

### Backend
```powershell
# Core test suite
.venv\Scripts\pytest -q -m "not live"

# Live AI tests (requires Ollama running)
.venv\Scripts\pytest -q tests/test_live_gemma4.py

# Synthetic demo suite
.venv\Scripts\pytest -v -s tests/test_synthetic_demo_suite.py
```
