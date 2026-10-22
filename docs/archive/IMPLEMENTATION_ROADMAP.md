# Notice2Action AI — Prioritized Implementation Roadmap

**Problem Statement:** PS02 — Notice-to-Action Accessibility Assistant  
**Date of Audit:** October 20, 2026  
**Auditor:** Principal Software Architect & QA Lead  
**Current Readiness:** 100% Core Features Implemented & Verified (110 Tests Passing)  

---

## 1. Roadmap Prioritization Framework

Items are classified into four strategic tiers:
- **P0: Critical Correctness & Security:** High-impact defects, security vulnerabilities, or application blockers. (*Zero P0 defects currently present*).
- **P1: High-Priority Enhancements:** Core accessibility extensions, offline independence, and document type expansions.
- **P2: Usability & Feature Completeness:** Export enhancements, multi-lingual OCR data bundles, and configuration UX.
- **P3: Architectural Optimizations:** Containerization, token streaming, and embedding acceleration.

---

## 2. Prioritized Roadmap Items

### Tier P0: Critical Application-Blocking Issues
*No P0 issues identified during the forensic audit. All critical paths (ingestion, OCR, LLM inference, evidence verification, session isolation, and calendar export) are 100% operational.*

---

### Tier P1: High-Priority Enhancements

#### P1-1: Native Offline Text-to-Speech Engine
- **Reason:** Currently, `src/notice2action/tts.py` relies on `gTTS` (Google Translate TTS), which requires active internet connectivity. In an offline air-gapped scenario (e.g., local administrative office), audio playback fails or falls back to silent headers.
- **Affected Modules:** `src/notice2action/tts.py`, `src/notice2action/api/server.py`.
- **Dependencies:** `pyttsx3` or `edge-tts` (offline SAPI5 on Windows / espeak on Linux).
- **Acceptance Criteria:**
  - TTS endpoint produces valid `.wav` or `.mp3` audio when machine has zero network access.
  - Audio generation operates for both English and Hindi text.
- **Verification Method:** Run unit test with network sockets blocked (`unittest.mock.patch("socket.socket")`) asserting successful audio binary generation.

---

#### P1-2: Multi-Page PDF Splitting & Batch OCR Ingestion
- **Reason:** Real-world government notices frequently arrive as multi-page PDF documents. Currently, users must upload image files or extract text manually.
- **Affected Modules:** `src/notice2action/ingestion.py`, `src/notice2action/ocr.py`, `frontend/src/components/FileUploadZone.tsx`.
- **Dependencies:** `pypdf` or `pdf2image` + `poppler`.
- **Acceptance Criteria:**
  - Ingestion endpoint accepts `.pdf` files up to 25MB.
  - Extracts embedded text directly if native PDF; renders pages to images and runs Tesseract OCR if scanned PDF.
  - Aggregates page lines into `EvidenceService` with page-and-line markers (`Page 2, Line 14`).
- **Verification Method:** Execute ingestion test with synthetic 3-page scanned PDF fixture; verify all 3 pages are parsed into a single indexed notice.

---

### Tier P2: Usability & Feature Completeness

#### P2-1: Structured JSON Data Export
- **Reason:** In addition to human-readable Markdown and RFC 5545 `.ics` calendar files, enterprise legal workflows and case management software require machine-readable JSON exports.
- **Affected Modules:** `src/notice2action/api/server.py`, `frontend/src/components/ActionChecklistTable.tsx`.
- **Dependencies:** Existing `StructuredNotice` schema.
- **Acceptance Criteria:**
  - Provide `POST /api/export/json` endpoint and corresponding "Export JSON" button in the React UI.
  - Returns complete notice payload including Six Core Fields, certainty statuses, and timestamps.
- **Verification Method:** Test endpoint asserting `Content-Type: application/json` and schema compliance.

---

#### P2-2: Automated Hindi OCR Model (`hin.traineddata`) Downloader
- **Reason:** While English Tesseract OCR is installed by default, Hindi OCR requires `hin.traineddata` in the Tesseract `tessdata` folder. If absent, Hindi images fall back to English dictionary matching.
- **Affected Modules:** `scripts/setup_tesseract_hindi.ps1`, `src/notice2action/config.py`.
- **Dependencies:** Official Tesseract GitHub tessdata repository.
- **Acceptance Criteria:**
  - Provide PowerShell utility script to download and install `hin.traineddata` to `C:\Program Files\Tesseract-OCR\tessdata`.
  - Diagnostics endpoint checks for `hin` language availability and surfaces setup guidance if missing.
- **Verification Method:** Execute script, query `/api/health`, verify `"hin"` appears in Tesseract language list.

---

### Tier P3: Architectural Optimizations

#### P3-1: Docker Compose Multi-Service Deployment
- **Reason:** Provides one-click containerized deployment for Linux/macOS/Windows servers.
- **Affected Modules:** `Dockerfile`, `docker-compose.yml`, `frontend/Dockerfile`.
- **Dependencies:** Docker, Docker Compose, Linux base image with Tesseract installed.
- **Acceptance Criteria:**
  - `docker compose up` starts FastAPI backend, React frontend Nginx server, and links to host Ollama instance.
- **Verification Method:** Run container build in CI pipeline and execute automated health probe.

---

#### P3-2: Token Streaming via Server-Sent Events (SSE) for Q&A
- **Reason:** Reduces perceived latency during follow-up conversational answers by streaming tokens in real-time.
- **Affected Modules:** `src/notice2action/api/server.py`, `frontend/src/services/apiClient.ts`, `frontend/src/components/GroundedQAChat.tsx`.
- **Dependencies:** FastAPI `EventSourceResponse` / SSE.
- **Acceptance Criteria:**
  - `/api/followup/stream` streams JSON or token deltas as they are generated by the LLM.
- **Verification Method:** Playwright browser test verifying incremental text rendering in the chat bubble.
