# Notice2Action AI — REST API Specification

**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Date:** October 20, 2026  
**Auditor / Engineer:** Senior Full-Stack Engineer, QA Automation & Local AI Specialist  
**Repository Directory:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Base URL:** `http://127.0.0.1:8000`  
**API Version:** `1.0.0`  

---

## 1. Overview & Conventions

The Notice2Action AI REST API is built on FastAPI and exposes all backend document ingestion, optical character recognition, local LLM extraction, confirmation workflows, and export services.

### General Conventions
- All request and response bodies use JSON (`application/json`) unless handling file uploads (`multipart/form-data`) or exports (`text/markdown`, `text/calendar`, `audio/mpeg`).
- CORS is enabled for local Vite development origins (`http://localhost:5173`, `http://127.0.0.1:5173`).
- Pydantic v2 schemas enforce strict data validation on every endpoint.
- Errors follow standard HTTP status codes with structured `{ "detail": "message" }` payloads.

---

## 2. Endpoints Reference

### 2.1 System Health & Diagnostics

#### `GET /api/health`
Runs preflight system checks on Python runtime, Tesseract OCR executable, and local Ollama daemon.

**Response:** `200 OK`
```json
{
  "overall_status": "ok",
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
      "name": "Ollama Server",
      "status": "ok",
      "details": "Connected to http://127.0.0.1:11434. Found 9 model(s).",
      "remedy": null
    },
    {
      "name": "LLM Model (gemma4:latest)",
      "status": "ok",
      "details": "Model 'gemma4:latest' is downloaded and ready in Ollama.",
      "remedy": null
    }
  ]
}
```

---

### 2.2 Synthetic Demo Notices

#### `GET /api/samples`
Returns the list of available synthetic demo notices for testing and demonstration.

**Response:** `200 OK`
```json
[
  {
    "id": "demo_scholarship_ambiguous.txt",
    "title": "🎓 Demo A: Scholarship (Ambiguous Deadline)",
    "type": "text",
    "language": "en"
  },
  {
    "id": "demo_campus_placement.txt",
    "title": "💼 Demo B: Campus Placement (CGPA & NOC)",
    "type": "text",
    "language": "en"
  },
  {
    "id": "demo_municipal_water_advisory.txt",
    "title": "🚰 Demo C: Municipal Water Advisory (Zero-Hallucination)",
    "type": "text",
    "language": "en"
  },
  {
    "id": "synthetic_scholarship_notice.txt",
    "title": "🎯 Competition Demo (TEST-SCH-2026-001)",
    "type": "text",
    "language": "en"
  }
]
```

#### `GET /api/samples/{filename}`
Retrieves content of a specific demo notice fixture. Protected against directory traversal.

**Parameters:** `filename` (string, path parameter)  
**Responses:**
- `200 OK`: JSON `{ "filename": "...", "content": "...", "fingerprint": "..." }` or raw image bytes (`image/png`).
- `404 Not Found`: Fixture does not exist.

---

### 2.3 Notice Ingestion & OCR

#### `POST /api/ingest/text`
Sanitizes pasted notice text, checks for prompt injection, and computes its SHA-256 fingerprint.

**Request Body:**
```json
{
  "text": "GOVERNMENT SCHOLARSHIP NOTIFICATION..."
}
```

**Response:** `200 OK`
```json
{
  "raw_text": "GOVERNMENT SCHOLARSHIP NOTIFICATION...",
  "char_count": 850,
  "line_count": 28,
  "security_warning": null,
  "fingerprint": "a3f2b4c8..."
}
```

#### `POST /api/ingest/upload`
Uploads and validates a notice file (`.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`). Enforces 10MB limit.

**Content-Type:** `multipart/form-data`  
**Parameters:** `file` (UploadFile)  
**Response:** `200 OK` with source metadata (`"source_type": "text"` or `"source_type": "image"`).

#### `POST /api/ocr`
Executes local Tesseract OCR on an uploaded image with adaptive contrast preprocessing.

**Content-Type:** `multipart/form-data`  
**Parameters:**
- `file` (UploadFile, required)
- `target_lang` (string, optional, default `"eng"`)
- `enhance_contrast` (boolean, optional, default `true`)

