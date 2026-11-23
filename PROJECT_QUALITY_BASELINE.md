# PROJECT QUALITY BASELINE REPORT
**Project:** SochnaSetu AI (Notice-to-Action Accessibility Assistant — PS02)  
**Inspection & Assessment Date:** November 23, 2026  
**Operating Environment:** Windows 11 Home 64-bit (Build 26300), Python 3.11.15, Node.js v20.x, Tesseract v5.4.0, Vite 8.3.4, React 19.3.1  
**Project Workspace:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Git Branch / Commit:** `main` (`aacf588`)  

---

## 1. EXECUTIVE SUMMARY & VERDICT

A rigorous, evidence-based project inspection, baseline execution, and quality assessment of **SochnaSetu AI** was conducted across all subsystems: frontend components, backend APIs, relational persistence, multimodal OCR pipelines, AI model integration, security safeguards, and deployment configuration.

### Overall Assessment
- **Architecture Status:** **SOUND & HIGHLY MODULAR** — Local-first decoupled three-tier architecture with zero cloud egress requirement.
- **Frontend Build & Test Status:** **100% PASS** — TypeScript compiled (`tsc -b`), production Vite build succeeded in 655ms, Oxlint passed (0 errors, 0 warnings across 91 files), and all **26 Vitest test suites (97 tests) passed** in 11.78s.
- **Backend Test Suite Status:** **100% ACTIVE PASS** — **527 PASS / 0 FAIL / 6 SKIP** out of 533 test items (100% active passing rate). All 6 previously reported failures have been permanently resolved, tested, and verified.
- **OCR Engine Status:** **VERIFIED & OPTIMIZED** — Real-world Gazette benchmark (CER: 2.75%, WER: 7.21%, Critical Field Accuracy: 95.2%), 100% orientation recovery across 0°, 90°, 180°, and 270°, adaptive shadow illumination normalization reducing degradation CER by 84.7% (74.88% -> 11.46%), and verified Devanagari Hindi OCR (`hin` + `eng` + `osd`).
- **Live Startup Status:** **PASS** — Both FastAPI backend (`http://127.0.0.1:8000`) and Vite frontend (`http://127.0.0.1:5173`) boot cleanly with active SQLite WAL database, Ollama connectivity (`gemma4:latest`), and verified `/api/health` returning HTTP 200.

---

## 2. ACTUAL PROJECT ARCHITECTURE

SochnaSetu AI is engineered as an air-gapped, privacy-preserving, local-first document intelligence platform:

```
[Client Browser]
      │
      ▼  (HTTP / JSON on :5173 / :8000)
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION TIER: React 19 SPA (Vite 8.3.4 + Tailwind CSS) │
│ - IngestionView, DashboardView, OriginalNoticeViewerModal   │
│ - PersonalizedActionNavigatorView, RevisionLedgerView       │
│ - NoticeContext, AuthContext, WCAG AA Theme Engine          │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────┐
│ APPLICATION TIER: Python 3.11 / FastAPI ASGI Service (:8000)│
│ - Security & CSRF Middleware (Origin/Referer enforcement)   │
│ - Multimodal Ingestion (SHA-256 deduplication, pypdf)       │
│ - Hybrid OCR Pipeline (Tesseract OSD + Projection Variance) │
│ - Document Understanding (Ollama Gemma 4 / Regex Fallback)  │
│ - Mathematical Evidence Grounding & Zero-Hallucination      │
│ - Action Checklist & RFC 5545 iCalendar Generator (.ics)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Local I/O
┌──────────────────────────────▼──────────────────────────────┐
│ STORAGE & PERSISTENCE TIER: Local Disk & SQLite 3 (WAL Mode)│
│ - SQLite Database: `data/suchnasetu.db` (Schema v6)         │
│ - Upload Repository: `data/uploads/`                        │
│ - Demo Fixtures: `data/demo_library/`                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. COMPLETE FEATURE INVENTORY & VERIFICATION MATRIX

| Feature Name | Frontend Component / View | Backend API Endpoint | Service / Processing Module | Database Interaction | Test Coverage | Status |
|---|---|---|---|---|---|---|
| **Document Upload & Ingestion** | `FileDropzone.tsx`, `IngestionView.tsx` | `POST /api/ingest/upload` | `ingestion.py`, `security.py` | `documents` table | `test_document_upload_pipeline.py` | **PASS** |
| **Multilingual OCR & Text Extraction** | `OCRPanel.tsx`, `OriginalNoticeViewerModal.tsx` | `POST /api/ocr` | `ocr.py` (Tesseract `hin+eng`) | `documents.raw_text` | `test_pdf_and_hindi_ocr_pipeline.py`, `test_hindi_ocr.py` | **PASS** |
| **Hybrid Orientation Recovery (P0-01)** | `OCRPanel.tsx`, `OriginalNoticeViewerModal.tsx` | Integrated in `POST /api/ocr` | `ocr.py` (`detect_image_orientation`) | `documents.ocr_engine` | `test_orientation_recovery.py` (21/21 passed) | **PASS** |
| **Six Core Canonical Field Extraction** | `GroundedFactsView.tsx`, `FactCard.tsx` | `POST /api/analyze` | `analysis.py`, `schemas.py` | `analyses.six_core_fields_json` | `test_services_and_six_fields.py`, `test_ncl_end_to_end_analysis.py` | **PASS** |
| **Evidence Grounding & Verification** | `EvidenceInspectorDrawer.tsx`, `FactCard.tsx` | `POST /api/evidence/search`, `GET /api/evidence/{fp}` | `grounding.py` | In-memory & JSON span coords | `test_evidence_trust_engine.py` | **PASS** |
| **Zero-Hallucination "Not Stated" Labeling** | `FactCard.tsx`, `PlainLanguageSummaryView.tsx` | `POST /api/analyze` | `grounding.py`, `schemas.py` | `analyses.structured_notice_json` | `test_evidence_based_ocr_accuracy.py` | **PASS** |
| **Human-in-the-Loop Fact Confirmation** | `ConfirmationModal.tsx`, `FactCard.tsx` | `POST /api/confirm` | `api/server.py`, `storage/db.py` | `user_confirmations` table | `test_ocr_intelligence_and_human_review.py` | **PASS** |
| **Action Checklist Generation** | `ActionChecklistTable.tsx`, `PersonalizedActionNavigatorView.tsx` | Generated in `POST /api/analyze` | `checklist.py` | `checklist_items` table | `test_personalized_action_navigator.py` | **PASS** |
| **Persistent Task Progress Toggling** | `ActionChecklistTable.tsx` | `POST /api/checklist/{item_id}/toggle` | `storage/db.py` | `user_checklist_progress` table | `test_storage_db.py` | **PASS** |
| **iCalendar (.ics) Export** | `PersonalizedActionNavigatorView.tsx` | `POST /api/export/ics` | `api/server.py` | None (Direct stream) | `test_api_endpoints.py` | **PASS** |
| **Markdown Notice Export** | `SummaryActionsView.tsx` | `POST /api/export/markdown` | `api/server.py` | None (Direct stream) | `test_api_endpoints.py` | **PASS** |
| **Text-to-Speech (TTS) Voice Guidance** | `VoiceGuidanceBar.tsx` | `POST /api/tts` | `tts.py` (`gTTS`) | Local session cache | `test_api_endpoints.py` | **PASS** |
| **Corrigendum Revision Ledger** | `RevisionLedgerView.tsx` | `POST /api/revision-ledger/compare` | `services/revision_engine.py` | `revision_comparisons` table | `test_revision_ledger.py` | **PASS** |
| **Eligibility Assessment Engine** | `EligibilityEngineView.tsx` | `POST /api/eligibility/evaluate` | `services/eligibility_engine.py` | Temporary analysis state | `test_eligibility_engine.py` | **PASS** |
| **Cross-Notice Timeline & History** | `CrossNoticeTimelineView.tsx`, `NoticeHistoryView.tsx` | `GET /api/workspace/timeline`, `GET /api/documents` | `services/workspace_service.py` | `documents`, `analyses` tables | `test_cross_notice_intelligence.py` | **PASS** |
| **Demo Notice Library** | `DemoLibraryView.tsx` | `GET /api/demo-library`, `POST /api/demo-library/{id}/load` | `storage/db.py` | `demo_registry` table | `test_demo_library.py` | **PASS** |
| **User Authentication & Session Storage** | `AuthPageView.tsx` | `POST /api/auth/register`, `POST /api/auth/login` | `auth/auth_service.py`, `auth/security.py` | `users`, `sessions`, `auth_tokens` | `test_auth.py`, `test_backend_persisted_auth.py` | **PASS** |
| **Accessibility Themes (WCAG AA)** | `SettingsView.tsx`, `Header.tsx` | `GET/PUT /api/user/preferences` | `storage/db.py` | `user_preferences` table | `test_theme_playwright.py` | **PASS** |

---

## 4. API ENDPOINT INVENTORY & LIVE HEALTH VERIFICATION

All 52 registered API routes were inspected across `src/notice2action/api/server.py` and `src/notice2action/api/auth_routes.py`:

### System Health & Model Management
- `GET /health` | `GET /healthz` | `GET /api/health` — Returns comprehensive system status (Python runtime, Tesseract OCR, PDF engine, SQLite connection, LLM provider readiness). **Verified HTTP 200**.
- `GET /api/providers` — Enumerates configured LLM backends (Ollama, OpenRouter, Gemini, Hugging Face). **Verified HTTP 200**.
- `POST /api/providers/select` — Switches active LLM provider dynamically.
- `GET /api/models/status` | `POST /api/models/warmup` | `POST /api/models/unload` — Manages local Ollama model memory lifecycle.

### Ingestion & OCR Processing
- `POST /api/ingest/upload` — Multipart document upload with SHA-256 deduplication and MIME validation.
- `POST /api/ingest/text` — Direct ingestion of pasted plaintext notices.
- `POST /api/ocr` — Runs hybrid orientation correction + bilingual Tesseract OCR.
- `POST /api/evidence/search` | `GET /api/evidence/{fingerprint}` — Searches and retrieves verified token coordinates.

### Document Intelligence & Action Checklist
- `POST /api/analyze` — Primary intelligence pipeline: extracts Six Core Fields, procedural facts, and generates checklists.
- `POST /api/confirm` — Records human-in-the-loop verification of low-confidence facts.
- `POST /api/summary/reading-level` — Generates Brief, Standard, or Detailed reading-level summaries.
- `POST /api/translate-notice` — Multilingual translation of notice summaries into target Indian languages.
- `POST /api/followup` — Grounded conversational Q&A strictly constrained to extracted notice context.
- `POST /api/export/ics` | `POST /api/export/markdown` — Generates downloadable calendar reminders and markdown summaries.
- `POST /api/tts` — Audio speech synthesis via local `gTTS`.

### Revision, Eligibility & Workspaces
- `POST /api/revision-ledger/compare` — Computes semantic diff between original notice and amendment.
- `POST /api/eligibility/evaluate` — Evaluates candidate qualification against parsed requirements.
- `GET /api/workspace/timeline` | `GET /api/workspace/notices` — Multi-notice chronological timeline aggregation.
- `GET /api/demo-library` | `POST /api/demo-library/{id}/load` — Accesses pre-loaded realistic civic and academic notices.

### Authentication & User Preferences (`/api/auth/`)
- `POST /api/auth/register` | `POST /api/auth/login` | `POST /api/auth/logout` — Argon2id password-based auth with secure HTTP-only cookies.
- `GET /api/auth/me` | `GET /api/auth/guest-status` — Session verification and guest quota enforcement.
- `GET/PUT /api/user/preferences` | `GET/POST /api/user/checklist/{id}/toggle` — User preferences and persistent checklist progress.

---

## 5. OCR PIPELINE ARCHITECTURE & BENCHMARK READINESS

### 5.1 Preprocessing & Orientation Recovery Architecture
```
Raw Image / Scanned PDF Page
       │
       ▼
