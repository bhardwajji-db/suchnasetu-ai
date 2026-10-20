# Notice2Action AI — API Inventory & External Integration Registry

**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Host Application:** FastAPI Backend Server (`src/notice2action/api/server.py`)  
**Base URL:** `http://127.0.0.1:8000`  
**Date of Audit:** October 20, 2026  
**Status:** FULLY DOCUMENTED & VERIFIED  

---

## 1. Overview & Security Architecture

The Notice2Action AI backend exposes a RESTful API designed with strict input validation via Pydantic v2 schemas, granular error handling, line-level evidence grounding, and session isolation.

### Key Security Principles:
1. **Zero Secret Exposure:** Credentials are never returned in endpoint responses or written to logs. API keys are loaded strictly from the process environment (`.env`).
2. **Session Isolation:** All session mutations and queries are isolated in `.sessions/{session_id}.json` using re-entrant thread locks (`threading.RLock`).
3. **Prompt Injection Protection:** Untrusted text inputs are wrapped in boundary markers (`<<<UNTRUSTED_NOTICE>>>`) and sanitized against prompt-override sequences.
4. **Path Traversal Protection:** File access is restricted to whitelisted safe directories (`tests/fixtures/`, `assets/`, `.sessions/`) using canonical path resolution (`resolve()`).

---

## 2. Comprehensive Endpoint Registry

### Group A: System Health & Provider Management

#### 1. `GET /api/health`
- **Purpose:** Executes live preflight diagnostics across Python runtime, Tesseract OCR, configured LLM provider, and Ollama server.
- **Authentication:** None (Public diagnostic endpoint).
- **Request Parameters:** None.
- **Response Format (200 OK):**
  ```json
  {
    "overall_status": "ok",
    "active_provider": "ollama",
    "model_name": "gemma4:latest",
    "is_ready_for_inference": true,
    "items": [
      { "name": "Python Runtime", "status": "ok", "details": "Python 3.11.15...", "remedy": "" },
      { "name": "Tesseract OCR", "status": "ok", "details": "tesseract v5.4.0.20240606...", "remedy": "" },
      { "name": "Configured LLM Provider", "status": "ok", "details": "Active provider: 'ollama'", "remedy": "" },
      { "name": "Ollama Server", "status": "ok", "details": "Connected to http://127.0.0.1:11434. Found 9 model(s).", "remedy": "" }
    ]
  }
  ```
- **Error Responses:** None (Graceful degradation; diagnostic failures are captured inside individual items with `status: "error"` and remedial advice).
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_health_endpoint` and live curl).

---

#### 2. `GET /api/providers`
- **Purpose:** Lists all four supported LLM providers with their current configuration status, local/cloud designation, and credential readiness.
- **Authentication:** None.
- **Request Parameters:** None.
- **Response Format (200 OK):**
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
    },
    {
      "id": "gemini",
      "name": "Google Gemini (Cloud)",
      "is_active": false,
      "is_local": false,
      "requires_api_key": true,
      "model": "gemini-1.5-flash",
      "endpoint": "https://generativelanguage.googleapis.com",
      "key_configured": false
    },
    {
      "id": "huggingface",
      "name": "Hugging Face Inference (Cloud)",
      "is_active": false,
      "is_local": false,
      "requires_api_key": true,
      "model": "google/gemma-2-9b-it",
      "endpoint": "https://router.huggingface.co/hf-inference/v1",
      "key_configured": false
    }
  ]
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_providers_endpoints` and live curl).

---

