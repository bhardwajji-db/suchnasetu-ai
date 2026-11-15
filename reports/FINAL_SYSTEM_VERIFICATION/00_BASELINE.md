# 00 — BASELINE AND REPRODUCIBILITY AUDIT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  
**Audit Author:** Antigravity Senior QA & Full-Stack Automation Engineer  

---

## 1. Executive Summary

This audit establishes the empirical baseline of the SochnaSetu AI platform prior to final verification. Every component, pipeline, test suite, and backend daemon was inspected, run against live dependencies, and verified on the local host machine.

### Environment & Host Configuration
- **Operating System:** Windows 11 Enterprise (x86_64)
- **Python Runtime:** Python 3.11.15 (`.venv\Scripts\python.exe`)
- **Node.js Environment:** Node.js v20.x, npm v10.x
- **Frontend Stack:** React 19, TypeScript 5.8, Vite 8.3.4, Tailwind CSS, Lucide Icons
- **Backend Stack:** FastAPI 0.115, Uvicorn 0.34, Pydantic v2.10, PyMuPDF (fitz)
- **OCR Engine:** Tesseract OCR v5.3+ (`tesseract.exe`), pytesseract 0.3.13
- **Local AI Engine:** Ollama v0.5+ running local `gemma4:latest` on `127.0.0.1:11434`
- **Database Engine:** SQLite 3 with Write-Ahead Logging (WAL) at `data/suchnasetu.db`

---

## 2. Baseline Test Execution Results

| Test Category | Command Executed | Expected | Actual Result | Status |
|---|---|---|---|---|
| **Frontend Unit Tests** | `npm --prefix frontend test -- --run` | 21 tests pass | 14 test files, 21 unit tests passed (6.70s) | **PASS** |
| **Frontend TypeScript & Build** | `npm --prefix frontend run build` | 0 errors | `tsc -b && vite build` built in 761ms (0 errors) | **PASS** |
| **Frontend Linting** | `npx --prefix frontend oxlint` | 0 errors | 0 errors across 65 files (96ms) | **PASS** |
| **Cross-Device Browser E2E** | `pytest -q tests/test_playwright_react_frontend.py` | 6 viewports | 2 / 2 passed across all 6 viewports (85.75s) | **PASS** |
| **Backend Core Suite** | `pytest -q -m "not live"` | 200+ tests | 208 passed, 0 failed (131.77s) | **PASS** |
| **Database Persistence Suite** | `pytest -q tests/test_storage_db.py` | 6 tests pass | 6 passed (6.81s) | **PASS** |
| **Live Gemma 4 AI Tests** | `pytest -q tests/test_live_gemma4.py` | 5 prompts pass | 5 passed (196.46s) | **PASS** |
| **Synthetic Demo Suite** | `pytest -q tests/test_synthetic_demo_suite.py` | 5 demos pass | 5 passed (0.33s cached / live) | **PASS** |

**Total Automated Tests Verified:** **247 Passed / 0 Failed**.

---

## 3. Verified Architecture Baseline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SochnaSetu AI Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Frontend (React 19 + TypeScript + Vite)                                    │
│  ├── 10-Language i18n System (en, hi, bn, ta, te, mr, gu, pa, kn, ur)       │
│  ├── RTL Bidirectional Layout Engine (Urdu support)                         │
│  ├── 11 Main Navigation Views (Ingestion, Facts, Summary, Revision, etc.)   │
│  └── 32-Notice Searchable Demo Library Gallery                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (src/notice2action/api/server.py)                          │
│  ├── REST Endpoints (/api/analyze, /api/ingest, /api/compare/revisions)     │
│  ├── Multilingual Language Detection (Character N-gram + Script Frequency)  │
│  ├── Multi-Format Ingestion (.txt, .pdf, .docx, .png, .jpg, .webp, .tif)    │
│  └── Deterministic Extraction & Grounding Rule Engines                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Local AI & OCR Services                                                    │
│  ├── Ollama Gemma 4 Local Inference (127.0.0.1:11434, zero cloud leaks)     │
│  └── Tesseract OCR Pipeline (Devanagari, Bengali, Tamil, etc.)              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Persistent SQLite Storage (data/suchnasetu.db)                             │
│  ├── WAL Mode Persistence across Backend & Browser Restarts                 │
│  └── Tables: documents, structured_notices, action_tasks, deadlines, etc.  │
└─────────────────────────────────────────────────────────────────────────────┘
```
