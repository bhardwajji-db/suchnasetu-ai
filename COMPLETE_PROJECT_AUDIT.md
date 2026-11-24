# SochnaSetu AI — Complete Software Quality & System Architecture Audit

**Document Version:** 1.0.0  
**Audit Date:** November 24, 2026  
**Auditor:** Independent Principal Engineering & Quality Assurance Team  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Current Branch:** `integration-master` (Commit `71fa7b5`)  
**Audit Scope:** End-to-End Codebase, Runtime Execution, OCR Pipeline, Security, Storage, Frontend, and Deployment Readiness  

---

## 1. Executive Summary & Audit Mandate

This document provides a comprehensive, evidence-based engineering audit of **SochnaSetu AI (Notice-to-Action Accessibility Assistant - PS02)**. The audit was conducted through direct source code inspection, dependency analysis, empirical test suite execution (534 backend test items, 97 frontend Vitest tests, and Oxlint/Vite build toolchains), performance latency measurement, and live runtime probing.

### Overall System Assessment
SochnaSetu AI is a well-structured, privacy-focused administrative document intelligence platform designed to ingest circulars, academic notices, and government notifications. It bridges digital and scanned documents into structured, actionable items, eligibility rules, and deadline calendars. 

**Core Engineering Verdict:** The platform has achieved genuine production-readiness in its core workflows (bilingual English/Hindi OCR, SQLite persistence in WAL mode, CSRF/auth security boundaries, and responsive React 19 frontend). However, significant discrepancies exist between historical documentation claims and actual runtime reality—most notably regarding multilingual Indic language models (where only English and Hindi models are installed) and client-side React warning notices during asynchronous modal updates.

---

## 2. Complete Project Architecture Mapping

```
+----------------------------------------------------------------------------------------------------+
|                                    CLIENT TIER (Frontend)                                          |
|  React 19.3.1 | Vite 8.3.4 | TypeScript 6.0.3 | Tailwind CSS 4.3.3 | Lucide Icons | Context Store   |
+----------------------------------------------------------------------------------------------------+
                                                  │ (REST API / SSE / CSRF-Protected Cookies)
                                                  ▼
+----------------------------------------------------------------------------------------------------+
|                               APPLICATION GATEWAY (FastAPI Tier)                                   |
|   FastAPI 0.115+ | Uvicorn ASGI Server | Modern Async Lifespan | Defense-in-Depth Middleware        |
|   Rate Limiting (Token Bucket) | Session Auth (Argon2id) | CSRF Origin Validation | Upload Quota    |
+----------------------------------------------------------------------------------------------------+
           │                                 │                                    │
           ▼                                 ▼                                    ▼
+-----------------------+         +-----------------------+            +---------------------+
|      OCR ENGINE       |         |     AI / LLM TIER     |            |    STORAGE LAYER    |
| Tesseract v5.4.0      |         | Multi-Provider Router |            | SQLite 3 (WAL Mode) |
| (eng, hin, osd)       |         | - OpenRouter Cloud    |            | 19 Tables Managed   |
| Dual-Pass Token Fusion|         |   (Gemma 4 26B)       |            | Busy Timeout 30s    |
| RapidOCR Fallback     |         | - Local Ollama        |            | Startup Pruning     |
| Poppler pdftoppm      |         | - Hugging Face API    |            | /app/data Volume    |
| BBox Re-projection    |         | Strict Grounding Guard|            | Local Disk Quotas   |
+-----------------------+         +-----------------------+            +---------------------+
```

### 2.1 Frontend Architecture (`frontend/src`)
- **Framework & Tooling:** React 19.3.1, TypeScript 6.0.3, Vite 8.3.4, Tailwind CSS v4.
- **State Management:** Single source of truth managed via `NoticeContext.tsx` with local storage synchronization for settings, reading levels, and active notices.
- **Key Views:**
  - `IngestionView.tsx`: Multi-format file uploader (drag-and-drop, PDF, image, text), sample notice picker, demo library loader.
  - `DashboardView.tsx`: Tabbed interface housing Grounded Facts, Summary Actions, Checklist, and Verification drawers.
  - `OriginalNoticeViewerModal.tsx`: Visual document inspector displaying OCR bounding boxes overlaid on orientation-corrected images.
  - `EligibilityEngineView.tsx` & `RevisionLedgerView.tsx`: Specialized administrative decision trees and notice revision version diffing.
  - `SettingsView.tsx`: User preferences, theme selection (Dark/Light/Midnight Teal/Slate Green), and language selection.

### 2.2 Backend Architecture (`src/notice2action`)
- **API Framework:** FastAPI with modular routers:
  - `api/server.py`: Primary application entry point, middleware registration, notice ingestion, OCR, analysis, export (Markdown, ICS), and health routes.
  - `api/auth_routes.py`: User authentication, session management, registration, password recovery, and guest quota enforcement.
- **Core Processing Engines:**
  - `ocr.py`: Multi-stage OCR pipeline (preprocessing, deskewing, rotation recovery, dual-pass Tesseract execution, spatial token fusion, Devanagari dictionary post-correction).
  - `analysis.py`: LLM orchestration, structured field extraction, six core statutory fields schema adherence, and fallbacks.
  - `grounding.py` & `services/trust_engine.py`: Grounding and anti-hallucination verification engine computing verbatim quote containment and confidence scores.
  - `checklist.py`: Deterministic rule extraction converting free-form administrative text into structured actionable items.
  - `ingestion.py`: Safe file ingestion with MIME validation, magic byte checks, and PDF multi-page extraction.

