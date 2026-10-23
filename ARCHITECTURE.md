# SuchnaSetu AI — System Architecture & Design Specification

**Project:** SuchnaSetu AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Date:** October 20, 2026  
**Auditor / Engineer:** Senior Full-Stack Engineer, AI Architect & QA Automation Specialist  
**Repository Directory:** `.`  
**Classification:** PUBLIC / COMPETITION-READY  

---

## 1. System Overview & Philosophy

SuchnaSetu AI addresses the accessibility gap in formal administrative communications. Bureaucratic circulars, scholarship announcements, exam schedules, and municipal advisories are frequently dense, legalistic, multi-column, or distributed as low-resolution scanned notices.

The system is designed with four foundational principles:
1. **Air-Gapped Local Privacy First:** Zero sensitive data leaves the host machine by default. Local Ollama (`gemma4:latest`) and local Tesseract OCR v5.4.0 provide 100% on-device operation.
2. **Modular Multi-Provider Extensibility:** A clean, unified LLM adapter interface supports optional cloud providers (OpenRouter, Google Gemini, Hugging Face) via user-configured environment variables, with strict credential protection and zero hardcoded secrets.
3. **Deterministic Evidence Grounding:** All extracted facts cite verbatim quotations with line numbers. The Six Core Notice Fields are strictly verified, and missing information is explicitly tagged rather than hallucinated.
4. **Isolated Session Management & Evidence Indexing:** Dedicated `EvidenceService` segments text into line-numbered units, and thread-safe `SessionStore` isolates conversation and analysis state without cross-session leakage.

---

## 2. System Architecture & Component Map

```
+-----------------------------------------------------------------------------------------+
|                                      HOST MACHINE                                       |
|                                                                                         |
|  +------------------------------------------------------------------------------------+ |
|  |                 React 19 + TypeScript + Vite Frontend                              | |
|  |                 (Port 5173 - Modern Accessible Dashboard)                          | |
|  +------------------------------------------+-----------------------------------------+ |
|                                             |                                           |
|                                             | REST / JSON                               |
|                                             v                                           |
|  +------------------------------------------------------------------------------------+ |
|  |                         FastAPI ASGI REST Backend Layer                            | |
|  |                         (Port 8000 - server.py)                                    | |
|  |                                                                                    | |
|  |  [ Evidence Service ]    [ Session Store ]    [ OCR Engine Manager (Tess/Rapid) ]  | |
|  |  Stores & indexes        Isolates session     Adaptive preprocessing,              | |
|  |  line-level quotes       state on disk/RAM    word-level confidence                | |
|  +------------------------------------+-----------------------------------------------+ |
|                                       |                                                 |
|                                       v                                                 |
|  +------------------------------------------------------------------------------------+ |
|  |                     Modular Multi-Provider LLM Integration Layer                   | |
|  |                                                                                    | |
|  |  +----------------------+  +---------------------+  +----------------------------+ | |
|  |  | Ollama (Local)       |  | OpenRouter (Cloud)  |  | Google Gemini (Cloud)      | | |
|  |  | gemma4:latest        |  | OpenAI compatible   |  | REST API v1beta            | | |
|  |  +----------------------+  +---------------------+  +----------------------------+ | |
|  |  +-----------------------------------------------+                               | |
|  |  | Hugging Face Inference Router (Cloud)        |                               | |
|  |  +-----------------------------------------------+                               | |
|  +------------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------------+
```

### Component Network Map

| Component | Technology | Network Address | Primary Role |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4 | `http://127.0.0.1:5173/` | Modern accessible dashboard with language & provider selectors |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | `http://127.0.0.1:8000/` | REST API, validation, session storage, evidence indexing |
| **Evidence Service** | Python 3.11, Pydantic | In-Memory / Indexed | Line-level text segmenting, verbatim quote verification |
| **Session Store** | Python 3.11, Thread-safe JSON | Local Disk / Memory | Session isolation, conversation history, user confirmations |
| **Local LLM** | Ollama Daemon (`gemma4:latest`) | `http://127.0.0.1:11434/` | 100% on-device generative reasoning (default) |
| **Cloud LLMs** | OpenRouter, Gemini, Hugging Face | Secure Outbound HTTPS | Optional cloud inference when credentials are provided |
| **Vision / OCR** | Tesseract OCR v5.4.0 (Default) / RapidOCR | System Executable / ONNX | Local optical character recognition & layout preservation |

---

## 3. Data Model: Six Core Notice Fields

Every analyzed notice is structured into the **Six Core Legal Fields** alongside procedural dimensions:

1. **`issuing_authority`**: Department, university, or municipal authority issuing the circular.
2. **`notice_reference_number`**: Official serial or file reference identifier (e.g. `MTU/COMP/2026/8941`).
3. **`notice_date`**: Exact statutory date of issuance.
4. **`recipient`**: Target group, affected individuals, or concerned public.
5. **`main_subject`**: Core allegation, administrative purpose, or regulatory mandate.
6. **`required_action_and_deadline`**: Mandatory compliance action paired with its strict cutoff date/time.

Each field is modeled as an `ExtractedFact` containing:
- `value`: Extracted textual value or `"Not stated in the notice."`
- `status`: `stated`, `not_stated`, `uncertain`, `conflicting`, `unreadable`
- `evidence_quote`: Exact verbatim quotation from the document
- `source_location`: Line number or section citation
- `requires_confirmation`: Flagged when ambiguous, tentative, or low confidence
- `uncertainty_type`: `"ocr_quality"`, `"document_ambiguity"`, `"missing_in_text"`, `"conflict"`
- `user_confirmed`: True once verified or corrected by the user
- `confirmed_value`: User-supplied override preserving original extracted ground truth

---

## 4. OCR Engine Comparison: Tesseract vs RapidOCR

| Criteria | Tesseract OCR (Default) | RapidOCR (Optional Adapter) |
| :--- | :--- | :--- |
| **Maturity & Stability** | Industry standard, UB-Mannheim v5.4.0 binary | Modern PaddleOCR port |
| **Installation Requirements** | Local binary executable in system PATH | Python package (`rapidocr-onnxruntime`), ONNX Runtime, visual C++ runtimes |
| **Image Preprocessing** | Custom PIL pipeline: Lanczos DPI scaling, auto-contrast, edge sharpening | Internal preprocessing in ONNX pipeline |
| **Confidence Scoring** | Word-level confidence extraction via `image_to_data` | Box-level detection score |
| **Language Support** | Extensive traineddata packs (`eng`, `hin`, `osd`) | Language-specific ONNX models |
| **System Recommendation** | **Selected as Primary Default** (zero external cloud dependencies, pre-installed, rock-solid) | Supported as optional plugin adapter via `OCR_ENGINE=rapidocr` |

---

## 5. Security & Privacy Model

- **Zero Secret Ingestion:** API keys are never stored in the database, codebase, or logs. All credentials are read from environment variables or `.env` (strictly ignored by `.gitignore`).
- **Data Boundary Control:** Notices are never transmitted to cloud providers unless the user explicitly switches the provider in the UI and sets the corresponding API key.
- **Prompt Injection Defense:** Untrusted notice documents are encapsulated in XML tags (`<notice_document_data>`) and explicitly treated as inert data, never instructions.
- **Session Isolation:** Analysis state and Q&A history are keyed to isolated session IDs, preventing cross-tenant data leakage.
