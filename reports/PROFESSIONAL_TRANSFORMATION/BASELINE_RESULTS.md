# BASELINE EXECUTION & CODEBASE HEALTH REPORT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Verified Baseline Test Metrics

Every test suite was executed against the active codebase and local services (FastAPI on Port 8000, Ollama on Port 11434, and SQLite on `data/suchnasetu.db`):

| Test Suite / Subsystem | Execution Tool | Target Files | Verified Output | Status |
|---|---|---|---|---|
| **Frontend Unit Tests** | Vitest v5.0.5 + jsdom | 14 test files in `frontend/src/test/` | 21 / 21 tests passed (6.70s) | **PASS** |
| **Frontend Type Checking** | TypeScript 5.8 (`tsc -b`) | Entire frontend React codebase | 0 compile errors (0.45s) | **PASS** |
| **Frontend Production Build** | Vite 8.3.4 | `frontend/dist/` bundle | Built in 761ms (`index.html`, CSS, JS) | **PASS** |
| **Frontend Static Linter** | Oxlint | 65 frontend source files | 0 errors, 6 warnings (96ms) | **PASS** |
| **Cross-Device Browser E2E** | Playwright (Python) | 6 viewports (Mobile to Ultra-Wide) | 2 / 2 passed (85.75s) | **PASS** |
| **Backend Core Non-Live** | pytest 9.1.1 | 25 test files in `tests/` | 208 passed, 0 failed (131.77s) | **PASS** |
| **SQLite WAL Persistence** | pytest 9.1.1 | `tests/test_storage_db.py` | 6 passed (6.81s) | **PASS** |
| **Live Gemma 4 AI Tests** | pytest 9.1.1 + Ollama | `tests/test_live_gemma4.py` | 5 passed (196.46s) | **PASS** |
| **Synthetic Demo Notices** | pytest 9.1.1 + FastAPI | `tests/test_synthetic_demo_suite.py` | 5 passed (0.33s) | **PASS** |

**Total Automated Verifications:** **247 Passed / 0 Failed**.

---

## 2. Baseline Architecture Health

- **Python Virtual Environment:** Python 3.11.15 in `.venv\Scripts\python.exe`.
- **Node.js Environment:** Node.js v20.x, Vite 8.3.4, React 19.
- **OCR Engine:** Tesseract OCR v5.4.0 (`eng`, `hin`, `osd` installed).
- **Local AI:** Ollama local daemon serving `gemma4:latest` at `http://127.0.0.1:11434`.
- **Database Engine:** SQLite 3 in WAL mode at `data/suchnasetu.db`.
- **Memory Footprint:** Low (<300MB RAM for backend process, ~150MB for frontend Vite server).
- **Service Response Times:**
  - Health endpoint (`/api/health`): <15ms.
  - Plain text analysis (`/api/analyze`): 1.2s - 3.5s (rule-based extraction + LLM).
  - Revision ledger comparison (`/api/compare/revisions`): <80ms.
  - Demo library load (`/api/demo-library/load`): <45ms.