#### 3. `POST /api/providers/select`
- **Purpose:** Switches the active runtime LLM provider for subsequent inference requests.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "provider_id": "openrouter"
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "status": "success",
    "active_provider": "openrouter",
    "provider_name": "OpenRouter (Cloud Router)",
    "model": "google/gemma-2-9b-it:free"
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: When `provider_id` is unrecognized or invalid.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_providers_endpoints`).

---

### Group B: Sample Notices & Document Ingestion

#### 4. `GET /api/samples`
- **Purpose:** Enumerates all pre-installed fictional demo notices and benchmark fixtures.
- **Authentication:** None.
- **Response Format (200 OK):**
  ```json
  [
    { "id": "sample_scholarship_notice.txt", "name": "Merit Scholarship Notice (English)" },
    { "id": "sample_hindi_notice.txt", "name": "Water Pipeline Notice (Hindi)" },
    { "id": "sample_court_summons.txt", "name": "District Court Summons" },
    { "id": "sample_electricity_disconnection.txt", "name": "Electricity Disconnection Demand" },
    { "id": "sample_tax_assessment.txt", "name": "Income Tax Assessment Notice" },
    { "id": "demo_missing_compliance.txt", "name": "Demo 1: Compliance Notice (Missing Proof)" },
    { "id": "demo_outstanding_dues.txt", "name": "Demo 2: Outstanding Dues Notice" },
    { "id": "demo_response_hearing.txt", "name": "Demo 3: Administrative Hearing Notice" }
  ]
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_samples_list`).

---

#### 5. `GET /api/samples/{filename}`
- **Purpose:** Retrieves the verbatim text of a demo fixture.
- **Authentication:** None.
- **Path Parameter:** `filename` (e.g., `demo_missing_compliance.txt`).
- **Security Check:** Validates against path traversal using `Path(filename).name` and directory boundary checking.
- **Response Format (200 OK):**
  ```json
  {
    "filename": "demo_missing_compliance.txt",
    "content": "DELHI POLLUTION CONTROL COMMITTEE...\n..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Attempted path traversal (e.g. `../../etc/passwd`).
  - `404 Not Found`: Sample file does not exist.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_samples_get_content` and `test_api_samples_path_traversal_protection`).

---

#### 6. `POST /api/ingest/text`
- **Purpose:** Ingests raw text, validates length/content, indexes lines into `EvidenceService`, and returns a deterministic SHA-256 fingerprint.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "text": "Full text of notice..."
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "sanitized_text": "Full text of notice...",
    "fingerprint": "a3b890f4...",
    "char_count": 1284,
    "line_count": 38,
    "session_id": "d14f9c0e-45a8-4229-873d-9e1b2f4f2c8d"
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Empty or whitespace-only text string.
  - `413 Payload Too Large`: Text exceeds 500,000 characters.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_ingest_text_valid`).

---

