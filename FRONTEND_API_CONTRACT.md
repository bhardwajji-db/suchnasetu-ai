# Frontend-Backend API Contract & Specification
**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Protocol:** REST over HTTP / JSON / Multipart Form-Data  
**Base URL:** `http://127.0.0.1:8000` (Dev Proxy: `/api`)  
**Security:** Local CORS whitelist (`http://localhost:5173`, `http://127.0.0.1:5173`)  

---

## 1. Master Endpoint Inventory & Feature Mapping

| Operation / Feature | Existing Python Function | HTTP Method & Path | Adapter Needed? | Frontend Service Function | Test Coverage |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **System Diagnostics** | `run_preflight_diagnostics()` | `GET /api/health` | Yes (FastAPI route) | `apiClient.getHealth()` | `test_api_health` |
| **List Demo Fixtures** | `config.synthetic_fixtures_dir` | `GET /api/samples` | Yes (FastAPI route) | `apiClient.getSamples()` | `test_api_samples` |
| **Load Demo Fixture** | File read from `fixtures_dir` | `GET /api/samples/{name}` | Yes (FastAPI route) | `apiClient.loadSample(name)` | `test_api_load_sample` |
| **Sanitize Ingestion** | `ingest_pasted_text()` | `POST /api/ingest/text` | Yes (FastAPI route) | `apiClient.ingestText(text)` | `test_api_ingest_text` |
| **Upload Document** | `ingest_uploaded_file()` | `POST /api/ingest/upload` | Yes (FastAPI route) | `apiClient.uploadFile(file)` | `test_api_upload_file` |
| **Tesseract OCR** | `extract_text_from_image()` | `POST /api/ocr` | Yes (FastAPI route) | `apiClient.runOCR(formData)` | `test_api_ocr` |
| **Analyze Notice** | `NoticeAnalyzer.analyze_notice()` | `POST /api/analyze` | Yes (FastAPI route) | `apiClient.analyzeNotice(req)` | `test_api_analyze` |
| **Grounded Q&A** | `FollowUpAssistant.answer_question()` | `POST /api/followup` | Yes (FastAPI route) | `apiClient.askQuestion(req)` | `test_api_followup` |
| **Export Markdown** | Custom generator in `app.py` | `POST /api/export/markdown`| Yes (FastAPI route) | `apiClient.exportMarkdown(req)`| `test_api_export_md` |
| **Export iCalendar** | `ActionChecklist.to_ics_bytes()` | `POST /api/export/ics` | Yes (FastAPI route) | `apiClient.exportIcs(req)` | `test_api_export_ics` |
| **Text-to-Speech** | `generate_audio_bytes()` | `POST /api/tts` | Yes (FastAPI route) | `apiClient.getTTSAudio(req)` | `test_api_tts` |

---

## 2. Endpoint Specifications

