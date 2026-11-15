# SochnaSetu AI — Project Overview & Architecture Specification

**Target Archive & Codebase:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**System Title:** SochnaSetu AI (सूचना + सेतु) — Notice-to-Action Accessibility Assistant  
**Event & Track:** Hacktoberfest 2026 — Track 1: Best Use of Gemma 4 (PS 02: Notice-to-Action Accessibility Assistant)  
**Evaluation Role:** Senior Software Architect, AI/ML Engineer, OCR Research Engineer, QA Engineer, Security Auditor  
**Audit Date:** 2026-11-14  

---

## 1. Project Purpose & Mission

Official public circulars, statutory orders, university examination announcements, and administrative notices in India are customarily published as dense, low-resolution scanned posters, multi-column bilingual gazettes, or complex bureaucratic PDFs. Citizens, applicants, and college students routinely face missed deadlines, disqualification, or financial forfeiture due to obscured requirements, legalese, and inaccessible document formatting.

**SochnaSetu AI** is an air-gapped, privacy-first civic intelligence system that converts bureaucratic notices into structured, verified, and plain-language action plans. By combining adaptive OCR, local Gemma 4 reasoning, deterministic evidence grounding, and an accessible bilingual web portal, the system extracts critical facts without hallucinating unstated details.

### Core Capabilities
1. **Multi-Format Ingestion:** Accepts scanned/digital PDFs, JPEG/PNG images, and raw pasted text up to 15MB.
2. **Adaptive Multilingual OCR:** Tesseract v5.4.0 with dual-pass Devanagari and Latin fusion, projection profile deskewing, OSD upright rotation, and contrast normalization.
3. **Six Core Canonical Fields:** Issuing Authority, Notice Reference Number, Notice Date, Recipient, Main Subject, and Required Action with Cutoff Deadline.
4. **Anti-Hallucination Evidence Grounding:** Verifies every extracted fact against verbatim source text; strictly preserves `"Not stated in the notice."` for omitted requirements.
5. **Human-in-the-Loop Confirmation:** Identifies tentative or low-confidence spans and prompts citizens to confirm or override them with side-by-side original visual highlighting.
6. **Bilingual Accessibility:** Complete English and Hindi (`हिंदी`) localization across summaries, action checklists, follow-up Q&A, and Web Speech API audio synthesis.
7. **Cross-Notice Intelligence:** Identifies Corrigendum relationships (`AMENDMENT`, `EXTENSION`, `CANCELLATION`) and renders differential revision ledgers.

---

## 2. Complete Technology Stack

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND CLIENT                                   │
│  React 19.3.1  •  TypeScript 6.0.3  •  Vite 8.3.4  •  Tailwind CSS v4.3.3        │
│  Lucide React Icons  •  React Router DOM 7.18.4  •  Web Speech API (TTS)         │
│  Vitest 5.0.5  •  @testing-library/react 16.3.3  •  JSDOM 30.1.3                 │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Reverse Proxy /api (:5173 -> :8000)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                BACKEND SERVICES                                  │
│  FastAPI 0.115+  •  Starlette  •  Uvicorn  •  Pydantic v2  •  Python 3.11.15    │
│  PyPDF 5.1+  •  Pillow (PIL) 11.1+  •  NumPy 2.2+  •  Pytesseract 0.3.13        │
│  Argon2id (argon2-cffi)  •  HMAC-SHA256  •  SQLite3 (WAL Mode)                  │
└──────────────────┬───────────────────────────────────────────────┬───────────────┘
                   │                                               │
                   ▼                                               ▼