#### 7. `POST /api/ingest/upload`
- **Purpose:** Uploads text files (`.txt`, `.md`) or image documents (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`).
- **Authentication:** None.
- **Request Body (`multipart/form-data`):**
  - `file`: Uploaded file payload (max 25MB).
- **Response Format (200 OK):**
  ```json
  {
    "filename": "scholarship_circular.txt",
    "content_type": "text/plain",
    "size_bytes": 2048,
    "extracted_text": "...",
    "fingerprint": "e7b140...",
    "session_id": "f8a4..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Unsupported file extension, zero-byte file, or corrupt header.
  - `413 Payload Too Large`: Upload exceeds size limit.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_ingest_upload_text_file`).

---

### Group C: OCR & Evidence Services

#### 8. `POST /api/ocr`
- **Purpose:** Runs image preprocessing and text extraction using the active OCR engine (Tesseract default, RapidOCR adapter fallback).
- **Authentication:** None.
- **Request Body (`multipart/form-data`):**
  - `file`: Image file.
  - `engine`: Optional string (`"tesseract"` or `"rapidocr"`, default: `"tesseract"`).
  - `target_lang`: Optional OCR language (`"eng"`, `"hin"`, or `"eng+hin"`, default: `"eng"`).
  - `apply_preprocessing`: Boolean (default: `true`).
- **Response Format (200 OK):**
  ```json
  {
    "extracted_text": "DEPARTMENT OF STUDENT WELFARE...",
    "confidence_score": 91.4,
    "engine_used": "tesseract",
    "target_lang": "eng",
    "preprocessing_applied": true,
    "fingerprint": "b71e84a..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Unreadable or corrupt image data.
  - `500 Internal Server Error`: OCR engine failure.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_ocr_endpoint` and `tests/test_live_gemma4.py::test_live_05_image_ocr_pipeline`).

---

#### 9. `POST /api/evidence/search`
- **Purpose:** Performs line-level grounded evidence search across the notice buffer, returning relevant lines with exact quotes and line numbers.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "query": "deadline to apply",
    "raw_notice_text": "Full notice text...",
    "max_results": 3
  }
  ```
- **Response Format (200 OK):**
  ```json
  [
    {
      "line_number": 29,
      "quote": "- Final submission deadline: 15 November 2026, 5:00 PM IST.",
      "relevance_score": 0.94
    }
  ]
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_evidence_search_endpoint`).

---

#### 10. `GET /api/evidence/{fingerprint}`
- **Purpose:** Retrieves pre-indexed line evidence for a specific notice fingerprint.
- **Authentication:** None.
- **Path Parameter:** `fingerprint` (SHA-256 hash).
- **Response Format (200 OK):** Array of indexed lines with line numbers and hashes.
- **Verification Status:** **PASS**.

---

#### 11. `GET /api/session/{session_id}`
- **Purpose:** Retrieves full isolated session state from the `SessionStore`.
- **Authentication:** None.
- **Path Parameter:** `session_id` (UUID).
- **Response Format (200 OK):**
  ```json
  {
    "session_id": "4b68e982...",
    "created_at": 1792484000.0,
    "last_accessed": 1792484100.0,
    "data": {
      "raw_text": "...",
      "structured_notice": { ... },
      "action_checklist": { ... }
    }
  }
  ```
- **Error Responses:**
  - `404 Not Found`: Session does not exist or has expired.
- **Verification Status:** **PASS** (Tested in `tests/test_services_and_six_fields.py::test_session_store_lifecycle`).

---

### Group D: AI Notice Analysis, Q&A, and Human Confirmation

#### 12. `POST /api/analyze`
- **Purpose:** Executes the full structured analysis pipeline via the active LLM provider. Extracts the Six Core Fields, certainty statuses, evidence quotes, and generates the action checklist and plain summary.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "raw_notice_text": "Full notice text...",
    "target_lang": "en",
    "session_id": "optional-uuid"
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "structured_notice": {
      "notice_type": "Scholarship",
      "purpose": { "value": "Financial aid for students", "status": "STATED", "evidence_quote": "To support meritorious..." },
      "issuing_authority": { "value": "Department of Student Welfare, IIMT University", "status": "STATED", "evidence_quote": "DEPARTMENT OF STUDENT WELFARE..." },
      "notice_reference_number": { "value": "IIMTU/DSW/2026/SCH-042", "status": "STATED", "evidence_quote": "Circular Ref: IIMTU/DSW/2026/SCH-042" },
      "notice_date": { "value": "10 October 2026", "status": "STATED", "evidence_quote": "Date: 10 October 2026" },
      "recipient": { "value": "Undergraduate B.Tech / B.Sc students", "status": "STATED", "evidence_quote": "Applications are invited..." },
      "main_subject": { "value": "Merit-cum-Means Financial Assistance Scholarship", "status": "STATED", "evidence_quote": "NOTICE: MERIT-CUM-MEANS SCHOLARSHIP" },
      "required_action_and_deadline": { "value": "Submit online form and documents by 15 November 2026, 5:00 PM", "status": "STATED", "evidence_quote": "Final submission deadline: 15 November 2026..." },
      "deadline": { "value": "15 November 2026", "status": "STATED", "evidence_quote": "Final submission deadline: 15 November 2026" },
      "eligibility": { "value": "75% CGPA, family income < 5 Lakhs", "status": "STATED", "evidence_quote": "Minimum cumulative score..." },
      "required_documents": { "value": "Mark sheets, Income cert, Aadhar, passbook", "status": "STATED", "evidence_quote": "Applicants must attach..." },
      "fee_or_cost": { "value": "No fee", "status": "STATED", "evidence_quote": "There is NO application fee" },
      "contact_details": { "value": "dsw-helpdesk@iimtu.edu.in", "status": "STATED", "evidence_quote": "Email: dsw-helpdesk@iimtu.edu.in" },
      "consequences_of_inaction": { "value": "Application rejected", "status": "STATED", "evidence_quote": "Incomplete submissions... summarily rejected" },
      "six_core_fields": { ... },
      "fingerprint": "a82c40..."
    },
    "summary": {
      "about": "Merit scholarship assistance...",
      "deadline": "15 November 2026",
      "required_action": "Complete online form...",
      "documents": "Income certificate, mark sheets",
      "cost": "No fee",
      "contact": "dsw-helpdesk@iimtu.edu.in",
      "consequences": "Incomplete submissions rejected"
    },
    "checklist": {
      "items": [
        { "id": "task_1", "action": "Verify eligibility criteria", "deadline": "15 November 2026", "priority": "CRITICAL", "category": "ELIGIBILITY", "evidence_quote": "...", "status": "PENDING" }
      ],
      "overall_status": "ACTION_REQUIRED"
    },
    "session_id": "4b68e982..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Empty or invalid text.
  - `502 Bad Gateway`: Active provider unreachable or offline.
  - `504 Gateway Timeout`: Inference timeout.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_analyze_endpoint` and `tests/test_live_gemma4.py::test_live_02_structured_analysis_scholarship_notice`).

---

#### 13. `POST /api/confirm`
- **Purpose:** Human-in-the-loop review. Updates an uncertain or unverified fact with the user's manual confirmation/correction and synchronizes the action checklist and plain summary.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "field_name": "deadline",
    "confirmed_value": "15 November 2026",
    "structured_notice": { ... },
    "checklist": { ... }
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "structured_notice": { ... },
    "checklist": { ... },
    "summary": { ... },
    "updated_field": "deadline",
    "new_status": "CONFIRMED"
  }
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_confirm_endpoint`).

---

#### 14. `POST /api/summary/reading-level`
- **Purpose:** Regulates summary complexity according to user selection (`simple`, `standard`, `detailed`), accompanied by an informational/legal disclaimer.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "structured_notice": { ... },
    "reading_level": "simple",
    "target_lang": "en"
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "reading_level": "simple",
    "target_lang": "en",
    "disclaimer": "This plain-language summary is provided for informational and accessibility assistance...",
    "summary": { ... }
  }
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_reading_level_endpoint`).

---

#### 15. `POST /api/followup`
- **Purpose:** Notice-grounded conversational Q&A. Enforces strict factual grounding against `EvidenceService`. If information is unmentioned, returns the mandatory refusal:
  `"This information was not found in the provided notice."`
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "question": "Can I submit the application late?",
    "raw_notice_text": "...",
    "target_lang": "en"
  }
  ```