### 1. `GET /api/health`
- **Description:** Returns system diagnostics for Python runtime, Tesseract OCR, Ollama server connectivity, and Gemma 4 model presence.
- **Request:** None
- **Response (200 OK):**
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
        "details": "tesseract v5.4.0.20240606 at ... Languages: eng, osd",
        "remedy": null
      },
      {
        "name": "Ollama Server",
        "status": "ok",
        "details": "Connected to http://127.0.0.1:11434. Found 1 model(s).",
        "remedy": null
      },
      {
        "name": "Gemma 4 Model",
        "status": "ok",
        "details": "Target model 'gemma4:latest' is available in Ollama.",
        "remedy": null
      }
    ]
  }
  ```
- **Error Behavior:** 500 Internal Server Error if server diagnostic engine encounters unhandled exception.

---

### 2. `GET /api/samples`
- **Description:** Returns the available quick-load demo notices and fixtures.
- **Request:** None
- **Response (200 OK):**
  ```json
  [
    {
      "id": "synthetic_scholarship_notice.txt",
      "title": "🎯 Competition Demo (TEST-SCH-2026-001)",
      "type": "text",
      "language": "en"
    },
    {
      "id": "sample_scholarship_notice.txt",
      "title": "📄 Scholarship Notice (EN)",
      "type": "text",
      "language": "en"
    },
    {
      "id": "sample_hindi_notice.txt",
      "title": "🇮🇳 Notice (Hindi)",
      "type": "text",
      "language": "hi"
    },
    {
      "id": "synthetic_notice_ocr.png",
      "title": "🖼️ Scanned Notice (OCR Demo)",
      "type": "image",
      "language": "en"
    },
    {
      "id": "sample_uncertain_notice.txt",
      "title": "⚠️ Tentative Dates Notice",
      "type": "text",
      "language": "en"
    },
    {
      "id": "sample_missing_fields_notice.txt",
      "title": "❓ Missing Fields Notice",
      "type": "text",
      "language": "en"
    }
  ]
  ```

---

### 3. `GET /api/samples/{filename}`
- **Description:** Fetches the raw content of a specific fixture.
- **Request:** Path parameter `filename: str`
- **Response (200 OK):**
  - If text fixture: `application/json` with `{ "filename": str, "content": str, "fingerprint": str }`
  - If image fixture: `image/png` binary stream.
- **Error Behavior:** 404 Not Found if fixture does not exist; 400 Bad Request if filename attempts path traversal (`..`).

---

### 4. `POST /api/ingest/text`
- **Description:** Ingests pasted or edited text, sanitizes content, and computes SHA-256 fingerprint.
- **Request (JSON):**
  ```json
  {
    "text": "Notice text here..."
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "raw_text": "Sanitized notice text...",
    "char_count": 733,
    "line_count": 18,
    "security_warning": null,
    "fingerprint": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
  }
  ```
- **Error Behavior:** 422 Unprocessable Entity if `text` is empty or whitespace.

---

### 5. `POST /api/ocr`
- **Description:** Uploads an image and runs Tesseract OCR with adaptive preprocessing.
- **Request (Multipart Form-Data):**
  - `file`: binary image file (PNG, JPG, JPEG, WEBP)
  - `target_lang`: string (`eng`, `hin`, `eng+hin`), default `eng`
  - `enhance_contrast`: boolean, default `true`
- **Response (200 OK):**
  ```json
  {
    "extracted_text": "Extracted OCR text...",
    "confidence_score": 86.8,
    "languages_used": "eng",
    "line_count": 22,
    "char_count": 721,
    "is_preprocessed": true,
    "warning": null,
    "error": null,
    "fingerprint": "..."
  }
  ```
- **Error Behavior:** 400 Bad Request if file exceeds size limit or invalid image type.

---

### 6. `POST /api/analyze`
- **Description:** Executes the complete 5-phase analysis pipeline: structured extraction via Gemma 4, quotation verification, summary synthesis, action checklist generation, and Hindi translation.
- **Request (JSON):**
  ```json
  {
    "notice_text": "Official notice text...",
    "target_language": "en"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "structured_notice": {
      "purpose": { "field_name": "purpose", "value": "...", "status": "stated", "evidence_quote": "...", "requires_confirmation": false, "user_confirmed": false },
      "eligibility": { ... },
      "deadline": { ... },
      "fee_or_cost": { ... },
      "required_documents": { ... },
      "contact_details": { ... },
      "required_actions": { ... },
      "important_conditions": { ... },
      "missing_information": ["..."],
      "uncertain_or_conflicting_details": ["..."],
      "raw_notice_text": "..."
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
          "requires_confirmation": false,
          "is_completed": false,
          "grounded_quote": "...",
          "notes": null
        }
      ]
    },
    "checklist_hi": { ... },
    "fingerprint": "...",
    "duration_seconds": 31.42
  }
  ```
- **Error Behavior:** 500 Internal Server Error with actionable diagnostic detail if Ollama or model inference fails.

---

### 7. `POST /api/followup`
- **Description:** Answers follow-up queries strictly grounded in the notice text.
- **Request (JSON):**
  ```json
  {
    "question": "What documents are required to apply?",
    "notice_text": "..."
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "question": "What documents are required to apply?",
    "answer": "You need to submit: Previous qualifying examination marksheet, College identity card, and Bank account proof.",
    "is_supported": true,
    "evidence_quote": "Required documents: 1. Previous qualifying examination marksheet (self-attested copy) 2. Current college identity card 3. Bank account passbook copy for direct fund transfer",
    "unsupported_message": null
  }
  ```

---

### 8. `POST /api/export/markdown`
- **Description:** Generates formatted Markdown report.
- **Request (JSON):** `{ "structured_notice": ..., "summary": ..., "checklist": ... }`
- **Response (200 OK):** `text/markdown` file attachment (`notice2action_plan.md`).

---

### 9. `POST /api/export/ics`
- **Description:** Generates RFC 5545 iCalendar (`.ics`) file for deadline scheduling.
- **Request (JSON):** `{ "checklist": { "items": [...] }, "title": "..." }`
- **Response (200 OK):** `text/calendar` file attachment (`notice_deadline.ics`).

---

### 10. `POST /api/tts`
- **Description:** Returns generated MP3 audio stream using gTTS for screen-reader and accessibility read-aloud.
- **Request (JSON):** `{ "text": "...", "lang": "en" | "hi" }`
- **Response (200 OK):** `audio/mpeg` binary stream.
- **Fallback:** Returns 204 No Content if gTTS is offline, prompting frontend to use browser-native `window.speechSynthesis`.
