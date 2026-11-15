# SochnaSetu AI — Prioritized Improvement Roadmap & Technical Debt Ledger

**Project Scope:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Evaluation Role:** Senior Technical Project Reviewer & Systems Architect  

---

## 1. Priority Classification Guidelines

- **P0 — CRITICAL:** Prevents core application execution, risks serious data loss/corruption, or causes critical workflow termination.
- **P1 — HIGH:** Breaks important user features, introduces severe OCR inaccuracies, or causes factual hallucination.
- **P2 — MEDIUM:** Feature is incomplete, has known edge-case failures, poor error handling, or performance degradation.
- **P3 — LOW:** Minor UI inconsistencies, non-critical static analysis warnings, code cleanup, and documentation polish.

---

## 2. Comprehensive Issue & Enhancement Ledger

### Issue P0-01: Tesseract OSD Rotation Failure on Short Notices
- **Severity:** **P0 (Critical)**
- **Affected Module:** `src/notice2action/ocr.py` (lines 63–91, `detect_image_orientation`)
- **Evidence:** Rotating `synthetic_scholarship_notice.png` by 90° returns `Detected rotation: 0 degrees`. Tesseract's `image_to_osd` fails silently when text contains fewer than ~15 lines, leaving sideways circulars unreadable.
- **Root Cause:** Tesseract OSD uses an internal character-threshold cutoff. When threshold is not met, an exception is caught and the function returns the unmodified image (`return image, 0`).
- **Recommended Fix:** Implement an auxiliary edge-projection or four-way contour bounding aspect ratio check. If line count is low, sample 90° and 270° rotations against a rapid OCR confidence pass and select the orientation with the highest recognition confidence.
- **Dependencies:** None. Self-contained in `ocr.py`.

### Issue P1-01: Numeral & Date Spacing Split in Dual-Pass OCR
- **Severity:** **P1 (High)**
- **Affected Module:** `src/notice2action/ocr.py` and `src/notice2action/grounding.py`
- **Evidence:** Dual-pass Tesseract occasionally outputs `15/1 1/2026` instead of `15/11/2026`. Strict regex patterns in `grounding.py` fail to extract the date, incorrectly triggering `status="flagged_uncertain"`.
- **Root Cause:** Token IoU fusion aligns separate character boxes from `hin` and `eng` passes, introducing spaces between adjacent digits.
- **Recommended Fix:**
  1. Add token post-processing in `ocr.py`: `re.sub(r'(\d)\s+(?=\d)', r'\1', text)` and normalize slashes: `re.sub(r'(\d+)\s*/\s*(\d+)\s*/\s*(\d+)', r'\1/\2/\3', text)`.
  2. Relax date regex in `grounding.py` to tolerate optional internal spaces: `r'\b\d{1,2}\s*[/-]\s*\d{1,2}\s*[/-]\s*\d{2,4}\b'`.
- **Dependencies:** Impacts `ocr.py`, `grounding.py`, and `test_factual_grounding.py`.

### Issue P1-02: Overfitted Hardcoded Gazette Vocabulary in General Pipeline
- **Severity:** **P1 (High)**
- **Affected Module:** `src/notice2action/ocr.py` (lines 220–225, 843–850)
- **Evidence:** Hardcoded string overrides (`"अपराजिता सारंगी"`, `"11011/1/2016"`, gazette vocabulary list) are embedded directly within `clean_and_repair_gazette_text` and `fused_multilingual_tesseract`.
- **Root Cause:** Specialized logic introduced to achieve a 95.2% score on a single benchmark sample (`gazette_corrigendum_2017.jpeg`) was placed into the general OCR execution path.
- **Recommended Fix:** Decouple domain-specific gazette post-processors into a pluggable rule engine or condition them strictly upon `category == "GAZETTE"`. Use generalized Indic dictionary lookup for non-gazette circulars.
- **Dependencies:** Regression testing against `test_gazette_ocr_benchmark.py`.

### Issue P1-03: RapidOCR ONNX Adapter Inert in Virtual Environment
- **Severity:** **P1 (High)**
- **Affected Module:** `src/notice2action/ocr.py` (lines 1180–1205, `RapidOCREngine`)
- **Evidence:** `RapidOCREngine` falls back to Tesseract with a warning because `rapidocr-onnxruntime` is not listed in `requirements.txt`.
- **Root Cause:** Adapter code was committed, but dependency was not added to the production environment manifest.
- **Recommended Fix:** Add `rapidocr-onnxruntime>=1.3.0` to `requirements.txt` and `pyproject.toml`. Configure RapidOCR as the default primary engine for CPU environments (yielding 4x faster execution: ~0.8s vs 6.3s per page).
- **Dependencies:** Python environment package installation.

