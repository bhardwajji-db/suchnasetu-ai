# SuchnaSetu AI — Initial Project & Boundary Inventory

**Official Project Name:** SuchnaSetu AI  
**Project Description:** Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hacktoberfest HackDay 2026 — PS02  
**Project Root:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Parent Directory:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest`  
**Operating System:** Windows 11 Home (x64)  
**Shell:** PowerShell 5.1 / Core  
**Python Runtime:** Python 3.11.15 in `.venv`  
**Date of Inspection:** October 23, 2026  
**Auditor:** Antigravity AI Senior Architect & QA Automation Specialist  

---

## 1. Project Boundaries & Git Status

- **Project Root Existence:** Verified at `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`.
- **Git Initialized:** Yes.
- **Git Top-Level Root:** `C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober fest/ps2` (The project directory itself is the repository root).
- **Current Git Branch:** `main` (Up-to-date with `origin/main`).
- **Initial Working-Tree Tracked Changes (Unstaged):**
  - `.gitignore`
  - `API.md`
  - `ARCHITECTURE.md`
  - `README.md`
  - `REQUIREMENTS_CHECKLIST.md`
  - `docs/ARCHITECTURE.md`
  - `docs/archive/CLEANUP_REPORT.md`
  - `docs/archive/FINAL_AUDIT_PLAN.md`
  - `docs/archive/FINAL_BUG_FIX_LOG.md`
  - `docs/archive/FINAL_COMPLETION_REPORT.md`
  - `docs/archive/FINAL_FUNCTIONALITY_AUDIT.md`
  - `docs/archive/FINAL_FUNCTIONALITY_REPORT.md`
  - `docs/archive/FINAL_PONYTAIL_AUDIT.md`
  - `docs/archive/FINAL_SECURITY_PRIVACY_AUDIT.md`
  - `docs/archive/FINAL_TEST_RESULTS.md`
  - `docs/archive/FINAL_UI_VERIFICATION.md`
  - `docs/archive/IMPLEMENTATION_CHANGELOG.md`
  - `docs/archive/IMPLEMENTATION_REPORT.md`
  - `docs/archive/IMPLEMENTATION_TRACKER.md`
  - `docs/archive/MIGRATION_VERIFICATION_REPORT.md`
  - `docs/archive/POST_CLEANUP_VERIFICATION_REPORT.md`
  - `docs/archive/PROJECT_MASTER_AUDIT.md`
  - `docs/archive/SECURITY_AUDIT.md`
  - `reports/PS02_END_TO_END_TEST_REPORT.md`
  - `reports/PS02_MASTER_TASK_AUDIT.md`
- **Initial Untracked Files:** 0.
- **Initial Ignored Files & Directories:**
  - `.coverage` (SQLite coverage database)
  - `.pytest_cache/`
  - `.sessions/` (FastAPI backend local runtime session store)
  - `.venv/` (Local Python 3.11 virtual environment)
  - `assets/screenshots/viewport_*.png` & `workflow_tab*.png` (Legacy visual audit logs)
  - `frontend/dist/`
  - `frontend/node_modules/`
  - `release/` (Contains official competition zip deliverable `notice2action_ps02_release.zip`)
  - `reports/` audit markdown files (e.g. `BASELINE_AUDIT.md`, `TEST_RESULTS.md`)
  - `scratch/` (Development scripts, test runs, and temporary debug outputs)
  - `src/notice2action.egg-info/`
  - Bytecode caches (`__pycache__/`)

---

## 2. Parent Directory Inspection & Ownership Classification

**Immediate Parent Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest`

