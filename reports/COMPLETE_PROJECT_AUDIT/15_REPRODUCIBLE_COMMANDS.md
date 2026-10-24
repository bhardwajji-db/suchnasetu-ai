# 15. REPRODUCIBLE RUN & TEST COMMANDS — SOCHNASETU AI

All commands required to install, build, run, and test SochnaSetu AI on Windows 11.

---

## 1. Quick Launch (One-Click)

### Production Mode (Unified Port 8000)
```powershell
.\\start_production.bat
```
*Builds the frontend, ensures Ollama is running, and launches the unified server on `http://localhost:8000`.*

### Development Mode (Vite on 5173 + FastAPI on 8000)
```powershell
.\\start_all.bat
```

---

## 2. Automated Test Execution

### Run All Backend Regression Tests (213 Tests)
```powershell
.venv\\Scripts\\python -m pytest tests/
```

### Run All Frontend Vitest Suites (38 Tests)
```powershell
npm --prefix frontend test -- --run
```

### Run Master 20-Feature End-to-End Verification
```powershell
.venv\\Scripts\\python scripts/verify_all_features.py
```

### Run Ground Truth Accuracy Audit
```powershell
.venv\\Scripts\\python scripts/evaluate_ground_truth.py
```

### Build Frontend Production Assets
```powershell
npm --prefix frontend run build
```