┌──────────────────────────────────────┐       ┌───────────────────────────────────┐
│              OCR ENGINE              │       │          AI / LLM LAYER           │
│  Tesseract OCR v5.4.0 Engine         │       │  Ollama Local Daemon (:11434)     │
│  Traineddata: eng, hin, osd          │       │  google/gemma-4-31b-it (Default)  │
│  OpenCV / NumPy Projection Deskew    │       │  OpenRouter / Google Gemini API   │
│  Adaptive Contrast & Lanczos Scaling │       │  Hugging Face Inference API       │
└──────────────────────────────────────┘       └───────────────────────────────────┘
```

### Detailed Component Inventory

| Subsystem | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | React | `19.3.1` | Concurrent UI rendering with strict hooks and error boundaries |
| **Language & Bundler** | TypeScript / Vite | `~6.0.3` / `^8.3.4` | Strict type checking and ESM build pipeline |
| **Styling & Theme** | Tailwind CSS | `^4.3.3` | Dual-theme (Light Civic / Dark Midnight Navy) + WCAG 2.1 AA |
| **Icons & Media** | Lucide React | `^1.59.0` | Accessible SVG status icons and visual controls |
| **Backend Framework** | FastAPI | `>=0.115.0` | High-throughput asynchronous REST API |
| **Data Validation** | Pydantic v2 | `>=2.10.0` | Strict schema serialization and payload validation |
| **Primary OCR** | Tesseract OCR | `v5.4.0` | Local C++ OCR engine with Leptonica 1.84.1 |
| **Image Processing** | Pillow & NumPy | `11.1.0` / `2.2.0` | Lanczos interpolation, projection profile deskew, binarization |
| **PDF Extraction** | PyPDF | `>=5.1.0` | Digital text extraction & scanned page rasterization |
| **Database** | SQLite3 | `3.45.0` (WAL) | ACID-compliant persistence, 18 tables, zero-cloud dependency |
| **Password Hashing** | Argon2id | `argon2-cffi` | Cryptographic key derivation (`time_cost=2`, `memory=64MB`) |
| **Session Security** | HMAC-SHA256 | Python `hmac` | Digest-only session tokens and 6-digit recovery codes |
| **Local LLM Engine** | Ollama | `>=0.5.0` | Local GGUF Gemma 4 inference (`gemma4:latest`) |
| **Cloud LLM Providers**| OpenRouter / Gemini | API v1 / v1beta | Optional multi-provider cloud fallback |

---

## 3. High-Level System Architecture & Dataflow

```
[ Citizen Document Input ]
 (PNG, JPG, PDF, or Pasted Text)
           │
           ▼
[ FastAPI Ingestion Gateway ] ──► [ Security & Validation ]
                                    • Magic byte MIME check
                                    • Max size 15MB limit
                                    • SHA-256 fingerprinting
                                    • Prompt injection defense
                                    │
                                    ▼
                          [ Document Routing ]
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
 [ Digital PDF Path ]                                  [ Scanned / Image Path ]
  • PyPDF text extraction                               • Tesseract OSD (Upright Rotation)
  • If text >= 30 chars: Bypass OCR                     • Projection Profile Deskew
                                                        • Lanczos Upscaling (~300 DPI)
                                                        • Median Noise Filter / Autocontrast
                                                        • Dual-Pass Tesseract (hin+eng)
                                                        • Token IoU Spatial Fusion
                                                        │
                                                        ▼
                                              [ Extracted OCR Text & Bounding Boxes ]
                                                        │
                                                        ▼
                                              [ LLM Extraction Engine ]
                                                • Ollama / Gemma 4 / Gemini
                                                • Strict JSON System Prompt
                                                • 6 Canonical Fields + Checklist
                                                        │
                                                        ▼
                                              [ Evidence Grounding Layer ]
                                                • Verbatim Quote Verification
                                                • Critical Token Calibration
                                                • Missing Info -> "Not stated"
                                                • Ambiguous -> "Needs confirmation"
                                                        │
                                                        ▼
                                              [ SQLite WAL Persistence ]
                                                • `documents` & `analyses`
                                                • `checklist_items` & `confirmations`
                                                        │
                                                        ▼
                                              [ React 19 Frontend Views ]
                                                • Dashboard & Fact Cards
                                                • Side-by-side Notice Highlighting
                                                • Citizen Action Slips & Exports
```

---

## 4. Current Implementation Status (`ps2`)

The `ps2` directory contains the complete, production-ready implementation of SochnaSetu AI:
- **Database Schema Version:** `5` (Fully migrated across 18 SQLite tables).
- **Frontend Code Quality:** Passing `oxlint` (0 errors), compiling clean via `tsc -b && vite build` (0 errors), and passing **26 Vitest test suites (98 unit tests)**.
- **Backend Code Quality:** 448 automated Pytest test cases passing, covering API endpoints, persistent authentication, document processing, and multi-provider failover.
- **Visual Bounding-Box Highlighting:** Added coordinate mapping (`word_boxes`, `image_dimensions`) connecting OCR tokens to the frontend document viewer.
