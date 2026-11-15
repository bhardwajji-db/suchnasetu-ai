# SochnaSetu AI — Current State & Technical Baseline

**Target Repository:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Evaluation Role:** Senior Software Architect, AI/ML Engineer, OCR Research Engineer  
**Inspection Date:** 2026-11-14  
**Audit Context:** Pre-implementation baseline assessment for Computer Organization & Architecture (COA) laboratory submission.  

---

## 1. Executive Baseline Summary

SochnaSetu AI is an operational civic intelligence system designed to ingest, process, verify, and summarize complex Indian administrative circulars, scholarship announcements, and government gazettes.

The codebase is built on an asynchronous **FastAPI** backend with **Tesseract v5.4.0** and **Gemma 4** local reasoning via **Ollama**, coupled with a **React 19 + TypeScript + Tailwind CSS** frontend.

### Current Health & Quality Scorecard
| Dimension | Measured Status | Verification Evidence |
|---|---|---|
| **Frontend Tests** | **98 Passed / 0 Failed (100%)** | 26 Vitest test suites executed cleanly in 10.29s |
| **Frontend Build** | **0 Errors / 0 Warnings** | `tsc -b && vite build` bundled 1,981 modules in 830ms |
| **Frontend Linter** | **0 Errors / 18 Warnings** | Oxlint passed (18 synchronous `setState` in `useEffect` warnings) |
| **Backend Tests** | **448 Passed / 13 Skipped** | Executed via Pytest 9.1.1 on Python 3.11.15 |
| **Database Schema** | **Version 5 (18 Tables)** | SQLite3 in Write-Ahead Logging (WAL) mode |
| **English OCR CER**| **0.69% (WER: 6.06%)** | Measured on `synthetic_scholarship_notice.png` (2.15s, 33.7MB) |
| **Bilingual OCR CER**| **2.75% (WER: 7.21%)** | Measured on `gazette_corrigendum_2017.jpeg` (6.30s, 59.2MB) |
| **Security Posture**| **Air-gapped by default** | Argon2id + HMAC-SHA256 digests + parameterized SQL |

---

## 2. Architectural Subsystem Baseline

### 2.1 Ingestion & Document Processing (`src/notice2action/ingestion.py`)
- **Status:** **WORKING**
- **Capabilities:**
  - Validates MIME types and magic bytes (`%PDF-`, `\xFF\xD8\xFF`, `\x89PNG`).
  - Limits file size to 15MB and PDF page counts to 30 pages.
  - Digital PDFs bypass OCR if extractable digital text length $\ge 30$ characters (<50ms execution).
  - Generates deterministic SHA-256 content hashes to achieve deduplication in ~12ms.
- **Limitations:** Only handles single-document uploads at the API endpoint level; multi-file batch uploads are queued in frontend memory rather than processed concurrently on the server.

### 2.2 OCR Pipeline (`src/notice2action/ocr.py`)
- **Status:** **PARTIALLY WORKING / REQUIRES UPGRADE**
- **Capabilities:**
  - Tesseract v5.4.0 with adaptive Lanczos upscaling (~2400px width / 300 DPI equivalent).
  - Skew correction via horizontal projection profile variance (tested on 3.5° skew: 100% recovery).
  - Dual-pass Tesseract (`hin+eng` for Devanagari and `eng` for Latin/numerals) with spatial IoU token fusion.
  - Generates token-level bounding boxes (`word_boxes`) and image dimensions.
- **Current Deficiencies:**
  1. **OSD Orientation Blindspot:** `image_to_osd` fails on documents with fewer than ~15 lines (e.g. posters), failing to correct 90°/270° rotations.
  2. **Overfitted Gazette Post-Processing:** Contains hardcoded strings for specific signatories (`"अपराजिता सारंगी"`) and Gazette numbers (`"11011/..."`).
  3. **Numeral Spacing Errors:** Token IoU fusion introduces intra-numeral spaces (`15/1 1/2026`).
  4. **Inert RapidOCR Adapter:** The `RapidOCREngine` skeleton exists in code, but lacks `rapidocr-onnxruntime` in the environment, falling back to slow single-core Tesseract.

### 2.3 AI & Information Extraction (`src/notice2action/analysis.py`, `grounding.py`)
- **Status:** **WORKING**
- **Capabilities:**
  - Modular LLM adapter supporting Ollama (`gemma4:latest`), OpenRouter, Gemini, and Hugging Face.
  - Strict JSON prompt enforcing the 6 Canonical Fields: Issuing Authority, Notice Number, Date, Recipient, Subject, and Required Action with Deadline.
  - Verbatim quote verification (`locate_quote_in_text`) and critical figure cross-checking (`extract_critical_tokens`).
  - Missing details explicitly marked `"Not stated in the notice."` with `status="not_stated"`.
- **Limitations:** Offline deterministic mock has a narrow cross-lingual dictionary for Hindi inquiries against English notices.

### 2.4 Human-in-the-Loop Review (`frontend/src/components/`)
- **Status:** **PARTIALLY WORKING**
- **Current Implementation:**
  - `OriginalNoticeViewerModal.tsx` provides side-by-side zoomable image viewing with red wavy underlines for text matches and coordinate bounding boxes on the original scan.
  - `ConfirmationModal.tsx` allows citizens to edit high-level structured fields (`purpose`, `eligibility`, `deadline`).
- **Missing Architecture:**
  - Citizens cannot edit the **raw extracted OCR text directly** before LLM extraction.
  - Word-level confidence color-coding (e.g., green for >85%, amber for 65–85%, red for <65%) is not rendered interactively on the text canvas.
  - Accepting or rejecting corrections operates at the field level, not the OCR word token level.

### 2.5 Persistence & Database (`src/notice2action/storage/db.py`)
- **Status:** **WORKING**
- **Capabilities:**
  - 18 normalized tables covering documents, analyses, checklist items, confirmations, Q&A interactions, users, sessions, and activity logs.
  - ACID-compliant Write-Ahead Logging (WAL) mode with thread-local pooling.
  - Session tokens and recovery codes stored as HMAC-SHA256 digests.

### 2.6 Frontend Workspace & UI (`frontend/src/`)
- **Status:** **WORKING**
- **Capabilities:**
  - 12 comprehensive workspace tabs covering Dashboard, Ingestion, Grounded Facts, Plain Summary, Revision Ledger, Eligibility Engine, Follow-Up Q&A, Action Navigator, Timeline, History, Settings, and Demo Library.
  - Full English and Hindi bilingual dictionary localization.
  - High-contrast, warm background, and text-sizing accessibility controls.
- **Deficiencies:** Monolithic JavaScript bundle size (1.17 MB) due to lack of dynamic view imports (`React.lazy`).