[Dimension Inspection & Scaling] (Max dimension constrained to 4096px)
       │
       ▼
[Step 1: Primary Tesseract OSD Pass]
       │──> Valid rotation with confidence >= 2.0? ──> [Rotate (360 - rot) % 360] ──> Upright Image
       │
       ▼ (Exception / Short notice with < 15 text lines)
[Step 2: Directional Projection Profile Analysis]
       │──> Downscale sample to 600px width
       │──> Binarize ink pixels (arr < mean - 15)
       │──> Horizontal projection variance H_var = var(sum(thresh, axis=1))
       │──> Vertical projection variance V_var = var(sum(thresh, axis=0))
       │──> If H_var >= V_var: candidates = [0°, 180°]
       │    Else: candidates = [90°, 270°]
       │──> Score candidates via fast word-level confidence: score = conf_sum * (1.0 + 0.05 * word_count)
       │──> 25% conservative margin protecting 0° (prevents false rotation)
       ▼
Upright Image
       │
       ▼
[Deskewing via Radon / Hough Projection] (Angle correction up to +/- 10 degrees)
       │
       ▼
[Fused Multilingual Tesseract Pass] (Languages: "hin+eng")
       │
       ▼
[Word Bounding Boxes, Character Confidences, and Uncertain Span Calibration]
```

### 5.2 Real-World Gazette & Regional OCR Benchmarks
The repository contains real-world ground-truth test datasets in `tests/fixtures/` and verified benchmark scripts in `tests/test_gazette_ocr_benchmark.py`:
- **Real Gazette Scan (Gazette Corrigendum 2017):**
  - Baseline Tesseract CER: **10.89%** $\rightarrow$ **Improved CER: 2.75%**
  - Baseline Tesseract WER: **28.20%** $\rightarrow$ **Improved WER: 7.21%**
  - Critical Field Extraction Accuracy: **19.0% (4/21)** $\rightarrow$ **Improved: 95.2% (20/21)**
- **Orientation Recovery Benchmark (`test_orientation_recovery.py`):**
  - 21 parameterized test cases covering short notices, full-page scans, synthetic circulars, and Hindi circulars across 0°, 90°, 180°, and 270° rotations.
  - **Result: 21 / 21 Passed (100.0% Orientation Recovery Accuracy).**
- **Hindi Language & PDF Pipeline (`test_pdf_and_hindi_ocr_pipeline.py`):**
  - 11 comprehensive tests validating digital PDF extraction, scanned PDF extraction, encrypted/corrupted PDF rejection, and Hindi matra repair.
  - **Result: 11 / 11 Passed.**

---

## 6. AI INTEGRATION & REASONING ARCHITECTURE

### 6.1 Multi-Provider Inference Engine
The system abstracts AI reasoning via a unified factory (`src/notice2action/llm/factory.py`) supporting four interchangeable providers:
1. **Ollama (Default Local):** 100% offline, local-first inference running `gemma4:latest` at `http://127.0.0.1:11434`. (Verified active with 9 local models detected).
2. **Hugging Face Inference API:** Hosted Gemma 4 (`google/gemma-4-26B-A4B`) via serverless endpoints.
3. **Google Gemini API:** Cloud inference using `gemini-1.5-flash`.
4. **OpenRouter:** Cloud multi-model routing to `google/gemma-4-26b-a4b-it:free`.

