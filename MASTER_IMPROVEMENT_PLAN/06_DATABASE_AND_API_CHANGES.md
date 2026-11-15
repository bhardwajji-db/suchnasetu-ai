# SochnaSetu AI — Database Migrations & API Endpoint Changes

**Target Files:** `src/notice2action/storage/db.py`, `src/notice2action/api/server.py`, `src/notice2action/schemas.py`  
**Role:** Senior Database Administrator & Backend Architect  

---

## 1. Database Schema Migration Plan: Schema Version 5 $\to$ 6

The SQLite persistence layer currently operates at `SCHEMA_VERSION = 5`. To support token-level Human-in-the-Loop review, correction memory, and full-text search, the schema will be upgraded to `SCHEMA_VERSION = 6` using non-destructive, backwards-compatible transactions.

```
Migration 6 Schema Additions:
  ├── Table: `ocr_tokens`           -> Stores granular word bounding boxes & confidence
  ├── Table: `correction_memory`    -> Stores citizen-approved OCR corrections
  └── Virtual Table: `documents_fts`-> SQLite FTS5 full-text search index
```

### 1.1 SQL Migration Script (`Migration_6.sql`)

```sql
-- Migration 6: Token Coordinates, Correction Memory, and Full-Text Search
BEGIN TRANSACTION;

-- 1. Granular OCR Tokens Table
CREATE TABLE IF NOT EXISTS ocr_tokens (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL DEFAULT 1,
    token_index INTEGER NOT NULL,
    word_text TEXT NOT NULL,
    confidence REAL NOT NULL,
    box_x1 INTEGER NOT NULL,
    box_y1 INTEGER NOT NULL,
    box_x2 INTEGER NOT NULL,
    box_y2 INTEGER NOT NULL,
    is_uncertain BOOLEAN NOT NULL DEFAULT 0,
    uncertainty_reason TEXT,
    corrected_text TEXT,
    is_user_corrected BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ocr_tokens_doc ON ocr_tokens(document_id, token_index);
CREATE INDEX IF NOT EXISTS idx_ocr_tokens_uncertain ON ocr_tokens(document_id, is_uncertain);

-- 2. Correction Memory & Pattern Dictionary Table
CREATE TABLE IF NOT EXISTS correction_memory (
    id TEXT PRIMARY KEY,
    issuing_authority TEXT,
    raw_ocr_string TEXT NOT NULL,
    corrected_string TEXT NOT NULL,
    hit_count INTEGER NOT NULL DEFAULT 1,
    last_applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_correction_raw ON correction_memory(raw_ocr_string);

-- 3. Full-Text Search Virtual Table (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    document_id UNINDEXED,
    filename,
    issuing_authority,
    text_content
);

-- Populate FTS5 with existing document data
INSERT INTO documents_fts (document_id, filename, issuing_authority, text_content)
SELECT id, filename, source_language, text_content FROM documents;

-- Update Schema Version Tracker
UPDATE schema_migrations SET version = 6 WHERE id = 1;

COMMIT;
```

---

## 2. API Endpoint Additions & Pydantic Schemas

### 2.1 OCR Token Correction Endpoint
- **Route:** `POST /api/ocr/correct-token`
- **Controller:** `server.py` $\to$ `correct_ocr_token_endpoint`
- **Request Schema:**
  ```python
  class TokenCorrectionRequest(BaseModel):
      document_id: str
      token_index: int
      corrected_text: str
      field_name: Optional[str] = None
  ```
- **Response Schema:**
  ```python
  class TokenCorrectionResponse(BaseModel):
      status: str = "success"
      document_id: str
      token_index: int
      new_token_text: str
      updated_quality_score: float
      affected_field: Optional[str] = None
      is_now_verified: bool = True
  ```

### 2.2 Re-Grounding Execution Endpoint
- **Route:** `POST /api/documents/{document_id}/re-ground`
- **Description:** Re-evaluates fact grounding across the full document text after token corrections.
- **Response Schema:**
  ```python
  class ReGroundResponse(BaseModel):
      document_id: str
      structured_notice: StructuredNotice
      six_core_fields: SixCoreFields
      summary_en: str
      summary_hi: str
      checklist_en: List[ChecklistItem]
      checklist_hi: List[ChecklistItem]
  ```

### 2.3 Native Binary PDF Export Endpoint
- **Route:** `POST /api/export/pdf`
- **Request Schema:**
  ```python
  class ExportPdfRequest(BaseModel):
      document_id: str
      language: str = "en"  # "en" or "hi"
      include_original_thumbnail: bool = True
      include_audit_trail: bool = True
  ```
- **Response:** Streaming HTTP response with headers:
  ```http
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="sochnasetu_citizen_dossier.pdf"
  ```

### 2.4 Hardware Architecture Benchmark Endpoint
- **Route:** `GET /api/hardware/benchmark`
- **Description:** Executes live SIMD AVX2 vs Scalar Python comparison for academic COA demonstrations.
- **Response Schema:**
  ```python
  class HardwareBenchmarkResponse(BaseModel):
      simd_supported: bool
      avx2_detected: bool
      scalar_execution_ms: float
      vector_simd_execution_ms: float
      measured_speedup_factor: float
      l1_cache_size_kb: int
      processed_pixels: int
      throughput_gb_per_sec: float
  ```

---

## 3. Safe Migration & Backwards Compatibility Rules

1. **Zero Data Loss Guarantee:** Migrations are wrapped in an atomic SQLite transaction (`BEGIN TRANSACTION` / `COMMIT`). If any table creation fails, the transaction rolls back cleanly, leaving Version 5 database files unmodified.
2. **Graceful Fallback:** If `FTS5` is unavailable in the host Python SQLite compilation, the system catches the initialization error and falls back to traditional SQL `LIKE %query%` queries without crashing.
3. **Additive-Only Schema Changes:** No existing columns are renamed or dropped from `documents`, `analyses`, `checklist_items`, or `users`. Existing stored notices remain 100% accessible.
