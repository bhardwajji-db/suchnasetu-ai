# REPRODUCIBLE RUN & DEMONSTRATION INSTRUCTIONS
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Quick Launch (Recommended)

Double-click `start_all.bat` or run in PowerShell:
```powershell
.\start_all.bat
```

This single command:
1. Verifies the local Ollama server on `http://127.0.0.1:11434` (starting it if offline).
2. Launches the FastAPI backend on `http://127.0.0.1:8000`.
3. Launches the React 19 + Vite frontend on `http://localhost:5173`.
4. Automatically opens `http://localhost:5173` in your default browser.

---

## 2. Manual Service Launch

```powershell
# 1. Start Ollama local AI server:
ollama serve

# 2. Start FastAPI backend (from project root):
.venv\Scripts\uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000

# 3. Start React 19 Frontend:
cd frontend && npm run dev
```

---

## 3. Running Automated Tests

```powershell
# 1. Frontend unit tests (Vitest - 21 tests):
npm --prefix frontend test -- --run

# 2. Frontend production build & typecheck:
npm --prefix frontend run build

# 3. Backend core tests (208 tests):
.venv\Scripts\pytest -q -m "not live"

# 4. Database persistence tests (6 tests):
.venv\Scripts\pytest -q tests/test_storage_db.py

# 5. Live Gemma 4 AI tests (5 tests):
.venv\Scripts\pytest -q tests/test_live_gemma4.py

# 6. Synthetic demo notices (5 demos):
.venv\Scripts\pytest -v -s tests/test_synthetic_demo_suite.py

# 7. Playwright cross-device browser tests:
pytest -q tests/test_playwright_react_frontend.py
```