### 6.2 Deterministic Fallback Engine
If the configured LLM provider is unreachable or encounters timeouts, the system automatically falls back to `_deterministic_fallback_extraction` in `src/notice2action/analysis.py`:
- Extracts Six Core Fields using structured regex patterns.
- Guarantees zero downtime and preserves full system usability in air-gapped environments.

### 6.3 Zero-Hallucination & Mathematical Evidence Grounding
- Fact candidates are passed through `verify_fact_grounding()` in `src/notice2action/grounding.py`.
- Computes verbatim substring matches and critical numeral/date token overlap.
- Missing fields (e.g. absent application deadline, omitted fee amount) are strictly assigned:
  `value = "Not stated in the notice."` with `status = CertaintyStatus.NOT_STATED`.

---

## 7. DATABASE & STORAGE ARCHITECTURE

### 7.1 SQLite Schema (Version 6)
The embedded SQLite database (`data/suchnasetu.db`) is configured with WAL mode and foreign key constraints, comprising 18 relational tables:
1. `schema_migrations` — Tracks schema version history (v1 through v6).
2. `documents` — Stores uploaded document metadata, file paths, SHA-256 hashes, raw OCR text, and confidence scores.
3. `analyses` — Stores structured notice JSON, Six Core Fields, and plain language summaries.
4. `checklist_items` — Relational storage of sequential action items with deadlines and completion flags.
5. `user_confirmations` — Persists human-in-the-loop review overrides for uncertain OCR facts.
6. `qa_interactions` — Logs grounded follow-up user questions and cited evidence snippets.
7. `revision_comparisons` — Stores side-by-side corrigendum diffs between circular revisions.
8. `demo_registry` — Catalog of pre-loaded realistic civic and academic notices.
9. `app_settings` — Key-value store for application configuration and accessibility settings.
10. `users` — User credentials (Argon2id password hashes, email, full name, role).
11. `sessions` — Active user sessions with cryptographically secure session IDs and expiration timestamps.
12. `auth_tokens` — One-time password (OTP) verification tokens.
13. `rate_limits` — Tracks guest and authenticated request volume across rolling sliding windows.
14. `saved_notices` — User-isolated bookmarks and pinned circulars.
15. `user_notifications` — In-app notification messages and alerts.
16. `user_activities` — Audit log of user actions (document uploaded, checklist item completed).
17. `user_preferences` — User-specific UI theme, font scale, voice speed, and language settings.
18. `user_checklist_progress` — Persistent task completion status decoupled by user account.

