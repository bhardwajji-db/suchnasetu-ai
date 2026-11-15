# SochnaSetu AI — Detailed Implementation Tasks & Work Breakdown

**Role:** Senior Project Manager & Technical Delivery Lead  
**Structure:** Work Breakdown Structure (WBS) ranked by strict architectural priority (P0 to P3).  

---

## Task Summary Ledger

| Task ID | Title | Priority | Est. Hours | Prerequisite Tasks | Independent? |
|---|---|:---:|:---:|:---:|:---:|
| **TASK-P0-01** | Fix Tesseract OSD Orientation on Short Notices | **P0** | 4h | None | **YES** |
| **TASK-P0-02** | Add Development Loopback Bypass to CSRF Middleware | **P0** | 2h | None | **YES** |
| **TASK-P1-01** | Implement Intra-Numeral Space Normalization | **P1** | 3h | None | **YES** |
| **TASK-P1-02** | Decouple Hardcoded Gazette Vocabulary Overfitting | **P1** | 4h | None | **YES** |
| **TASK-P1-03** | Activate RapidOCR ONNX Adapter with Token Bounding Boxes | **P1** | 6h | None | **YES** |
| **TASK-P1-04** | Implement Human-in-the-Loop Token Correction Endpoint | **P1** | 6h | Schema Migration | No |
| **TASK-P1-05** | Build Interactive Red Zigzag OCR Token Editor Popover | **P1** | 6h | TASK-P1-04 | No |
| **TASK-P2-01** | Execute Database Migration 6 (Schema v6) | **P2** | 3h | None | **YES** |
| **TASK-P2-02** | Implement Split-Screen Workspace (Viewer + AI Cards) | **P2** | 8h | TASK-P1-05 | No |
| **TASK-P2-03** | Server-Side Binary PDF Dossier Export Endpoint | **P2** | 6h | None | **YES** |
| **TASK-P2-04** | Implement Frontend Lazy Loading (`React.lazy`) | **P2** | 3h | None | **YES** |
| **TASK-P3-01** | Build COA SIMD Hardware Benchmark CLI Tool | **P3** | 4h | None | **YES** |
| **TASK-P3-02** | Resolve 18 Frontend Oxlint Synchronous setState Warnings | **P3** | 3h | None | **YES** |

---

## Detailed Task Specifications

### [TASK-P0-01] Fix Tesseract OSD Orientation on Short Notices
- **Objective:** Prevent silent rotation failures on circulars and posters with $<15$ text lines.
- **Exact Files Affected:**
  - `src/notice2action/ocr.py` (`detect_image_orientation`)
- **Dependencies:** None. Self-contained in `ocr.py`.
- **Implementation Approach:**
  Wrap `image_to_osd` in a try/except block. If `image_to_osd` raises an exception or confidence $<15.0$, compute horizontal vs. vertical edge density using Sobel gradients. If height < width on standard notices, test 90° rotation against a lightweight header recognition check.
- **Acceptance Criteria:**
  - Synthetic 90°-rotated notice image (`synthetic_scholarship_notice.png` rotated 90°) is correctly detected as requiring 90° rotation and returned upright.
  - Test `test_orientation_recovery.py` passes 100%.

---

### [TASK-P0-02] Add Development Loopback Bypass to CSRF Middleware
- **Objective:** Eliminate HTTP 403 Forbidden errors when test clients or local developer tools send state-changing requests with session cookies without Origin headers.
- **Exact Files Affected:**
  - `src/notice2action/api/server.py` (lines 400–415)
- **Dependencies:** None.
- **Implementation Approach:**
  In the CSRF middleware, if `has_session_cookie` is true and `not (origin or referer)`, check if `getattr(config, "environment", "development") == "development"` or client host is loopback (`127.0.0.1`, `localhost`, `testclient`). If so, log a debug message and permit the request.
- **Acceptance Criteria:**
  - All 32 failing integration tests in `test_backend_persisted_auth.py` and `test_master_e2e_acceptance.py` pass without needing manual test header injection.

---

### [TASK-P1-01] Implement Intra-Numeral Space Normalization
- **Objective:** Prevent split numbers (e.g. `15/1 1/2026`) from triggering false uncertainty flags in grounding.
- **Exact Files Affected:**
  - `src/notice2action/ocr.py` (`clean_and_repair_gazette_text`, `fused_multilingual_tesseract`)
  - `src/notice2action/grounding.py` (`extract_critical_tokens`)
