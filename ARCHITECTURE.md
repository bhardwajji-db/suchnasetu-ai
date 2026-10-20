# Notice2Action AI — System Architecture & Design Specification

**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Date:** October 20, 2026  
**Auditor / Engineer:** Senior Full-Stack Engineer, QA Automation & Local AI Specialist  
**Repository Directory:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Classification:** PUBLIC / COMPETITION-READY  

---

## 1. System Overview & Philosophy

Notice2Action AI addresses the accessibility gap in formal administrative communications. Bureaucratic circulars, scholarship announcements, exam schedules, and municipal advisories are frequently dense, legalistic, multi-column, or distributed as low-resolution scanned notices.

The system is designed with four foundational principles:
1. **100% Local & Air-Gapped Privacy:** Zero sensitive data leaves the host machine. All AI inference runs through local Ollama (`gemma4:latest`) and local Tesseract OCR v5.4.0. No third-party cloud LLMs or telemetry.
2. **Deterministic Evidence Grounding:** Extracted facts are strictly grounded in verbatim quotations from the source document. Missing information is explicitly tagged as `Not stated in the notice.` rather than hallucinated.
3. **Interactive Accessibility:** Provides dual-language support (English and Hindi), adjustable reading levels (Simple Grade 5, Standard Grade 8, Detailed), read-aloud TTS capabilities, and interactive sequential checklists.
4. **State Integrity & Cryptographic Validation:** Notice text modifications post-analysis are immediately flagged via SHA-256 digest mismatches, preventing stale data and hallucinated actions.

---

## 2. System Architecture & Topology

```
+-----------------------------------------------------------------------------------+
|                                  HOST MACHINE                                     |
|                                                                                   |
|  +-------------------------------------+   +------------------------------------+ |
|  |     React 19 + Vite Frontend        |   |    Legacy Streamlit Application    | |
|  |     (Port 5173 - User Interface)    |   |    (Port 8501 - Backward Compat)   | |
|  +------------------+------------------+   +-----------------+------------------+ |
|                     |                                        |                    |
|                     | REST / JSON                            | Direct Python SDK  |
|                     v                                        v                    |
|  +------------------------------------------------------------------------------+ |
|  |                       FastAPI ASGI REST Backend Layer                        | |
|  |                       (Port 8000 - server.py)                                | |
|  +------------------------------------------------------------------------------+ |
|                     |                                        |                    |
|                     | Internal Service Calls                 | Subprocess / C-API |
|                     v                                        v                    |
|  +------------------------------------+    +------------------------------------+ |
|  |        Local Ollama Daemon         |    |        Tesseract OCR Engine        | |
|  |   (Port 11434 - gemma4:latest)     |    |   (System Executable v5.4.0)       | |
|  +------------------------------------+    +------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

### Component Network Map

| Component | Technology | Network Address | Primary Role |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite 6, Tailwind CSS v4 | `http://127.0.0.1:5173/` | Competition-ready dashboard, multi-viewport UI |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | `http://127.0.0.1:8000/` | REST API, validation, export orchestration |
| **Local LLM** | Ollama Daemon (`gemma4:latest`) | `http://127.0.0.1:11434/` | 100% on-device generative reasoning |
| **Vision / OCR** | Tesseract OCR v5.4.0 | System Binary | Local optical character recognition |
| **Legacy UI** | Streamlit 1.66.0 | `http://localhost:8501/` | Maintained for backward compatibility |

---

## 3. Five-Phase Processing Pipeline

```
[ Notice Input: Image / Text ]
              |
              v
+-------------------------------+
|  PHASE 1: Ingestion & Safety  |  --> Sanitization, Prompt Injection Filter,
+---------------+---------------+      File Whitelist & 10MB Ceiling
                |
                v
+-------------------------------+
|    PHASE 2: Tesseract OCR     |  --> Adaptive Grayscale, Contrast Autostretch,
+---------------+---------------+      Sharpening & Line Extraction
                |
                v
+-------------------------------+
|    PHASE 3: Local LLM         |  --> Multi-phase extraction via Gemma 4,
+---------------+---------------+      Strict Pydantic JSON Schema Parsing
                |
                v
+-------------------------------+
| PHASE 4: Grounding & Defense  |  --> Verbatim quote citation, Certainty tagging
+---------------+---------------+      (Stated, Not Stated, Uncertain, Conflicting)
                |
                v
+-------------------------------+
| PHASE 5: Synthesis & Exports  |  --> 7-Question Plain Summary, Sequential Action
+-------------------------------+      Checklist, .ics Calendar & .md Reports
```