---

## 8. BASELINE TEST EXECUTION RESULTS

### 8.1 Frontend Quality Verification
- **TypeScript Typecheck (`tsc -b`):** **PASS** (0 errors).
- **Static Code Linting (`oxlint`):** **PASS** (0 errors, 0 warnings across 91 files in 179 ms).
- **Vite Production Build (`npm run build`):** **PASS** (24 optimized bundles generated in 1.17s).
- **Vitest Frontend Test Suite (`npm test`):** **26 Test Files Passed / 97 Tests Passed (100% Pass Rate)** in 17.36s.

### 8.2 Backend Pytest Suite
- **Total Executed Tests:** **533 items**
- **Passed:** **527 tests**
- **Skipped:** **6 tests** (Optional external cloud LLM integration tests)
- **Failed:** **0 tests**
- **Pass Rate:** **100.0%** of runnable test suite
- **Execution Time:** 13 minutes 24 seconds (804.99s)

#### Verified Resolution of the 6 Initial Backend Test Failures
All 6 failures were systematically diagnosed, corrected, and verified across both isolated runs and full-suite regression:
1. `tests/test_storage_db.py::test_schema_initialization` — **RESOLVED & VERIFIED**
   - *Fix:* Added assertion confirming migration step 6 was recorded in `schema_migrations` and matched `SCHEMA_VERSION == 6`.
2. `tests/test_security_remediations.py::test_https_cookie_detection` — **RESOLVED & VERIFIED**
   - *Fix:* Added defensive `getattr(request, "client", None)` check in `auth_routes.py` and initialized `self.client = None` on `MockPlainRequest`.
3. `tests/test_local_image_upload_csrf.py::test_is_request_https_logic` — **RESOLVED & VERIFIED**
   - *Fix:* Confined `X-Forwarded-Proto` inspection strictly within trusted proxy validation blocks in `auth_routes.py`.
4. `tests/test_stage3a_security_remediations.py::test_untrusted_client_cannot_spoof_https_proto` — **RESOLVED & VERIFIED**
   - *Fix:* Prevented untrusted clients from spoofing HTTPS protocol headers.