### 2.3 Storage Architecture (`src/notice2action/storage/db.py`)
- **Engine:** SQLite 3 configured with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and a 30-second busy timeout (`PRAGMA busy_timeout = 30000;`).
- **Schema:** 19 distinct tables spanning documents, analyses, checklists, revisions, users, sessions, auth tokens, rate limits, notifications, and human review annotations.
- **Lifecycle Management:** Automated startup cleanup purging stale guest sessions (TTL 24h), expired auth tokens, and elapsed rate-limit windows.

---

## 3. Dependency & Dead Code Audit

### 3.1 Python Dependencies
- **Active Core:** `fastapi`, `uvicorn`, `python-multipart`, `pydantic`, `pytesseract`, `pillow`, `requests`, `python-dotenv`, `pypdf`, `pypdfium2`, `argon2-cffi`, `email-validator`.
- **RapidOCR (`rapidocr-onnxruntime>=1.3.0`):** Included in `requirements.txt` and `pyproject.toml`. Installed in `.venv`. In code (`src/notice2action/ocr.py`), it acts as an optional secondary engine (`RapidOCREngine`), but defaults to Tesseract.
- **`gTTS>=2.5.0`:** Installed for server-side Text-to-Speech (`tts.py`). In production, modern browsers utilize client-side Web Speech API via `SpeechSynthesis`, making `gTTS` primarily a headless fallback.
- **Unused Dependencies:** None found in active requirements; legacy libraries previously flagged (`reportlab`, `weasyprint`) were already pruned.

### 3.2 Frontend Dependencies
- **Active Core:** `react`, `react-dom`, `react-router-dom`, `lucide-react`, `tailwindcss`, `@tailwindcss/vite`.
- **Dev Dependencies:** `vitest`, `jsdom`, `@testing-library/react`, `oxlint`, `typescript`.
- **Linter Status:** `oxlint` scanned 91 files with 116 rules in 168ms: **0 warnings, 0 errors**.

### 3.3 Dead Code & Cleaned Artifacts
- The codebase was previously purged of obsolete scripts (`run_app.bat`, `start_all.bat`, `start_tunnel.bat`, `audit_buttons.py`).
- Runtime scripts now center on unified launchers: `LOCAL_DEPLOY.bat`, `start_production.sh`, and `run_sochnasetu.ps1`.

---

## 4. Architectural Strengths & Weaknesses

### 4.1 Architectural Strengths
1. **Zero External SaaS Requirement for Core Processing:** The entire OCR, text extraction, rule processing, and SQLite persistence pipeline can execute 100% locally and offline without external API keys.
2. **Deterministic Trust & Provenance Engine:** Extracted claims must be grounded in verbatim source quotes from the original notice; ungrounded statements are penalized with low trust scores, mitigating LLM hallucinations.
3. **Database Concurrency Resilience:** The transition to SQLite WAL mode with a 30-second busy timeout resolves prior file-locking deadlocks under multi-worker Uvicorn configurations.
4. **Clean Decoupling:** The React 19 frontend compiles to pure static assets (`frontend/dist`), enabling independent hosting on CDNs (e.g., Cloudflare Pages) or co-hosting directly from FastAPI.

### 4.2 Architectural Weaknesses
1. **Multilingual OCR Engine Mismatch:** While `language_detection.py` registers 10 Indian constitutional languages, the underlying Tesseract engine only has `eng` and `hin` trained data files installed. Non-Devanagari Indic scripts (Tamil, Telugu, Bengali, Gujarati, Punjabi, Urdu) fall back to English OCR.
2. **React 19 `act()` Warnings in Component Tests:** Vitest test output shows numerous `An update to NoticeProvider inside a test was not wrapped in act(...)` warnings during modal and banner async state updates.
3. **Synchronous OCR Processing in Request Path:** OCR execution on high-resolution multi-page documents (6.5s per page) runs synchronously inside API request workers, which can tie up ASGI workers during heavy burst traffic.

---

## 5. Summary Matrix of Architectural Quality

| Architectural Area | Implementation Status | Empirical Verification | Production Grade |
| :--- | :---: | :---: | :---: |
| **Frontend UI/UX** | Complete | Vitest 97/97 passed, Vite built in 1.08s | **A-** (React act warnings in tests) |
| **Backend REST API** | Complete | 52/52 API & Auth tests passed | **A** |
| **OCR Pipeline (Eng + Hin)**| Complete | Gazette 2.75% CER, Category E 12.60% CER | **A** |
| **Multilingual (8+ Indic)** | Incomplete | Fallback to English due to missing traineddata| **C** (Models absent) |
| **Database & Persistence** | Complete | 19 tables, WAL mode, 33/33 security passed | **A** |
| **Security & Headers** | Complete | nosniff, SAMEORIGIN, CSRF, Argon2id active | **A** |
| **PDF Ingestion** | Complete | 23/23 PDF tests passed (Vector + Scanned) | **A** |
