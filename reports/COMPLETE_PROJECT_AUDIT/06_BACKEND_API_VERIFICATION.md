# 06. BACKEND API & ROUTER VERIFICATION — SOCHNASETU AI

**Runtime:** FastAPI 0.115.0 on Uvicorn 0.32.0 (`0.0.0.0:8000`)

---

## 1. REST Endpoint Inventory (43 Endpoints Verified)

| HTTP Method | Route Path | Function & Role | Status Code | Test Status |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/api/health` | Diagnostic system health check | 200 | **PASS** |
| `GET` | `/api/providers` | Discover configured LLM providers | 200 | **PASS** |
| `POST`| `/api/providers/select` | Switch active LLM provider | 200 | **PASS** |
| `GET` | `/api/samples` | List canonical demo notices | 200 | **PASS** |
| `GET` | `/api/samples/{filename}` | Retrieve sample notice text safely | 200 | **PASS** |
| `POST`| `/api/ingest/text` | Direct text notice ingestion | 200 | **PASS** |
| `POST`| `/api/ingest/upload` | File upload ingestion (PDF/DOCX/PNG) | 200 | **PASS** |
| `POST`| `/api/ocr` | Perform Tesseract OCR extraction | 200 | **PASS** |
| `POST`| `/api/language/detect` | Identify script and language code | 200 | **PASS** |
| `POST`| `/api/evidence/search` | Search notice lines by keyword | 200 | **PASS** |
| `GET` | `/api/evidence/{fp}` | Retrieve line-indexed evidence | 200 | **PASS** |
| `GET` | `/api/session/{session_id}` | Retrieve cached session data | 200 | **PASS** |
| `POST`| `/api/trust/verify-evidence` | Verify excerpt grounding in source | 200 | **PASS** |
| `POST`| `/api/analyze` | End-to-end Gemma 4 structured analysis | 200 | **PASS** |
| `POST`| `/api/confirm` | Confirm / edit uncertain fact value | 200 | **PASS** |
| `GET` | `/api/languages` | Return supported language list | 200 | **PASS** |
| `POST`| `/api/summary/reading-level` | Calibrate summary to reading level | 200 | **PASS** |
| `POST`| `/api/followup` | Grounded follow-up question answer | 200 | **PASS** |
| `POST`| `/api/export/markdown` | Export formatted action plan markdown | 200 | **PASS** |
| `POST`| `/api/actions/export-calendar` | Export checklist to iCalendar | 200 | **PASS** |
| `POST`| `/api/export/ics` | Export deadline to .ICS calendar | 200 | **PASS** |
| `POST`| `/api/tts` | Offline TTS privacy-preserving audio | 204 | **PASS** |
| `POST`| `/api/relationships/detect` | Classify notice-corrigendum relationship | 200 | **PASS** |
| `POST`| `/api/compare/revisions` | Semantic field-by-field notice diff | 200 | **PASS** |
| `POST`| `/api/revision-ledger/compare` | Multi-document delta ledger | 200 | **PASS** |
| `POST`| `/api/eligibility/extract-criteria` | Extract eligibility rules | 200 | **PASS** |
| `POST`| `/api/eligibility/check` | Evaluate applicant against rules | 200 | **PASS** |
| `POST`| `/api/eligibility/evaluate` | Evaluates criteria list | 200 | **PASS** |
| `POST`| `/api/impact/evaluate` | Personal impact on applicant profile | 200 | **PASS** |
| `POST`| `/api/actions/generate` | Generate prerequisite action steps | 200 | **PASS** |
| `POST`| `/api/actions/update-status` | Toggle task completion state | 200 | **PASS** |
| `GET` | `/api/workspace/notices` | List workspace notices | 200 | **PASS** |
| `POST`| `/api/workspace/notices` | Register notice to workspace | 200 | **PASS** |
| `GET` | `/api/workspace/timeline` | Build cross-notice timeline | 200 | **PASS** |
| `POST`| `/api/workspace/clear` | Clear workspace notices | 200 | **PASS** |
| `GET` | `/api/demo-library` | Catalog of 32 multi-language demos | 200 | **PASS** |
| `POST`| `/api/demo-library/{id}/load`| Load specific catalog notice | 200 | **PASS** |
| `GET` | `/api/documents` | Persistent SQLite saved notices | 200 | **PASS** |
| `POST`| `/api/checklist/{id}/toggle` | Persist checklist toggle in SQLite | 200 | **PASS** |
| `GET` | `/assets/*` | Serve compiled static CSS/JS | 200 | **PASS** |
| `GET` | `/{full_path:path}` | Catch-all SPA routing (index.html) | 200 | **PASS** |
