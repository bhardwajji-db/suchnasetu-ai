# SuchnaSetu AI — REST API Specification

**Project:** SuchnaSetu AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Date:** October 20, 2026  
**Auditor / Engineer:** Senior Full-Stack Engineer, AI Architect & QA Automation Specialist  
**Repository Directory:** `.`  
**Base URL:** `http://127.0.0.1:8000`  
**API Version:** `2.0.0`  

---

## 1. Overview & Conventions

The SuchnaSetu AI REST API is built on FastAPI and exposes all backend document ingestion, multi-engine OCR, multi-provider LLM extraction, evidence indexing, session management, and export services.

### General Conventions
- All request and response bodies use JSON (`application/json`) unless handling file uploads (`multipart/form-data`) or exports (`text/markdown`, `text/calendar`, `audio/mpeg`).
- CORS is enabled for local Vite development origins (`http://localhost:5173`, `http://127.0.0.1:5173`).
- Pydantic v2 schemas enforce strict data validation on every endpoint.
- Errors follow standard HTTP status codes with structured `{ "detail": "message", "error_type": "..." }` payloads.

---

## 2. Endpoints Reference

### 2.1 System Health & Diagnostics

#### `GET /api/health`
Runs preflight system checks on Python runtime, Tesseract OCR executable, configured LLM provider, and session store.

**Response:** `200 OK`
```json
{
  "overall_status": "ok",
  "active_provider": "ollama",
  "model_name": "gemma4:latest",
  "is_ready_for_inference": true,
  "items": [
    {
      "name": "Python Runtime",
      "status": "ok",
      "details": "Python 3.11.15",
      "remedy": null
    },
    {
      "name": "Tesseract OCR",
      "status": "ok",
      "details": "tesseract v5.4.0.20240606 at C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
      "remedy": null
    },
    {
      "name": "Configured LLM Provider",
      "status": "ok",
      "details": "Active provider: 'ollama'",
      "remedy": null
    },
    {
      "name": "Ollama Server",
      "status": "ok",
      "details": "Connected to http://127.0.0.1:11434. Found 9 model(s).",
      "remedy": null
    }
  ]
}
```

---

### 2.2 LLM Provider Management

#### `GET /api/providers`
Returns configuration, model name, and API key readiness status for all supported providers (`ollama`, `openrouter`, `gemini`, `huggingface`).

**Response:** `200 OK`
```json
[
  {
    "id": "ollama",
    "name": "Ollama (Local / Offline)",
    "is_active": true,
    "is_local": true,
    "requires_api_key": false,
    "model": "gemma4:latest",
    "endpoint": "http://127.0.0.1:11434",
    "key_configured": true
  },
  {
    "id": "openrouter",
    "name": "OpenRouter (Cloud Router)",
    "is_active": false,
    "is_local": false,
    "requires_api_key": true,
    "model": "google/gemma-2-9b-it:free",
    "endpoint": "https://openrouter.ai/api/v1",
    "key_configured": false
  }
]
```

#### `POST /api/providers/select`
Selects the active LLM provider for subsequent inference operations.

**Request Body:**
```json
{
  "provider": "ollama"
}
```

**Response:** `200 OK`
```json
{
  "active_provider": "ollama",
  "status": {
    "provider": "ollama",
    "connected": true,
    "has_target_model": true,
    "target_model": "gemma4:latest"
  }
}
```

---

### 2.3 Evidence Service & Session Store

#### `POST /api/evidence/search`
Searches indexed notice segments for verbatim quotations matching a user query with relevance scoring.

**Request Body:**
```json
{
  "query": "Where do I submit documents?",
  "notice_text": "Notice:\nLine 1: Announcement.\nLine 2: Submit all documents at Counter #4 before Nov 14.",
  "max_results": 3
}
```

**Response:** `200 OK`
```json
[
  {
    "line_number": 3,
    "quote": "Line 2: Submit all documents at Counter #4 before Nov 14.",
    "relevance_score": 1.0
  }
]
```

#### `GET /api/session/{session_id}`
Retrieves persisted session state, user confirmations, and Q&A conversation history.

---

### 2.4 Document Ingestion & OCR

#### `POST /api/ingest/text`
Sanitizes pasted notice text, filters injection attacks, and indexes lines in `EvidenceService`.