| Item Name | Mode | Size | Created / Modified | Classification | Relationship & Boundary Determination |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ps2` | Directory | — | 10/23/2026 | **PS02 Active Repo** | Authoritative active working repository for Hacktoberfest 2026 PS02 (SuchnaSetu AI). |
| `ps2 - Copy` | Directory | — | 10/22/2026 11:04 PM | **External PS02 Backup** | Complete manual external folder backup made prior to major verification refactor. **Protected: Kept 100% untouched.** |
| `ps2 - Copy.zip` | Archive | 215,169,064 bytes (~215 MB) | 10/22/2026 11:23 PM | **External PS02 Backup Archive** | Compressed zip archive containing a full snapshot of `ps2` including virtual environment. **Protected: Kept 100% untouched.** |
| `SUCHNASETU AI` | Directory | — | 10/20/2026 11:05 AM | **Sibling / Earlier Project** | Independent earlier project directory with its own `.git` repository, backend, frontend, and samples. **Protected: Kept 100% untouched.** |

**Parent Safety Verdict:**
No parent-directory content was deleted, renamed, or modified. Boundary enforcement strictly confines all write operations to `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`.

---

## 3. Project Root Structure & Component Catalog

```
ps2/
├── .env.example                       # Canonical environment configuration template
├── .gitignore                         # Git exclusion rules
├── API.md                             # REST API Specification (FastAPI endpoints)
├── ARCHITECTURE.md                    # Core System Architecture & Component Map
├── CONTRIBUTING.md                    # Developer guidelines and code quality standards
├── LICENSE                            # Apache 2.0 Open Source License
├── PROJECT_CLEANUP_PLAN.md            # Approved file audit and disposal plan
├── PROJECT_INITIAL_INVENTORY.md       # Baseline inventory and boundary report
├── pyproject.toml                     # Modern PEP 621 Python package configuration
├── README.md                          # Primary project documentation and quickstart
├── requirements.txt                   # Frozen production and test dependencies
├── REQUIREMENTS_CHECKLIST.md          # Traceability matrix for PS02 requirements
├── run_app.bat                        # Windows 1-click launcher (FastAPI + Vite React)
├── uv.lock                            # Deterministic dependency lockfile
│
├── assets/
│   ├── screenshots/                   # Multi-viewport and end-to-end workflow captures
│   └── tessdata/                      # Air-gapped Tesseract models (eng, hin, osd) + NOTICE.md
│
├── docs/
│   ├── ARCHITECTURE.md                # Architecture overview & design pillars
│   ├── DEMO_SCRIPT.md                 # 3-Minute Hackathon demonstration script
│   ├── MODEL_COMPATIBILITY_REPORT.md  # Gemma 4 resource profiling and hardware audit
│   ├── PS02_REQUIREMENTS_MATRIX.md    # Challenge requirement traceability
│   ├── SECURITY_AND_PRIVACY.md        # Air-gapped privacy and threat model
│   ├── TROUBLESHOOTING.md             # Operations guide for Windows PowerShell
│   └── archive/                       # Historical engineering logs and verification reports
│
├── frontend/                          # React 19 + TypeScript + Vite Web Application
│   ├── package.json                   # Dependencies: Lucide React, Tailwind CSS, Vite, Vitest
│   ├── vite.config.ts                 # Vite bundler configuration
│   ├── tsconfig.json                  # TypeScript compiler settings
│   └── src/
│       ├── components/                # 14 modular React components (PascalCase)
│       ├── views/                     # 7 full-page application views (PascalCase)
│       ├── context/                   # NoticeContext state container
│       ├── services/                  # Typed REST API client
│       ├── test/                      # Vitest component test suites
│       └── types/                     # Typed domain schemas matching backend
│
├── reports/                           # Comprehensive test, gap, and performance reports
│
├── scratch/                           # Diagnostic test scripts and AppTest verifications
│
├── scripts/
│   ├── evaluate_ground_truth.py       # Ground-truth evaluation script
│   ├── package_release.ps1            # Competition zip packager
│   ├── preflight.ps1                  # PowerShell preflight diagnostic wrapper
│   ├── preflight.py                   # Python environment and OCR preflight tester
│   ├── run.ps1                        # Full-stack launch script
│   ├── setup.ps1                      # Virtual environment setup script
│   └── test.ps1                       # Automated test execution script
│
├── src/
│   └── notice2action/                 # Core Python Backend Package
│       ├── analysis.py                # Gemma 4 analysis and structured JSON extraction
│       ├── checklist.py               # Sequential actionable checklist generator
│       ├── config.py                  # Environment config and preflight checks
│       ├── evaluator.py               # Independent ground-truth evaluation engine
│       ├── followup.py                # Notice-grounded follow-up Q&A engine
│       ├── grounding.py               # Deterministic quotation and evidence verifier
│       ├── ingestion.py               # Multi-format notice ingestion (Text, PNG, PDF)
│       ├── ocr.py                     # Tesseract OCR engine with contrast enhancement
│       ├── schemas.py                 # Pydantic v2 schemas and Six Core Fields
│       ├── security.py                # Prompt injection defense and upload sanitization
│       ├── summary.py                 # 7-Question plain-language summary generator
│       ├── translation.py             # Entity-preserving Hindi/English translation
│       ├── tts.py                     # Dual-mode Text-to-Speech (gTTS & Web Speech)
│       ├── api/                       # FastAPI REST Backend (`server.py`)
│       ├── llm/                       # Multi-provider client layer (Ollama, OpenRouter, Gemini, HF)
│       └── services/                  # EvidenceService & thread-safe SessionStore
│
└── tests/                             # 13 automated test suites (127 test items)
    ├── fixtures/                      # Sample English & Hindi notices and synthetic images
    ├── test_api_endpoints.py          # FastAPI REST endpoint integration tests
    ├── test_hindi_ocr.py              # Hindi language pack and OCR diagnostics
    ├── test_live_gemma4.py            # Live Ollama Gemma 4 integration tests (live marker)
    ├── test_multi_provider_llm.py     # Multi-provider LLM mock and contract tests
    ├── test_negative_and_edge_cases.py# Negative validation and edge-case tests
    ├── test_ollama_integration.py     # Unmocked Ollama connectivity & lifecycle tests
    ├── test_pdf_and_hindi_ocr_pipeline.py # Digital & scanned PDF extraction & OCR
    ├── test_pdf_ingestion.py          # PDF security, decompression bounds & page limits
    ├── test_phase_d_notice_scenarios.py # 15 required synthetic notice scenarios
    ├── test_playwright_react_frontend.py # Multi-viewport Playwright acceptance tests
    ├── test_services_and_six_fields.py # EvidenceService, SessionStore & Six Fields
    ├── test_structured_notice_regression.py # Robust JSON schema normalization tests
    └── test_unit_pipeline.py          # 25 deterministic unit tests
```
