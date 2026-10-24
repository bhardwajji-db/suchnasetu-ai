# SuchnaSetu AI — REST API Reference

The SochnaSetu AI backend runs on FastAPI at `http://127.0.0.1:8000`. Interactive OpenAPI documentation is accessible at `http://127.0.0.1:8000/docs`.

---

## 1. Primary Endpoints

### `POST /api/analyze`
Analyzes raw notice text, extracts structured facts, generates plain-language summaries, and outputs an action checklist.

**Request Body (`application/json`):**
```json
{
  "notice_text": "District Disaster Management Authority Order...",
  "target_language": "hi",
  "source_language": "en",
  "reading_level": "standard"
}
```

**Response (`200 OK`):**
```json
{
  "session_id": "uuid",
  "document_id": "uuid",
  "source_language": "en",
  "detected_language": "en",
  "language_confidence": 1.0,
  "structured_notice": {
    "issuing_authority": {"value": "DDMA", "status": "stated", "evidence_quote": "..."},
    "notice_reference_number": {"value": "DM/2026/01", "status": "stated"},
    "deadline": {"value": "15 Nov 2026", "status": "stated"}
  },
  "summary_en": "Plain English summary...",
  "summary_hi": "सरल हिन्दी सारांश...",
  "checklist_en": [
    {"task": "Prepare ID proof", "deadline": "15 Nov 2026", "is_completed": false}
  ]
}
```

---

### `POST /api/ingest/upload`
Uploads and processes multi-format documents (`.txt`, `.pdf`, `.docx`, `.png`, `.jpg`, `.webp`, `.tif`).

**Request (`multipart/form-data`):**
- `file`: Binary file upload

**Response (`200 OK`):**
```json
{
  "filename": "circular.pdf",
  "file_type": "pdf",
  "char_count": 2840,
  "raw_text": "Extracted text content...",
  "security_warning": null
}
```

---

### `POST /api/compare/revisions`
Compares original and revised notices field-by-field, producing an auditable revision ledger.

**Request Body (`application/json`):**
```json
{
  "source_session_id": "original_notice_id",
  "target_session_id": "revised_notice_id"
}
```

**Response (`200 OK`):**
```json
{
  "source_notice_id": "original_notice_id",
  "target_notice_id": "revised_notice_id",
  "entries": [
    {
      "field_name": "deadline",
      "display_name": "Application Deadline",
      "old_value": "10 Nov 2026",
      "new_value": "25 Nov 2026",
      "change_category": "MODIFIED",
      "category": "DEADLINE_EXTENSION"
    }
  ]
}
```

---

### `POST /api/eligibility/evaluate`
Evaluates an applicant profile against notice criteria.

**Request Body (`application/json`):**
```json
{
  "session_id": "session_uuid",
  "user_profile": {
    "category": "General",
    "annual_income_inr": 250000,
    "education_level": "Undergraduate"
  }
}
```

**Response (`200 OK`):**
```json
{
  "overall_status": "ELIGIBLE",
  "overall_verdict": "ELIGIBLE",
  "satisfied_criteria": ["Income <= 3,00,000", "Undergraduate Enrollment"],
  "unmet_criteria": [],
  "missing_information": []
}
```

---

### `POST /api/followup`
Answers specific user queries strictly grounded in the notice text.

**Request Body (`application/json`):**
```json
{
  "session_id": "session_uuid",
  "question": "What is the application deadline?",
  "target_language": "en"
}
```

---

### `GET /api/demo-library`
Returns the catalog of 32 synthetic demo notices.

---

### `GET /api/health`
Returns backend health, Ollama status, and active model name.