**Response:** `200 OK`
```json
{
  "extracted_text": "Extracted text content...",
  "confidence_score": 93.4,
  "languages_used": "eng",
  "line_count": 22,
  "char_count": 680,
  "is_preprocessed": true,
  "warning": null,
  "error": null,
  "fingerprint": "b7d1e8..."
}
```

---

### 2.4 Analysis, Confirmation & Reading Level

#### `POST /api/analyze`
Executes the full 5-phase extraction pipeline using local Gemma 4 inference and Pydantic validation.

**Request Body:**
```json
{
  "notice_text": "Official notice text...",
  "target_language": "en",
  "reading_level": "standard"
}
```

**Response:** `200 OK`
```json
{
  "structured_notice": {
    "purpose": { "field_name": "purpose", "value": "...", "status": "stated", "evidence_quote": "..." },
    "eligibility": { "field_name": "eligibility", "value": "...", "status": "stated" },
    "deadline": { "field_name": "deadline", "value": "31 October 2026", "status": "stated" },
    "fee_or_cost": { "field_name": "fee_or_cost", "value": "No fee", "status": "stated" },
    "required_documents": { "field_name": "required_documents", "value": "...", "status": "stated" },
    "contact_details": { "field_name": "contact_details", "value": "...", "status": "stated" },
    "required_actions": { "field_name": "required_actions", "value": "...", "status": "stated" },
    "important_conditions": { "field_name": "important_conditions", "value": "...", "status": "stated" },
    "missing_information": [],
    "uncertain_or_conflicting_details": []
  },
  "summary_en": {
    "about": "...",
    "eligible": "...",
    "actions": "...",
    "documents": "...",
    "deadline": "...",
    "help_contact": "...",
    "missing": "..."
  },
  "summary_hi": { ... },
  "checklist_en": {
    "items": [
      {
        "step_number": 1,
        "action": "...",
        "category": "eligibility",
        "is_mandatory": true,
        "is_completed": false
      }
    ]
  },
  "checklist_hi": { ... },
  "fingerprint": "...",
  "duration_seconds": 18.42
}
```

#### `POST /api/confirm`
Saves user verification or correction for an uncertain fact and synchronizes dependent summaries and checklists without overwriting the original ground-truth extraction.

**Request Body:**
```json
{
  "field_name": "deadline",
  "confirmed_value": "15 November 2026",
  "structured_notice": { ... },
  "reading_level": "standard"
}
```

**Response:** `200 OK` with updated `structured_notice` (`confirmed_value` set, `user_confirmed: true`), refreshed `summary_en`, `summary_hi`, `checklist_en`, `checklist_hi`.

#### `POST /api/summary/reading-level`
Generates plain-language summary calibrated to requested reading level (`simple`, `standard`, `detailed`).

**Request Body:**
```json
{
  "structured_notice": { ... },
  "reading_level": "simple"
}
```

**Response:** `200 OK` with `summary_en` and `summary_hi` at the requested reading level.

---

### 2.5 Follow-Up Q&A

#### `POST /api/followup`
Answers follow-up questions grounded strictly within the active notice text. Refuses out-of-scope inquiries.

**Request Body:**
```json
{
  "question": "What is the application deadline?",
  "notice_text": "Official notice text..."
}
```

**Response:** `200 OK`
```json
{
  "question": "What is the application deadline?",
  "answer": "The final deadline for online registration is 31 October 2026.",
  "is_supported": true,
  "evidence_quote": "Closing date for online registration is 31 October 2026.",
  "unsupported_message": null
}
```

---

### 2.6 Export Endpoints

#### `POST /api/export/markdown`
Generates a downloadable Markdown action report.  
**Content-Type:** `text/markdown` (`attachment; filename="notice2action_plan.md"`)

#### `POST /api/export/ics`
Generates an RFC 5545 iCalendar schedule with alarm notifications.  
**Content-Type:** `text/calendar` (`attachment; filename="notice_deadline.ics"`)

#### `POST /api/tts`
Synthesizes MP3 audio for text read-aloud via gTTS.  
**Content-Type:** `audio/mpeg` (or `204 No Content` if offline).