- **Dependencies:** None.
- **Implementation Approach:**
  Add regex replacement pass collapsing spaces between digits separated by slashes/hyphens: `re.sub(r'(\d{1,2})\s*([/-])\s*(\d{1,2})\s*([/-])\s*(\d{2,4})', r'\1\2\3\4\5', text)`. Relax date regex in `grounding.py` to match optional internal whitespace.
- **Acceptance Criteria:**
  - OCR outputs dates as solid tokens (`15/11/2026`).
  - Date extraction accuracy reaches 100% on synthetic and real test fixtures.

---

### [TASK-P1-02] Decouple Hardcoded Gazette Vocabulary Overfitting
- **Objective:** Remove hardcoded signatory names and reference numbers from the generic OCR loop, moving them to a conditional Gazette post-processor.
- **Exact Files Affected:**
  - `src/notice2action/ocr.py` (lines 204–248, 843–850)
- **Dependencies:** Regression check against `test_gazette_ocr_benchmark.py`.
- **Implementation Approach:**
  Condition specialized Gazette repair logic strictly upon `category == "GAZETTE"` or presence of statutory mastheads. Replace exact name strings with generic administrative regex patterns (`\b(?:संयुक्त सचिव|Joint Secretary|Under Secretary)\b`).
- **Acceptance Criteria:**
  - `tests/test_gazette_ocr_benchmark.py` maintains $\ge 95.2\%$ field accuracy on the Gazette sample.
  - Non-gazette circulars are processed cleanly without injecting Gazette terms.

---

### [TASK-P1-03] Activate RapidOCR ONNX Adapter with Token Coordinates
- **Objective:** Enable lightweight, high-speed ONNX CPU inference for English and Devanagari circulars.
- **Exact Files Affected:**
  - `pyproject.toml` / `requirements.txt`
  - `src/notice2action/ocr.py` (`RapidOCREngine`)
- **Dependencies:** Installation of `rapidocr-onnxruntime>=1.3.8`.
- **Implementation Approach:**
  Add package dependency. Implement polygon-to-bbox conversion $[x_1, y_1, x_2, y_2]$ in `RapidOCREngine.extract_text`. Populate `word_boxes` and `image_dimensions`. Wire RapidOCR as the primary engine when present.
- **Acceptance Criteria:**
  - OCR execution time drops from 6.3s to $<1.2\text{s}$ per page.
  - `word_boxes` and `image_dimensions` are fully populated.

---

### [TASK-P1-04] Implement Human-in-the-Loop Token Correction Endpoint
- **Objective:** Provide a backend endpoint to persist citizen word-level OCR corrections and re-trigger fact grounding.
- **Exact Files Affected:**
  - `src/notice2action/api/server.py`
  - `src/notice2action/schemas.py`
  - `src/notice2action/storage/db.py`
- **Dependencies:** Migration 6 (`ocr_tokens` and `correction_memory` tables).
- **Implementation Approach:**
  Implement `POST /api/ocr/correct-token`. Updates token in `ocr_tokens` and `documents.text_content`. Invokes `verify_structured_notice()` to recalculate grounded certainty states.
- **Acceptance Criteria:**
  - Submitting a corrected date string resolves `status="flagged_uncertain"` to `status="verified"`.

---

### [TASK-P1-05] Build Interactive Red Zigzag OCR Token Editor Popover
- **Objective:** Allow citizens to click any red-underlined OCR word to view original scan pixels and submit a correction.
- **Exact Files Affected:**
  - `frontend/src/components/OriginalNoticeViewerModal.tsx`
  - `frontend/src/components/OCRTokenEditorModal.tsx` (New component)
  - `frontend/src/context/NoticeContext.tsx`
- **Dependencies:** `TASK-P1-04`.
- **Implementation Approach:**
  Map `ocrResult.word_boxes` to interactive span tags with `style={{ textDecoration: 'underline wavy #DC2626 2px' }}` for words with confidence $<65\%$. On click, open `OCRTokenEditorModal` displaying original crop, confidence chip, and input box.
- **Acceptance Criteria:**
  - Clicking an underlined word opens editor popover and centers the scan on the matching bounding box.
  - Saving the edit updates the text in real-time.

---

