# Notice2Action AI 📢

> **PS02 — Notice-to-Action Accessibility Assistant**  
> **Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
> **Track:** Track 1 — Best Use of Gemma 4  
> **Theme:** "AI Belongs to Everyone"  
> **Official Challenge Reference:** [events2026.co.in/problem-statements](https://events2026.co.in/problem-statements)  

---

## 🌟 Executive Summary

Official college circulars, scholarship announcements, government notices, and application forms are frequently published as low-resolution image posters, cluttered PDFs, or dense academic legalese. Students and applicants routinely miss critical deadlines, overlook mandatory documents, or misinterpret eligibility criteria.

**Notice2Action AI** is a local-first accessibility assistant powered by Google's **Gemma 4** (`gemma4:latest`) and local **Tesseract OCR v5.4.0**. It extracts, verifies, simplifies, and translates notices into **grounded, plain-language action checklists** with strict anti-hallucination verification.

---

## 🚀 Key Features

- **📥 Dual Input Pipeline:** Upload notice images/screenshots (PNG, JPG, WEBP) or paste raw circular text directly.
- **👁️ Preprocessed OCR Extraction:** Adaptive contrast enhancement, upscaling, and sharpening with Tesseract OCR; allows users to review and correct text before analysis.
- **🧠 Gemma 4 Semantic Analysis:** Extracts purpose, eligibility criteria, submission deadlines, application fees, required documents, contact details, and required actions into strict validated schemas.
- **🛡️ Deterministic Evidence Grounding:** Anti-hallucination engine verifies that every single extracted fact is backed by a verbatim quotation and line number in the source text.
- **⚠️ Uncertainty & Confirmation Gate:** Tentative dates ("provisional", "subject to change", "TBD") or conflicting details trigger a confirmation gate before becoming actionable tasks.
- **📋 Plain-Language Summary:** Answers the 7 core user questions (*What is this about? Who is eligible? What must I do? What documents? What deadline? Where to get help? What's missing?*).
- **✅ Interactive Action Checklist:** Ordered sequential checklist with category badges and completion tracking.
- **🌐 English & Hindi Bilingual Output:** Full bilingual support with critical entity preservation auditing (dates, amounts, and percentages remain strictly intact).
- **🔊 Audio Accessibility (Read-Aloud):** Dual-mode TTS (server-side MP3 via gTTS and client-side browser Web Speech API) for visually impaired applicants.
- **💬 Truthful Follow-Up Q&A:** Answers user questions strictly from notice evidence. If a rule is absent (e.g. late submissions), it truthfully reports that the notice does not state it.
- **🔒 Privacy-Preserving & Local-First:** 100% offline inference on Ollama; zero cloud API calls; zero data exfiltration.

---

## 🏗️ Architecture

```
                                  [Notice Image or Pasted Text]
                                                │
                                                ▼
                                    [Security & Ingestion Gate]
                               (Max 10MB, Format & Injection Shield)
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     ▼                                                     ▼
           [Image Preprocessing]                                     [Direct Text]
      (Grayscale, Autocontrast, Sharpen)                                   │
                     │                                                     │
                     ▼                                                     │
           [Tesseract OCR Engine]                                          │
                     │                                                     │
                     └──────────────────────────┬──────────────────────────┘
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
                     ┌──────────────────────────┼──────────────────────────┐
                     ▼                          ▼                          ▼
          [Plain-Language Summary]     [Action Checklist]        [Follow-Up Assistant]
            (7 Core Questions)         (Confirmation Gate)      (Truthful Grounded Q&A)
                     │                          │                          │
                     └──────────────────────────┼──────────────────────────┘
                                                ▼
                                 [Accessible Streamlit Web UI]
                               (Bilingual Toggle + Audio Read-Aloud)
```

---

## 💻 System Requirements & Local Setup

### Hardware Tested:
- **Processor:** AMD Ryzen 7 7445HS (8 Cores, 16 Threads)
- **Memory:** 16 GB DDR5 System RAM
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM)
- **OS:** Windows 11 Home (PowerShell compatible)

### Prerequisites:
1. **Python:** 3.11 or higher
2. **Ollama:** Version 0.40.3+ with `gemma4:latest` model pulled
3. **Tesseract OCR:** v5.4.0+ installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

## ⚡ Quickstart (Windows PowerShell)

All commands should be executed from the project root:
`C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`

### 1. Run Setup Script (Once)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\scripts\setup.ps1
```
*Creates project-local `.venv`, installs dependencies from `requirements.txt`, and generates `.env`.*

### 2. Verify Preflight Health
```powershell
.\scripts\preflight.ps1
```
*Checks Python runtime, Tesseract OCR executable, Ollama daemon, and `gemma4:latest` availability.*

### 3. Run Automated Tests
```powershell
# Run all 24 deterministic unit tests (fast, ~2.5s)
.\scripts\test.ps1

# Optional: Run live Gemma 4 model integration tests
.\scripts\test.ps1 -IncludeLive
```

### 4. Launch Application
```powershell
.\scripts\run.ps1
```
*Opens Notice2Action AI at `http://localhost:8501` in your default browser.*

---

## 📂 Project Directory Structure

```
ps2/
├── app.py                         # Streamlit application entry point
├── pyproject.toml                 # Canonical project configuration & metadata
├── requirements.txt               # Locked project dependencies
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git exclusions (.venv, caches, temp files)
│
├── src/notice2action/             # Core application package
│   ├── __init__.py                # Package metadata
│   ├── config.py                  # Configuration & preflight diagnostics
│   ├── schemas.py                 # Pydantic models & certainty statuses
│   ├── security.py                # Input validation & prompt injection defense
│   ├── ingestion.py               # Safe image & text ingestion
│   ├── ocr.py                     # Image preprocessing & Tesseract OCR pipeline
│   ├── grounding.py               # Evidence verification & anti-hallucination engine
│   ├── analysis.py                # Gemma 4 structured analysis orchestrator
│   ├── summary.py                 # Plain-language 7-question summary generator
│   ├── checklist.py               # Grounded action checklist with confirmation gates
│   ├── translation.py             # Hindi & English bilingual engine with entity audit
│   ├── followup.py                # Notice-grounded Q&A assistant
│   ├── tts.py                     # Accessible read-aloud TTS (gTTS + Web Speech API)
│   ├── llm/
│   │   └── ollama_client.py       # Ollama adapter, thinking-token cleaning, timeouts
│   └── ui/
│       └── components.py          # High-contrast accessible UI components & badges
│
├── tests/                         # Comprehensive automated test suites
│   ├── test_unit_pipeline.py      # All 24 required deterministic tests (100% passing)
│   ├── test_live_gemma4.py        # Live Gemma 4 integration test suite
│   └── fixtures/                  # Synthetic demo notices
│       ├── sample_scholarship_notice.txt
│       ├── sample_hindi_notice.txt
│       ├── sample_uncertain_notice.txt
│       ├── sample_missing_fields_notice.txt
│       └── synthetic_notice_ocr.png
│
├── scripts/                       # Windows PowerShell automation scripts
│   ├── setup.ps1                  # One-click environment bootstrap
│   ├── preflight.ps1              # System and model diagnostics check
│   ├── run.ps1                    # Application startup script
│   ├── test.ps1                   # Automated test runner
│   └── package_release.ps1        # Clean release zip packager
│
├── docs/                          # Comprehensive technical documentation
│   ├── ARCHITECTURE.md            # System architecture & design choices
│   ├── PS02_REQUIREMENTS_MATRIX.md# Full traceability against official PS02 rubric
│   ├── DEMO_SCRIPT.md             # 3-minute hackathon judge demonstration guide
│   ├── MODEL_COMPATIBILITY_REPORT.md # Hardware, VRAM, and Gemma 4 benchmarks
│   ├── SECURITY_AND_PRIVACY.md    # Threat model & safety guarantees
│   └── TROUBLESHOOTING.md         # Windows PowerShell operational guide
│
└── release/                       # Release packages (generated via script)
    └── notice2action_ps02_release.zip
```

---

## 🧪 Traceability to Official PS02 Rubric

| Requirement | Implementation | Relevant File | Status |
|---|---|---|---|
| **REQ-01 (Input & OCR)** | Photo/screenshot upload + text pasting + Tesseract OCR | `ingestion.py`, `ocr.py` | **Verified** |
| **REQ-02 (Structured Fields)** | Purpose, eligibility, deadline, documents, fee, contact, actions | `schemas.py`, `analysis.py` | **Verified** |
| **REQ-03 (Summary & Checklist)** | 7 core questions answered + ordered interactive checklist | `summary.py`, `checklist.py` | **Verified** |
| **REQ-04 (Bilingual & TTS)** | English and Hindi with entity audit + Web Speech read-aloud | `translation.py`, `tts.py` | **Verified** |
| **REQ-05 (Grounded Q&A)** | Answers strictly from notice; truthful reporting of absent facts | `followup.py`, `grounding.py` | **Verified** |
| **REQ-06 (Gemma 4 Centered)** | Local `gemma4:latest` model via Ollama adapter for all semantic tasks | `ollama_client.py`, `analysis.py` | **Verified** |

---

## 📦 Creating Clean Release Archive

To generate a clean ZIP archive excluding virtual environments, weights, caches, git history, and secrets:
```powershell
.\scripts\package_release.ps1
```
*Archive created at: `release/notice2action_ps02_release.zip`.*

---

## 📄 License

Licensed under the Apache License, Version 2.0.