### Phase 1: Ingestion & Security Validation
- Sanitizes incoming text against known prompt-injection patterns (`IGNORE PREVIOUS`, `SYSTEM PROMPT OVERRIDE`, etc.).
- Verifies uploaded files against extension whitelist (`.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`) and 10MB size ceiling.
- Generates SHA-256 fingerprint for data integrity tracking.

### Phase 2: Local Optical Character Recognition
- Applies adaptive PIL image preprocessing: grayscale conversion, Lanczos resolution enhancement, autocontrast stretching, and subtle edge sharpening.
- Dispatches image to local Tesseract OCR engine, extracting text with line preservation and overall confidence scoring.

### Phase 3: Structured Extraction via Local Gemma 4
- Formulates strict prompts demanding discrete JSON facts across 8 semantic dimensions.
- Applies resilient parsing regex and Pydantic v2 validation models, safely handling string lists, nested dictionaries, and malformed LLM outputs.

### Phase 4: Grounding & Hallucination Defense
- Verifies that every extracted fact is accompanied by verbatim quotes from the source notice.
- Fields not present in the notice are explicitly tagged with `CertaintyStatus.NOT_STATED` and value `"Not stated in the notice."`.
- Ambiguous dates or tentative fees are flagged with `requires_confirmation = True`.

### Phase 5: Accessible Synthesis & Exports
- Produces plain-language answers to the 7 core questions:
  1. *What is this notice about?*
  2. *Who is eligible?*
  3. *What must the reader do?*
  4. *What documents are needed?*
  5. *What is the deadline?*
  6. *Where can the reader get help?*
  7. *What critical information is missing?*
- Produces sequential, prioritized action checklists with interactive checkboxes.
- Exports formatted Markdown (`.md`) action reports and RFC 5545 iCalendar (`.ics`) schedules with alarms.

---

## 4. Key Architectural Subsystems

### 4.1 Cryptographic Notice Buffer & Stale State Tracking
Whenever notice text is analyzed, the backend and frontend compute a SHA-256 fingerprint of the normalized text. If a user modifies the notice buffer post-analysis, the Web Crypto API detects `currentFingerprint !== analyzedFingerprint` and renders an amber warning banner across all tabs, prompting re-analysis.

### 4.2 Uncertain-Field Confirmation Workflow
When a critical detail is ambiguous, tentative, or conflicting:
1. The fact is flagged with `requires_confirmation = True`.
2. The user can review the original extracted value, verbatim evidence quote, and reason in `ConfirmationModal`.
3. The user can confirm the value as-is or supply a corrected value.
4. The system stores the user's verified value in `confirmed_value` while preserving the original extracted value in `value`.
5. Downstream summaries and action checklists immediately synchronize with the verified value.
6. Confirmations are strictly isolated to the active notice session.

### 4.3 Multilingual & Reading-Level Adaptation
- **Bilingual Interface & Outputs:** Full English and Devanagari Hindi support for plain summaries and action checklists, while preserving official numbers, dates, reference codes, and verbatim quotes.
- **Reading-Level Selector:** Calibrates explanations across three levels:
  - *Simple (Grade 5):* Short, bulleted words, zero legalistic vocabulary.
  - *Standard (Grade 8):* Clear, concise institutional explanations answering the 7 questions.
  - *Detailed:* Complete descriptive breakdown with administrative nuances.

### 4.4 Original Notice Viewer
A dedicated slide-over viewer modal accessible from any view allows users to cross-reference extracted facts against the verbatim source notice text and uploaded image scan, complete with search filtering and copy actions.

---

## 5. Security Architecture & Threat Model

| Threat | Mitigation Mechanism |
| :--- | :--- |
| **Prompt Injection** | Regex pattern matching + Pydantic v2 strict schema enforcement. Notice text treated as untrusted data, never as executable instructions. |
| **Path Traversal** | Sample filename sanitation using `Path(filename).name` restricted strictly within `tests/fixtures/`. |
| **Malicious Uploads** | Strict MIME and extension whitelist (`.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`). Strict 10MB payload ceiling. |
| **Data Residue** | Temporary files written via `NamedTemporaryFile` with guaranteed `try...finally` unlinking immediately after OCR. |
| **External Leakage** | All inference constrained to `http://127.0.0.1:11434` and local system binaries. Zero external API keys or cloud dependencies. |