### [TASK-P2-01] Execute Database Migration 6 (Schema v6)
- **Objective:** Create `ocr_tokens`, `correction_memory`, and `documents_fts` SQLite tables.
- **Exact Files Affected:**
  - `src/notice2action/storage/db.py` (`init_db`, `SCHEMA_VERSION = 6`)
- **Dependencies:** None.
- **Implementation Approach:**
  Add atomic migration step checking `SCHEMA_VERSION < 6`. Executes `CREATE TABLE IF NOT EXISTS ocr_tokens`, `correction_memory`, and virtual table `documents_fts`.
- **Acceptance Criteria:**
  - `SCHEMA_VERSION` advances to 6.
  - All existing documents and analyses remain intact.

---

### [TASK-P2-02] Implement Split-Screen Workspace (Viewer + AI Cards)
- **Objective:** Modernize the layout into a side-by-side document intelligence workbench.
- **Exact Files Affected:**
  - `frontend/src/components/ApplicationLayout.tsx`
  - `frontend/src/views/GroundedFactsView.tsx`
- **Dependencies:** `TASK-P1-05`.
- **Implementation Approach:**
  Embed `OriginalNoticeViewerModal` as a persistent left pane on wide viewports ($\ge 1024\text{px}$) with collapsible toggle. Clicking a fact card in the right pane highlights the corresponding scan region in the left pane.
- **Acceptance Criteria:**
  - Split-screen workspace operates with synchronized scrolling on desktop viewports.
  - Automatically collapses to stacked view on mobile devices.

---

### [TASK-P2-03] Server-Side Binary PDF Dossier Export Endpoint
- **Objective:** Allow citizens to download formal PDF action dossiers directly from the server.
- **Exact Files Affected:**
  - `src/notice2action/api/server.py`
  - `src/notice2action/services/pdf_export_service.py` (New module)
- **Dependencies:** Lightweight PDF canvas library (`pypdf` or `reportlab`).
- **Implementation Approach:**
  Implement `POST /api/export/pdf`. Assembles high-contrast, formatted PDF containing issuing header, verified fields table, action checklist with checkboxes, and SHA-256 seal.
- **Acceptance Criteria:**
  - Returns valid `%PDF-1.4` binary stream with `Content-Disposition: attachment`.

---

### [TASK-P2-04] Implement Frontend Lazy Loading (`React.lazy`)
- **Objective:** Reduce initial client bundle size by code-splitting view components.
- **Exact Files Affected:**
  - `frontend/src/components/ApplicationLayout.tsx`
- **Dependencies:** None.
- **Implementation Approach:**
  Replace static imports of `DashboardView`, `IngestionView`, `SettingsView`, etc., with `React.lazy(() => import(...))` wrapped in `<Suspense fallback={<LoadingSpinner />}>`.
- **Acceptance Criteria:**
  - Main bundle size decreases from 1,176 kB to $<450\text{ kB}$.

---

### [TASK-P3-01] Build COA SIMD Hardware Benchmark CLI Tool
- **Objective:** Provide a standalone benchmark tool demonstrating Computer Organization & Architecture concepts for lab submission.
- **Exact Files Affected:**
  - `scripts/coa_hardware_benchmark.py` (New script)
  - `src/notice2action/api/server.py` (`/api/hardware/benchmark`)
- **Dependencies:** None.
- **Implementation Approach:**
  Implement scalar loop vs AVX2 NumPy projection deskew. Measures clock cycles, cache utilization, and prints comparative speedup table ($>4x$).
- **Acceptance Criteria:**
  - Command `python scripts/coa_hardware_benchmark.py` executes in $<3\text{s}$ and outputs clean comparative metrics.

---

### [TASK-P3-02] Resolve 18 Frontend Oxlint Synchronous setState Warnings
- **Objective:** Eliminate all static analysis warnings in `NoticeContext.tsx` and view components.
- **Exact Files Affected:**
  - `frontend/src/context/NoticeContext.tsx`
  - `frontend/src/components/Header.tsx`, `OCRPanel.tsx`
- **Dependencies:** None.
- **Implementation Approach:**
  Refactor synchronous `setState` calls inside `useEffect` by wrapping them in asynchronous microtasks or initializing state directly via functional initializers.
- **Acceptance Criteria:**
  - `npm run lint` finishes with **0 errors and 0 warnings**.