#### `POST /api/ocr`
Executes optical character recognition using the configured engine (`tesseract` or `rapidocr`).

**Form Data:**
- `file`: Scanned document image (`.png`, `.jpg`, `.jpeg`, `.webp`)
- `target_lang`: Language code (`eng`, `hin`, or `eng+hin`)
- `enhance_contrast`: Boolean (`true` or `false`)
- `engine`: Optional engine override (`tesseract` or `rapidocr`)

**Response:** `200 OK`
```json
{
  "extracted_text": "OFFICIAL NOTICE...",
  "confidence_score": 88.4,
  "languages_used": "eng",
  "line_count": 24,
  "char_count": 1420,
  "is_preprocessed": true,
  "engine_used": "tesseract",
  "is_uncertain": false,
  "fingerprint": "a3b8..."
}
```

---

### 2.5 Structured Notice Analysis

#### `POST /api/analyze`
Executes structured notice extraction via the active LLM, returning the Six Core Fields, procedural dimensions, plain-language summaries (English & Hindi), and sequential action checklists.

**Request Body:**
```json
{
  "notice_text": "Notice text to analyze...",
  "target_language": "en",
  "reading_level": "standard",
  "session_id": null,
  "provider": null
}
```

**Response:** `200 OK`
```json
{
  "session_id": "c1f7a0b3-9821-4f32-84de-d68a2bf5c290",
  "six_core_fields": {
    "issuing_authority": {
      "field_name": "issuing_authority",
      "value": "Metropolitan Technical University",
      "status": "stated",
      "evidence_quote": "METROPOLITAN TECHNICAL UNIVERSITY (MTU)"
    },
    "notice_reference_number": {
      "field_name": "notice_reference_number",
      "value": "MTU/COMP/2026/8941",
      "status": "stated",
      "evidence_quote": "Ref No: MTU/COMP/2026/8941"
    },
    "notice_date": {
      "field_name": "notice_date",
      "value": "October 12, 2026",
      "status": "stated",
      "evidence_quote": "Date of Issuance: October 12, 2026"
    },
    "recipient": {
      "field_name": "recipient",
      "value": "All Final-Year Degree Candidates (Batch of 2026)",
      "status": "stated",
      "evidence_quote": "To: All Final-Year Degree Candidates (Batch of 2026)"
    },
    "main_subject": {
      "field_name": "main_subject",
      "value": "Deficient Enrollment Dossiers and Submission of Pending Certificates",
      "status": "stated",
      "evidence_quote": "Subject: Deficient Enrollment Dossiers and Submission of Pending Certificates"
    },
    "required_action_and_deadline": {
      "field_name": "required_action_and_deadline",
      "value": "Submit deficient documents by November 14, 2026 (5:00 PM IST)",
      "status": "stated",
      "evidence_quote": "DEADLINE: November 14, 2026 (5:00 PM IST)."
    }
  },
  "structured_notice": { ... },
  "summary_en": { ... },
  "summary_hi": { ... },
  "checklist_en": { ... },
  "checklist_hi": { ... },
  "fingerprint": "...",
  "duration_seconds": 4.12
}
```

---

### 2.6 Field Confirmation & Correction

#### `POST /api/confirm`
Allows human-in-the-loop verification or correction of any uncertain field, instantly updating downstream summaries and action checklists while preserving original extraction proof.

---

### 2.7 Evidence-Grounded Q&A

#### `POST /api/followup`
Answers follow-up questions strictly grounded within the active notice text. If information is absent, returns `"This information was not found in the provided notice."`

**Request Body:**
```json
{
  "question": "Is late submission allowed?",
  "notice_text": "Notice text...",
  "session_id": "c1f7a0b3-9821-4f32-84de-d68a2bf5c290",
  "target_language": "en"
}
```

**Response:** `200 OK`
```json
{
  "question": "Is late submission allowed?",
  "answer": "This information was not found in the provided notice. The notice does not specify this detail.",
  "is_supported": false,
  "evidence_quote": null,
  "unsupported_message": "Late submission policy is not specified."
}
```

---

### 2.8 Export Endpoints

- `POST /api/export/markdown`: Formatted Markdown action plan report.
- `POST /api/export/ics`: RFC 5545 iCalendar (`.ics`) file.
- `POST /api/tts`: Audio read-aloud via gTTS (`audio/mpeg`).
