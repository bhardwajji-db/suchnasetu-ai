# Notice2Action AI 📢

> **PS02 — Notice-to-Action Accessibility Assistant**  
> **Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
> **Track:** Track 1 — Best Use of Gemma 4  
> **Theme:** "AI Belongs to Everyone"  
> **Official Challenge Reference:** [events2026.co.in/problem-statements](https://events2026.co.in/problem-statements)  

---

## 🌟 Executive Summary

Official college circulars, scholarship announcements, government notices, and application forms are frequently published as low-resolution image posters, cluttered PDFs, or dense academic legalese. Students and applicants routinely miss critical deadlines, overlook mandatory documents, or misinterpret eligibility criteria.

**Notice2Action AI** is an air-gapped, local-first accessibility assistant powered by Google's **Gemma 4** (`gemma4:latest`) and local **Tesseract OCR v5.4.0**. It extracts, verifies, simplifies, and translates notices into **grounded, plain-language action checklists** with strict anti-hallucination verification.

The platform offers two seamless interfaces:
1. **Modern React 19 Frontend:** High-performance dashboard built with TypeScript, Vite, and Tailwind CSS v4, connected to a robust FastAPI REST layer.
2. **Legacy Streamlit Application:** Full-featured compatibility interface preserved for single-command rapid demonstrations.

---

## 🚀 Key Features

- **📥 Multi-Format Ingestion:** Paste raw text or upload scanned images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`) up to 10MB.
- **👁️ Adaptive Tesseract OCR:** Automatic grayscale conversion, Lanczos resolution enhancement, autocontrast stretching, and line preservation with confidence scoring.
- **🧠 Local Gemma 4 Extraction:** Extracts purpose, eligibility criteria, submission deadlines, application fees, required documents, contact details, and required actions into strict Pydantic v2 schemas.
- **🛡️ Deterministic Evidence Grounding:** Anti-hallucination engine verifies that every single extracted fact is backed by a verbatim quotation from the source text.
- **⚠️ Uncertain-Field Confirmation Workflow:** Tentative dates or conflicting details trigger an interactive confirmation modal, allowing users to verify or rectify values while preserving original notice ground truth.
- **📋 Plain-Language Accessible Summary:** Answers the 7 core user questions (*What is this about? Who is eligible? What must I do? What documents? What deadline? Where to get help? What's missing?*).
- **🎚️ Reading-Level Selector:** Switch dynamically between Simple (Grade 5), Standard (Grade 8), and Detailed explanations.
- **📜 Original Notice Viewer:** Slide-over modal accessible from any view to inspect source notice text, search words, copy text, and view original image scans.
- **✅ Interactive Action Checklist:** Ordered sequential checklist with category badges, deadline alerts, strike-through completion, and progress tracking.
- **📅 RFC 5545 iCalendar & Markdown Export:** Export scheduled deadlines with alarms (`.ics`) and formatted action dossiers (`.md`).
- **🌐 English & Hindi Bilingual Output:** Full bilingual support with critical entity preservation (dates, amounts, and percentages remain strictly intact).
- **🔊 Audio Accessibility (Read-Aloud):** Dual-mode TTS (server-side MP3 via gTTS and client-side browser Web Speech API) for visually impaired applicants.
- **💬 Truthful Follow-Up Q&A:** Answers user questions strictly from notice evidence. If a rule is absent, it truthfully reports that the notice does not state it.
- **🔒 100% Privacy-Preserving & Local-First:** Offline inference on local Ollama; zero cloud API calls; zero data exfiltration.

---

## 🏗️ System Architecture

```
                                [Notice Image or Pasted Text]
                                              │
                                              ▼
                                  [Security & Ingestion Gate]
                             (Max 10MB, Format & Injection Shield)
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
          [Image Preprocessing]                                   [Direct Text]
     (Grayscale, Autocontrast, Sharpen)                                 │
                    │                                                   │
                    ▼                                                   │
          [Tesseract OCR Engine]                                        │
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                                  [Editable Extracted Text]
                                              │
                                              ▼
                                 [Prompt Delimiter Framing]
                                              │
                                              ▼
                                  [Local Gemma 4 on Ollama]
                                              │
                                              ▼
                              [Evidence Grounding Verification]
                         (Verbatim Match & Critical Entity Audit)
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
         [Plain-Language Summary]    [Action Checklist]       [Follow-Up Assistant]
           (7 Core Questions)        (Confirmation Gate)     (Truthful Grounded Q&A)
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
       [Modern React 19 Frontend]                         [FastAPI REST Backend]
        (Port 5173 - Vite + Tailwind)                      (Port 8000 - server.py)
                    │
                    ▼
       [Legacy Streamlit Web UI]
         (Port 8501 - app.py)
```

---

## 💻 System Requirements & Local Setup

### Hardware Tested:
- **Processor:** AMD Ryzen 7 7445HS / Intel Core i7 or equivalent (8+ Cores)
- **Memory:** 16 GB DDR5 System RAM
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM) or equivalent CUDA GPU
- **OS:** Windows 11 Home / Pro (PowerShell compatible)

### Prerequisites:
1. **Python:** 3.11 or higher (configured in `.\.venv\`)
2. **Node.js:** v20+ or v24+ with npm
3. **Ollama:** Version 0.40.3+ with `gemma4:latest` model pulled
4. **Tesseract OCR:** v5.4.0+ installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

## ⚡ Verified Quickstart Runbook

All commands are executed from the project root:
`C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`

### 1. Start Local Ollama Server
In Terminal 1:
```powershell
ollama serve
```
*Verify model:*
```powershell
ollama list
# Should display gemma4:latest
```

### 2. Start FastAPI REST Backend (Port 8000)
In Terminal 2:
```powershell
.\.venv\Scripts\python.exe -m uvicorn notice2action.api.server:app --host 127.0.0.1 --port 8000
```
*Verify API health:*
```powershell
curl.exe -s http://127.0.0.1:8000/api/health
```

### 3. Start React 19 Frontend (Port 5173)
In Terminal 3:
```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
*Access in browser:* [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

### 4. Optional: Start Legacy Streamlit Interface (Port 8501)
In Terminal 4:
```powershell
.\.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.headless true
```
*Access in browser:* [http://localhost:8501/](http://localhost:8501/)

---

## 🧪 Comprehensive Automated Testing Runbook

```powershell
# 1. Run all backend pipeline and API unit tests (67 tests, ~27s)
.\.venv\Scripts\python.exe -m pytest tests/test_api_endpoints.py tests/test_unit_pipeline.py tests/test_negative_and_edge_cases.py tests/test_structured_notice_regression.py tests/test_notice_fingerprint_stale.py tests/test_ui_controls_comprehensive.py tests/test_streamlit_interaction.py -v

# 2. Run frontend component tests (10 suites, 16 tests, ~5s)
cd frontend
npm run test
cd ..

# 3. Compile frontend production bundle
cd frontend
npm run build
cd ..

# 4. Run real Google Chrome Playwright multi-viewport & workflow tests
.\.venv\Scripts\python.exe -m pytest tests/test_playwright_react_frontend.py -v

# 5. Run live Gemma 4 inference & OCR integration tests
.\.venv\Scripts\python.exe -m pytest tests/test_live_gemma4.py -v

# 6. Run ground-truth accuracy benchmark (100% Critical Field Accuracy)
.\.venv\Scripts\python.exe scripts/evaluate_ground_truth.py
```

---

## 📂 Project Directory Structure

```
ps2/
├── app.py                         # Legacy Streamlit application entry point
├── pyproject.toml                 # Canonical Python project configuration
├── requirements.txt               # Locked Python dependencies
├── .env.example                   # Environment configuration template
├── ARCHITECTURE.md                # Exhaustive system architecture document
├── API.md                         # Complete REST API specification
├── REQUIREMENTS_CHECKLIST.md      # PS02 requirements compliance matrix
├── IMPLEMENTATION_TRACKER.md      # Implementation progress tracker
├── IMPLEMENTATION_CHANGELOG.md    # Detailed changelog and audit log
├── FINAL_TEST_RESULTS.md          # Complete test results ledger
├── FINAL_BUG_FIX_LOG.md           # Defect root cause and remediation log
├── FINAL_UI_VERIFICATION.md       # Multi-viewport responsive audit report
├── FINAL_SECURITY_PRIVACY_AUDIT.md# Air-gap and threat model audit
├── FINAL_COMPLETION_REPORT.md     # Final release certification report
│
├── frontend/                      # Modern React 19 Frontend
│   ├── package.json               # Node dependencies & build scripts
│   ├── vite.config.ts             # Vite configuration with API proxy
│   ├── tsconfig.json              # TypeScript root configuration
│   └── src/
│       ├── App.tsx                # Top-level application component
│       ├── context/               # NoticeContext state provider
│       ├── components/            # Reusable UI component library
│       │   ├── Header.tsx         # Top bar with health & language switcher
│       │   ├── Sidebar.tsx        # Navigation tabs & demo loader
│       │   ├── NoticeBuffer.tsx   # Ground-truth notice buffer & demo selectors
│       │   ├── FileDropzone.tsx   # Drag-and-drop file uploader
│       │   ├── FactCard.tsx       # Grounded fact dimension cards
│       │   ├── ConfirmationModal.tsx # Uncertain-field verification modal
│       │   ├── OriginalNoticeViewerModal.tsx # Ground-truth document viewer
│       │   ├── PlainLanguageSummaryView.tsx # 7-question summary & reading level
│       │   └── ActionChecklistTable.tsx # Sequential checklist & exports
│       ├── views/                 # Primary tab views (Ingestion, Facts, Summary, QA)
│       ├── services/apiClient.ts  # Typed API client for FastAPI
│       └── test/                  # Vitest test suites (10 test files)
│
├── src/notice2action/             # Core Python package
│   ├── api/server.py              # FastAPI REST backend application
│   ├── config.py                  # Configuration & diagnostics
│   ├── schemas.py                 # Pydantic models & certainty statuses
│   ├── security.py                # Input validation & injection defense
│   ├── ingestion.py               # Document & text ingestion
│   ├── ocr.py                     # Adaptive Tesseract OCR pipeline
│   ├── grounding.py               # Anti-hallucination evidence engine
│   ├── analysis.py                # Gemma 4 structured analysis orchestrator
│   ├── summary.py                 # Plain-language summary generator (3 reading levels)
│   ├── checklist.py               # Grounded action checklist generator
│   ├── translation.py             # Hindi & English bilingual engine
│   ├── followup.py                # Grounded Q&A assistant
│   └── tts.py                     # Read-aloud TTS engine
│
├── tests/                         # Pytest test suites (74+ tests)
│   ├── test_api_endpoints.py      # FastAPI REST endpoint tests
│   ├── test_playwright_react_frontend.py # Chrome multi-viewport & workflow tests
│   ├── test_unit_pipeline.py      # Core unit pipeline tests
│   ├── test_live_gemma4.py        # Live local model integration tests
│   └── fixtures/                  # Synthetic demo notices (Scholarship, Placement, Water)
│
├── scripts/                       # PowerShell automation scripts
│   ├── setup.ps1                  # Bootstrap environment
│   ├── preflight.ps1              # System diagnostics
│   ├── package_release.ps1        # Clean release packager
│   └── evaluate_ground_truth.py   # Accuracy benchmark runner
│
└── release/                       # Clean production release archive
    └── notice2action_ps02_release.zip
```

---

## 📦 Clean Release Package

To generate a clean ZIP archive excluding virtual environments, weights, caches, git history, and transient dependencies:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```
*Archive created at: `release/notice2action_ps02_release.zip`.*

---

## 📄 License

Licensed under the Apache License, Version 2.0.