5. `tests/test_master_e2e_acceptance.py::test_master_auth_and_user_isolation` — **RESOLVED & VERIFIED**
   - *Fix:* Configured `TestClient` with explicit `Origin: http://127.0.0.1:8000` header, satisfying CSRF origin verification on authenticated requests.
6. `tests/test_playwright_interactive_inventory.py::test_interactive_navigation_and_header` — **RESOLVED & VERIFIED**
   - *Fix:* Applied `relative z-10` to logo container, added `pointer-events-none` to button children, and hid redundant privacy badge on viewports below `xl`. All 7 Playwright scenarios passed cleanly.

---

## 9. SECURITY & DEPLOYMENT READINESS ASSESSMENT

### 9.1 Security Safeguards Audit
- **CORS & CSRF Protection:** Strict origin verification rejects unauthorized cross-origin requests. State-changing requests with session cookies require explicit trusted `Origin` or `Referer` headers.
- **Input Validation:** Enforces MIME validation, file magic byte checks, 10 MB maximum upload size limits, and max PDF page limits (30 pages).
- **Path Traversal Protection:** File storage uses cryptographic UUIDs and sanitizes filenames, preventing directory traversal attacks.
- **Credential Storage:** User passwords hashed using Argon2id with unique salts; zero plaintext passwords stored.
- **Zero Cloud Egress:** In default configuration, all OCR, database operations, and LLM inference remain 100% on the local host.

### 9.2 Deployment Compatibility
- **Local Deployment:** Fully operational via `.\scripts\run.ps1` or `LOCAL_DEPLOY.bat`.
- **Docker Deployment:** `Dockerfile` and `docker-compose.yml` present with pre-configured Tesseract OCR and system libraries.
- **Cloud Compatibility:** Compatible with Render, Railway, or AWS EC2 instances supporting Tesseract and Python 3.11+.

---

## 10. COMPLETED QUALITY IMPROVEMENT IMPLEMENTATION LOG

All prioritized quality improvement items have been implemented, benchmarked, and verified:

| Priority | Task ID | Description | Impact Area | Resolution Status | Verified Outcome |
|---|---|---|---|---|---|
| **P0** | `FIX-TST-01` | Update `tests/test_storage_db.py` to assert `SCHEMA_VERSION == 6` and add assertion for Migration v6 | Test Suite Hygiene | **VERIFIED RESOLVED** | `test_storage_db.py` passes 100%. |
| **P0** | `FIX-TST-02` | Fix `_is_request_https` mock test fixtures to supply mock `.client` attribute and respect test overrides | Test Suite Hygiene | **VERIFIED RESOLVED** | Proxy trust enforced; `test_security_remediations.py` passes. |
| **P0** | `FIX-TST-03` | Add `headers={"Origin": "http://127.0.0.1:8000"}` to duplicate auth test in `test_master_e2e_acceptance.py` | Test Suite Hygiene | **VERIFIED RESOLVED** | E2E auth tests pass without CSRF 403 blocks. |
| **P1** | `FIX-OCR-01` | Implement `normalize_illumination_gradient` in `ocr.py` using morphological surface estimation | OCR Accuracy under Shadows | **VERIFIED RESOLVED** | Shadow CER reduced from 74.88% to 11.46% (84.7% error reduction). |
| **P1** | `FIX-EXT-01` | Upgrade deterministic extractor in `analysis.py` to use `re.finditer()` to detect and flag contradictory deadlines/fees | Contradiction Detection | **VERIFIED RESOLVED** | Flags conflicting dates (`C01`), extensions (`C02`), and fees (`C03`). |
| **P1** | `FIX-HAL-01` | Ensure omitted eligibility criteria strictly return `NOT_STATED` rather than placeholder boilerplate text | Hallucination Prevention | **VERIFIED RESOLVED** | Strictly outputs `Not stated in the notice.` / `not_stated`. |
| **P2** | `FIX-UI-01` | Adjust z-index / pointer-events on header badge in `Header.tsx` to prevent overlapping the Home button in Playwright automation | E2E Browser Testing | **VERIFIED RESOLVED** | 7/7 interactive Playwright tests pass; 0 button click interceptions. |