- **Response Format (200 OK):**
  ```json
  {
    "question": "Can I submit the application late?",
    "answer": "This information was not found in the provided notice. The notice does not specify this detail.",
    "is_supported": false,
    "evidence_quote": null,
    "unsupported_message": "Late submission policy is absent or unspecified in notice."
  }
  ```
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_followup_endpoint` and `tests/test_live_gemma4.py::test_live_04_followup_question_supported_and_unsupported`).

---

### Group E: Export & Accessibility Utilities

#### 16. `POST /api/export/markdown`
- **Purpose:** Exports the complete analysis, Six Core Fields, action checklist, and disclaimer as a clean Markdown report.
- **Authentication:** None.
- **Response Format (200 OK):** Text response (`text/markdown; charset=utf-8`).
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_export_markdown`).

---

#### 17. `POST /api/export/ics`
- **Purpose:** Generates a standard RFC 5545 iCalendar (`.ics`) file containing action checklist items with deadlines, reminders, and severity alarms.
- **Authentication:** None.
- **Response Format (200 OK):** `text/calendar; charset=utf-8` file download.
- **Verification Status:** **PASS** (Tested in `tests/test_api_endpoints.py::test_api_export_ics`).

---

#### 18. `POST /api/tts`
- **Purpose:** Converts notice summaries into MP3 audio via `gTTS` for auditory accessibility.
- **Authentication:** None.
- **Request Body (`application/json`):**
  ```json
  {
    "text": "Your scholarship application is due on 15 November 2026...",
    "lang": "en"
  }
  ```
- **Response Format (200 OK):** `audio/mpeg` binary audio stream.
- **Error Responses:**
  - `400 Bad Request`: Empty text.
  - `503 Service Unavailable`: TTS synthesis failure or offline environment without local TTS fallback.
- **Verification Status:** **PARTIAL** (Endpoint exists and validates input; live gTTS requires internet access to Google Translate TTS endpoints, with local fallback headers).

---

## 3. External Integration Registry

| Provider / Integration | Type | Endpoint / Base URL | Required Env Var | Local / Cloud | Default Active | Verified Status |
|---|---|---|---|---|---|---|
| **Ollama** | Local LLM | `http://127.0.0.1:11434` | None | Local | **YES** | **PASS** (Live Gemma 4) |
| **OpenRouter** | Cloud LLM Router | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | Cloud | NO | **PASS** (Offline Mocked) |
| **Google Gemini** | Cloud LLM | `https://generativelanguage.googleapis.com` | `GEMINI_API_KEY` | Cloud | NO | **PASS** (Offline Mocked) |
| **Hugging Face** | Cloud Inference | `https://router.huggingface.co/hf-inference/v1` | `HUGGINGFACE_API_KEY` | Cloud | NO | **PASS** (Offline Mocked) |
| **Tesseract OCR** | OCR Engine | `C:\Program Files\Tesseract-OCR\tesseract.exe` | None | Local | **YES** | **PASS** (Live v5.4.0) |
| **RapidOCR** | OCR Adapter | Native ONNX runtime | None | Local | Fallback | **PASS** (Adapter verified) |
| **gTTS (Google TTS)** | Audio TTS | `https://translate.google.com` | None | Cloud | Optional | **PARTIAL** (Cloud dependency) |
