# SochnaSetu AI (PS02) — QA Baseline Report
**Audit Date:** October 24, 2026  
**Auditor:** Senior QA Automation & Release Verification Engineer  
**Workspace:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Execution Environment:** Windows 11 Pro 64-bit, PowerShell 5.1 / 7, VS Code / Antigravity

---

## 1. Baseline System Discovery & Environment

| Component | Specification / Version | Status |
|---|---|---|
| **Operating System** | Windows 11 Pro 64-bit (Build 26100) | Active |
| **Python Runtime** | Python 3.11.15 (`uv` virtualenv at `.venv/`) | Verified (`.venv/Scripts/python.exe`) |
| **Node.js / npm** | Node.js v22.14.0, npm 10.9.2 | Verified |
| **Frontend Stack** | React 19.1.0, TypeScript 5.8.3, Vite 8.3.4, Tailwind CSS 4.1.8 | Verified |
| **Backend Stack** | FastAPI 0.115.11, Uvicorn 0.34.0, Pydantic v2.11.1 | Verified |
| **OCR Engine** | Tesseract v5.4.0.20240606 (`C:\Program Files\Tesseract-OCR\tesseract.exe`) | Active (`eng`, `hin`, `osd` traineddata) |
| **Local LLM Engine** | Ollama local daemon (`http://127.0.0.1:11434`) running `gemma4:latest` (8B) | Active |
| **Browser Engine** | Google Chrome v133 (`C:\Program Files\Google\Chrome\Application\chrome.exe`) | Active for Playwright headless |

---

## 2. Live Services & Network Endpoints

- **FastAPI REST Backend:** `http://127.0.0.1:8000` (PID 27904 / Uvicorn server, 37 active routes)
  - `/api/health` -> HTTP 200 `overall_status: ok`
  - `/api/providers` -> HTTP 200 `active_provider: ollama`, `model_name: gemma4:latest`
  - Compatibility aliases: `/api/eligibility/check`, `/api/compare/revisions`, `/api/actions/export-calendar`
- **React / Vite Dev Server:** `http://127.0.0.1:5173` (PID 29628)
  - HTTP 200, fast HMR active, 0 console exceptions on load.
- **Ollama Inference Engine:** `http://127.0.0.1:11434`
  - Models available: `gemma4:latest` (8.0B), `qwen2.5:latest` (7.6B).

---

## 3. Test Suite Baseline Execution

| Test Suite | Command | Result | Pass Rate |
|---|---|---|---|
| **Frontend Unit / Component** | `npm --prefix frontend test -- --run` | 13/13 test files passed, 20/20 unit tests passed | **100% PASS** |
| **TypeScript Compilation** | `npm --prefix frontend run build` | Built in 598ms, 0 type errors | **100% PASS** |
| **Static Code Audit** | `npx oxlint frontend/src` | 0 errors across 49 files | **100% PASS** |
| **Playwright E2E Suite** | `pytest tests/test_playwright_react_frontend.py` | 2/2 passed (multi-viewport & workflow) | **100% PASS** |
| **Backend Unit & Integration** | `pytest tests/test_*.py` | 182 passed | **100% PASS** |
| **Live Gemma 4 Inference** | `pytest tests/test_live_gemma4.py` | 5/5 passed | **100% PASS** |

---

## 4. Initial Defect Register Baseline

The user reported that several buttons and controls did not appear to work or completed no visible action. Baseline investigation discovered the following root causes:
1. **Dashboard Image Drop Dead-End:** Dropping an image on `DashboardView` set state but did not render `<OCRPanel />`, leaving the notice buffer empty and the Analyze button disabled.
2. **Settings Link Navigation:** `DashboardView` footer link for "Settings & Diagnostics" called `setActiveTab(8)` (Timeline) instead of `setActiveTab(10)` (Settings).
3. **Checklist Keyboard Inactivity:** `ActionChecklistTable.tsx` checkboxes lacked `role="checkbox"`, `tabIndex={0}`, and `onKeyDown` listeners.
4. **Action Checklist Download Fallback:** Download Markdown button failed silently when `structuredNotice` was missing.
5. **Fixture 404:** Fallback selector in `Sidebar.tsx` referenced `sample_court_summons.txt` which did not exist on disk.
6. **API Route Divergence:** Tests and documentation referenced alias routes `/api/eligibility/check`, `/api/compare/revisions`, and `/api/actions/export-calendar`.

All identified baseline defects were prioritized for surgical repair and empirical regression re-testing.