### Issue P2-01: CSRF Missing Origin Rejection in Test Clients
- **Severity:** **P2 (Medium)**
- **Affected Module:** `src/notice2action/api/server.py` (lines 406–411) and test suites
- **Evidence:** Automated test clients (`TestClient(app)`) that execute successive state-changing requests with persistent session cookies are rejected with HTTP 403 Forbidden because Starlette does not send `Origin` headers by default.
- **Root Cause:** CSRF middleware treats `has_session_cookie and not (origin or referer)` as an untrusted state-changing request.
- **Recommended Fix:** In `server.py`, add a development exception:
  ```python
  if has_session_cookie and not (origin or referer):
      if getattr(config, "is_development", False) or request.client.host in ("127.0.0.1", "testclient"):
          # Allow local development/test clients
  ```
- **Dependencies:** Ensures 100% pass rate across all 509 Pytest integration tests.

### Issue P2-02: Native Binary PDF Export for Citizen Action Slips
- **Severity:** **P2 (Medium)**
- **Affected Module:** `frontend/src/components/CitizenActionSlip.tsx` and `server.py`
- **Evidence:** Exporting citizen action plans currently relies on browser `window.print()` or Markdown text downloads. Rural kiosk operators require a direct "Download Official PDF" button.
- **Root Cause:** Server lacks a dedicated PDF rendering endpoint (e.g. `pypdf` canvas or `reportlab`).
- **Recommended Fix:** Add a `POST /api/export/pdf` endpoint returning a standardized, high-contrast, pre-formatted PDF document with official civic disclaimers.
- **Dependencies:** Backend PDF generation library.

### Issue P2-03: Frontend JavaScript Bundle Size Exceeds 1MB
- **Severity:** **P2 (Medium)**
- **Affected Module:** `frontend/src/App.tsx`, `vite.config.ts`
- **Evidence:** Vite build warns: `dist/assets/index-CoQrozz0.js is 1,176.27 kB`.
- **Root Cause:** All 12 workspace views (`DashboardView`, `IngestionView`, `CrossNoticeTimelineView`, `EligibilityEngineView`, etc.) are imported statically in `ApplicationLayout.tsx`.
- **Recommended Fix:** Convert view imports to dynamic `React.lazy()` imports with `Suspense` fallbacks:
  ```typescript
  const GroundedFactsView = React.lazy(() => import('../views/GroundedFactsView'));
  ```
- **Dependencies:** Frontend build configuration.

### Issue P3-01: Oxlint Synchronous setState Warnings in useEffect
- **Severity:** **P3 (Low)**
- **Affected Module:** `NoticeContext.tsx`, `Header.tsx`, `OCRPanel.tsx`
- **Evidence:** `npm run lint` reports 18 warnings: `react(set-state-in-effect): Calling setState synchronously within an effect can trigger cascading renders`.
- **Root Cause:** Initial state synchronization from `localStorage` occurs inside immediate `useEffect` callbacks.
- **Recommended Fix:** Wrap state initializers in `queueMicrotask` or derive values directly during render initialization (`useState(() => getInitialState())`).
- **Dependencies:** None.

---

## 3. Recommended Implementation Sequence (Phased Roadmap)

```
PHASE 1: Immediate Stabilization (Week 1)
  ├── 1. Add intra-numeral space normalization to `ocr.py` post-processing.
  ├── 2. Relax date regex in `grounding.py` to prevent false uncertainty flags.
  ├── 3. Add development/test loopback bypass in CSRF middleware (`server.py`).
  └── 4. Re-run complete 509-test backend test suite to verify 100% pass rate.

PHASE 2: OCR Architecture Modernization (Week 2)
  ├── 1. Install `rapidocr-onnxruntime` into project virtual environment.
  ├── 2. Wire RapidOCR as the default primary detection & recognition engine.
  ├── 3. Implement robust 4-direction edge orientation to replace failing Tesseract OSD.
  ├── 4. Decouple hardcoded gazette heuristics into a distinct domain plugin.
  └── 5. Measure and record updated CER/WER benchmarks on the Gazette sample.

PHASE 3: UI/UX & Kiosk Export Polish (Week 3)
  ├── 1. Implement code-splitting (`React.lazy`) in `ApplicationLayout.tsx`.
  ├── 2. Add server-side `POST /api/export/pdf` for one-click citizen dossier downloads.
  └── 3. Resolve all 18 `oxlint` warnings in frontend context hooks.

PHASE 4: COA Academic Presentation & Defense (Week 4)
  ├── 1. Generate SIMD vs Scalar execution time comparison scripts for lab viva.
  ├── 2. Assemble hardware block diagrams (Cache hierarchy, DMA socket streaming).
  └── 3. Prepare mini-project viva presentation deck and final dossier.
```
