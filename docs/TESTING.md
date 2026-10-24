# SuchnaSetu AI — Testing & QA Guide

This document details the test framework architecture, ground-truth fixtures, and execution procedures for SochnaSetu AI.

---

## 1. Test Architecture

The test suite spans three distinct tiers:

1. **Frontend Testing (Vitest + jsdom):**
   - 14 test files in `frontend/src/test/`.
   - Tests component rendering, modal dialogs, i18n context, audio controls, and the Demo Library.
   - Command: `npm --prefix frontend test -- --run`

2. **Backend Unit & Integration Testing (pytest):**
   - 25 test files in `tests/`.
   - Tests multi-format ingestion, OCR, Pydantic schemas, SQLite persistence, and API contracts.
   - Command: `.venv\Scripts\pytest -q -m "not live"`

3. **Live AI & Synthetic Demo Verification (pytest + Ollama):**
   - Tests live Ollama Gemma 4 inference (`tests/test_live_gemma4.py`).
   - Tests 5 end-to-end hackathon demo notices (`tests/test_synthetic_demo_suite.py`).
   - Command: `.venv\Scripts\pytest -v -s tests/test_synthetic_demo_suite.py`

4. **Cross-Device Browser E2E Testing (Playwright):**
   - Tests 6 device viewports (1920x1080 to 390x844).
   - Command: `pytest -q tests/test_playwright_react_frontend.py`

---

## 2. Test Execution Commands

```powershell
# Run all non-live backend tests (208 tests)
.venv\Scripts\pytest -q -m "not live"

# Run database persistence tests (6 tests)
.venv\Scripts\pytest -q tests/test_storage_db.py

# Run live Gemma 4 AI tests (5 tests)
.venv\Scripts\pytest -q tests/test_live_gemma4.py

# Run live synthetic demo notices (5 demos)
.venv\Scripts\pytest -v -s tests/test_synthetic_demo_suite.py

# Run frontend unit tests (21 tests)
npm --prefix frontend test -- --run

# Run Playwright cross-device tests (6 viewports)
pytest -q tests/test_playwright_react_frontend.py
```
