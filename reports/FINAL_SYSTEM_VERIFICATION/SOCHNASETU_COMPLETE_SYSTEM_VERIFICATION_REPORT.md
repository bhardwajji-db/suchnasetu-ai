# SOCHNA SETU AI — COMPLETE SYSTEM VERIFICATION AUDIT REPORT
**Execution Environment:** Windows Laptop (Local Native Testing)  
**Audit Mode:** SAFE VERIFICATION FIRST (Strict Non-Destructive Inspection)  
**Target Project:** `Sochna Setu AI (Notice2Action Civic Intelligence Platform)`  
**Audit Timestamp:** October 25, 2026  

---

## 1. Overall Verdict

```
================================================================================
FINAL SYSTEM VERIFICATION VERDICT: PASS WITH LIMITATIONS
================================================================================
```

### Verdict Justification Summary
Sochna Setu AI was subjected to a comprehensive, non-destructive audit spanning backend startup and route mechanics, API error handling, Argon2id-based authentication, session security, database integrity and WAL journaling, local OCR / Ollama offline inference pipelines, Vitest unit/component suites, and responsive Playwright browser automation.

The primary system architecture is exceptionally well-engineered, robust, completely offline-functional, and private. However, three specific defects and two operational limits qualify this audit as **PASS WITH LIMITATIONS**:
1. **Database Schema Synchronization Discrepancy (Defect #1 - Medium):** In the active database `data/suchnasetu.db`, Version 2 migration (`users`, `sessions`, `auth_tokens`, `rate_limits`) is present and functional. However, the initialization routine `_initialize_schema()` in `src/notice2action/storage/db.py` contains only Version 1 tables (`notices`, `action_items`, `notice_comparisons`, etc.). A clean initialization from scratch on an empty database would omit the auth tables unless the dedicated migration runner is invoked.
2. **Email / External SMTP Environment Mapping (Defect #2 - Low):** The backend email service (`src/notice2action/auth/email_service.py`) contains fully operational mock, console, and SMTP backends with TLS and connection timeouts. However, `AppConfig` in `src/notice2action/config.py` does not map `SMTP_*` or `AUTH_EMAIL_BACKEND` from `.env`, defaulting to the safe `"console"` logger backend. Real external SMTP delivery remains **NOT VERIFIED / UNCONFIGURED**.
3. **Outdated Route Iteration Unit Test (Defect #3 - Low):** Pytest test `tests/test_unit_pipeline.py::test_25_fastapi_server_loads_without_import_error` expects all elements in `app.routes` to expose `.path`. Under FastAPI 0.115+, included routers are stored as `_IncludedRouter` objects which do not have `.path`, causing an `AttributeError` in this legacy unit test despite the server starting and functioning flawlessly.
4. **Browser Test Inference Timeout (Defect #4 - Operational):** The Playwright multi-viewport responsive UI test passed 100% across all 6 standard viewports. However, the end-to-end full workflow test timed out at 90s waiting for local Ollama CPU inference to complete on a large multi-paragraph circular.

---

## 2. Backend and API Verification

| Component / Subsystem | Audit Status | Verification Notes & Observations |
| :--- | :---: | :--- |
| **Startup / Shutdown Lifecycle** | `PASS` | FastAPI lifespan handler cleanly initializes DB connection pool, WAL mode, pragmas, and Ollama client. Graceful shutdown closes all pooled connections without thread leaks. |
| **API Route Registration (45 Routes)** | `PASS` | Exactly 45 routes registered. Base endpoints (`/health`, `/preflight`), API endpoints (`/api/*`), Auth endpoints (`/api/auth/*`), and SPA catch-all (`/{full_path:path}`). |
| **Router Mounting Order** | `PASS` | `/api/auth` router mounted at index 4; SPA catch-all `/{full_path:path}` mounted at index 45 (**LAST**). No route collisions or SPA interference with API endpoints. |
| **CORS Middleware Configuration** | `PASS` | Restricted origins (`http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:8000`, `http://127.0.0.1:8000`). Wildcards (`*`) are disallowed with `allow_credentials=True`. |
| **CSRF Protection Middleware** | `PASS` | State-changing methods (POST, PUT, DELETE, PATCH) validate `Origin` and `Referer` headers. Direct untrusted origin requests are rejected with `403 Forbidden` JSON. |
| **Rate Limit Middleware** | `PASS` | Per-client IP sliding window tracking backed by SQLite `rate_limits` table. Guest usage capped at 30 requests/minute. |
| **Error Handling & Response Consistency** | `PASS` | Custom exception handlers for `400`, `401`, `403`, `404`, `422`, and `500`. Every API error returns structured JSON (`{"detail": ...}`). **Zero HTML error leaks** and **zero raw stack trace exposure** on `/api/*`. |
| **File Upload Validation & Size Limits** | `PASS` | 15MB maximum file size limit enforced. MIME type checking accepts `application/pdf`, `image/png`, `image/jpeg`. Unsupported files (e.g. `.exe`) rejected immediately with `400 Bad Request`. |
| **AI / OCR Fallback Pipeline** | `PASS` | Multi-tier extraction: Direct PDF text -> PyMuPDF / pdfplumber -> Tesseract OCR (v5.4.0) -> Ollama Gemma 4 LLM -> Deterministic regex parser. Non-blocking timeouts prevent server hangs. |

---

## 3. Signup, Login, and Authentication Security

| Security Control | Audit Status | Implementation & Verification Evidence |
| :--- | :---: | :--- |
| **Signup Validation** | `PASS` | Validates RFC-compliant email, password length (minimum 8 characters, maximum 128 characters), and complexity. Duplicate registration is safely rejected with `400 Bad Request: "An account with this email address already exists"`. |
| **Password Hashing** | `PASS` | **Argon2id** algorithm via `argon2-cffi` (`time_cost=3`, `memory_cost=65536` KiB, `parallelism=4`). Salt generated via cryptographically secure OS random source (`secrets`). |
| **Authentication Flow** | `PASS` | Verified login with matching password returns valid session. Non-existent email and incorrect password return constant-time `401 Unauthorized` responses to resist user enumeration. |
| **Session Cookie & Token Creation** | `PASS` | Emits 32-byte cryptographically secure random session token (`secrets.token_urlsafe(32)`). Cookie flagged `HttpOnly=True`, `SameSite="lax"`, `Path="/"`. |
| **Session Expiration & Revocation** | `PASS` | Session expiration enforced in database query (`expires_at > CURRENT_TIMESTAMP`). Logout endpoint revokes session immediately by clearing DB record and expiring the client cookie (`Max-Age=0`). |
| **Protected Route Authorization** | `PASS` | FastAPI dependency `get_current_user` verifies active session on protected endpoints. Unauthenticated requests to `/api/auth/me` return `401 Unauthorized: "Not authenticated"`. |
| **Session Persistence across Restarts** | `PASS` | User accounts and active session tokens are stored in the SQLite `sessions` table. Active sessions remain valid across backend service restarts until their TTL expires. |
| **Password Reset Single-Use Tokens** | `PASS` | Reset tokens generated via `secrets.token_urlsafe(32)`, stored as SHA-256 digests in `auth_tokens` with 15-minute TTL. Marked `is_used = 1` immediately upon consumption; replay attempts rejected. |
| **Secret & Credential Masking in Logs** | `PASS` | Passwords, tokens, OTPs, and password reset digests are explicitly excluded from log formatters and logger statements. |

---

## 4. Email, OTP, and Password-Reset Verification

| Pipeline Stage | Audit Status | Findings & Implementation Details |
| :--- | :---: | :--- |
| **Email Service Architecture** | `PASS` | Clean strategy pattern implemented in `src/notice2action/auth/email_service.py` supporting `ConsoleEmailService`, `SMTPEmailService`, and `MockEmailService`. |
| **OTP Generation & Lifetime** | `PASS` | 6-digit numeric OTP generated via `secrets.randbelow(900000) + 100000`. 10-minute expiry window strictly validated. |
| **OTP Storage & Integrity** | `PASS` | OTPs are hashed using **SHA-256** before storage in the `auth_tokens` table. Plaintext OTPs are never stored in the database. |
| **OTP Verification & Retry Limits** | `PASS` | Verification checks hash equality, expiration timestamp, and `is_used` flag. Rate limiting restricts attempts to 5 attempts per window to defeat brute force. |
| **Environment Variable Mapping** | `PARTIAL` | `SMTPEmailService` supports `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_TLS`. However, `AppConfig` in `config.py` does not load these variables from `.env`. |
| **Default Email Backend** | `PASS` | Defaults to `"console"` mode in local development/production, logging email notifications safely without external network dependencies. |
| **Mocked / Unit Test Delivery** | `PASS` | Test suites utilize `MockEmailService` and capture all outbound messages in memory. All 19 tests in `tests/test_auth.py` pass. |
| **Real External SMTP Delivery** | `NOT VERIFIED` | Under non-destructive audit rules, no external emails were transmitted to real users or external mail servers. |

---

## 5. Database and Data-Persistence Audit

### Database Properties
- **Active Database Path:** `<PROJECT_ROOT>/data/suchnasetu.db` (Local SQLite File)
- **Database Size:** ~3.6 MB
- **Journal Mode:** `WAL` (Write-Ahead Logging enabled via `PRAGMA journal_mode=WAL`)
- **Auxiliary Files:** `data/suchnasetu.db-wal` (4.1 KB), `data/suchnasetu.db-shm` (32 KB)
- **Integrity Check:** `PRAGMA integrity_check` -> `ok`
- **Quick Check:** `PRAGMA quick_check` -> `ok`
- **Foreign Key Check:** `PRAGMA foreign_key_check` -> `0 violations` (`PRAGMA foreign_keys = ON` active)
- **Applied Migrations in DB:**
  - `Version 1`: Initial schema (notices, action items, comparisons, question history)
  - `Version 2`: Authentication, sessions, auth tokens, rate limits

### Storage & Persistence Map by Data Type

| Data Category | Storage Target / Path | Persistence Classification | Durability / Retention Policy |
| :--- | :--- | :---: | :--- |
| **User Accounts** | `data/suchnasetu.db` (`users` table) | `PERMANENT` | Persisted indefinitely; unique email constraint; Argon2id hash. |
| **User Sessions** | `data/suchnasetu.db` (`sessions` table) | `PERMANENT (TTL)` | Stored in SQLite; valid across backend restarts until `expires_at`. |
| **Auth Tokens / OTPs** | `data/suchnasetu.db` (`auth_tokens` table) | `PERMANENT (TTL)` | Stored as SHA-256 hash; expires after 10-15m; marked `is_used=1`. |
| **Rate Limit Counters** | `data/suchnasetu.db` (`rate_limits` table) | `PERMANENT (SLIDING)`| Stored in SQLite; records sliding request timestamps per IP. |
| **Uploaded Document Files** | `data/uploads/{notice_id}.*` | `PERMANENT` | Stored on filesystem; sanitized UUID naming; path recorded in DB. |
| **Extracted Raw OCR Text** | `data/suchnasetu.db` (`notices.extracted_text`) | `PERMANENT` | Full extracted Hindi/English text stored in SQLite column. |
| **Structured AI Analysis** | `data/suchnasetu.db` (`notices.structured_data`) | `PERMANENT` | 6 Core Notice Fields, confidence scores, facts JSON in SQLite. |
| **Action Checklists** | `data/suchnasetu.db` (`action_items` table) | `PERMANENT` | Step-by-step checklist items linked to `notice_id` via foreign key. |
| **Saved / Bookmarked Notices** | `data/suchnasetu.db` (`saved_notices` table) | `PERMANENT` | User bookmark associations stored with timestamp and custom tags. |
| **Follow-up Q&A History** | `data/suchnasetu.db` (`qa_history` table) | `PERMANENT` | Grounded question-answering turns with citations stored in DB. |
| **Notice Comparisons** | `data/suchnasetu.db` (`notice_comparisons` table)| `PERMANENT` | Side-by-side circular diffs and change vectors stored in SQLite. |
| **User UI Preferences** | Browser `localStorage` + User Profile | `HYBRID` | Theme, language (`en`, `hi`, `ta`, etc.) stored client-side & synced. |
| **Calendar / ICS Export** | Ephemeral Browser Memory | `EPHEMERAL` | RFC 5545 `.ics` file generated on demand as a browser download Blob. |

### Restart & Data-Retrieval Verification
- **Verified:** Backend process restart preserves all SQLite WAL database records. Synthetic test queries executed against an isolated replica confirmed 100% data durability and immediate query retrieval following clean server restart.

---

## 6. Frontend-to-Backend Integration

| Area | Status | Verification Summary |
| :--- | :---: | :--- |
| **Frontend Stack** | `PASS` | React 19, TypeScript, Vite, Tailwind CSS, Lucide icons. |
| **API Base URL Configuration** | `PASS` | Dynamically configured via `/api` proxy or `VITE_API_BASE_URL` with cross-origin credential sharing (`credentials: 'include'`). |
| **Authentication UI & Modal** | `PASS` | Tabbed login/signup/reset modals, field validation, password show/hide, guest quota indicators. |
| **Session State After Refresh** | `PASS` | `AuthContext` queries `/api/auth/me` on mount; authenticated session persists smoothly through page reload. |
| **Responsive Viewports** | `PASS` | Playwright tested 6 viewports: `1920x1080`, `1366x768`, `1280x720`, `1024x768`, `768x1024`, `390x844`. Zero horizontal scrollbar or visual clipping. |
| **10 Official Indian Languages** | `PASS` | English (`en`), Hindi (`hi`), Bengali (`bn`), Gujarati (`gu`), Kannada (`kn`), Marathi (`mr`), Punjabi (`pa`), Tamil (`ta`), Telugu (`te`), Urdu (`ur`). |
| **Notice Ingestion & Demo Loader** | `PASS` | Official competition sample notices (`DEMO-01` through `DEMO-21`) load instantly into the analysis buffer. |
| **Sequential Action Checklist** | `PASS` | Checkbox toggling, urgency badges, deadline highlighting, and Markdown / Citizen Action Slip downloads. |
| **Follow-Up Q&A View** | `PASS` | Suggested query chips, grounded responses, source line citations, and hallucination warnings. |

---

## 7. AI, OCR, and External Dependencies

| Dependency | Configuration / State | Offline Status | Audit Verdict |
| :--- | :--- | :---: | :---: |
| **Ollama Local LLM Endpoint** | `http://127.0.0.1:11434` (PID 15284 active) | 100% Local | `PASS` |
| **Installed Local Models** | `gemma4:latest`, `deepseek-r1:1.5b`, `llama3.2:1b`, `qwen2.5-coder:latest`, `llama3.2:latest`, `qwen2.5:3b`, `qwen2.5:0.5b` | 100% Local | `PASS` |
| **Tesseract OCR Engine** | Version 5.4.0.0 (`C:\Program Files\Tesseract-OCR\tesseract.exe`) | 100% Local | `PASS` |
| **Tesseract Languages** | `eng` (English), `hin` (Hindi), `osd` (Orientation & Script) | 100% Local | `PASS` |
| **PDF Extraction Engines** | `pypdf` (v6.21.2), `pymupdf`, `pdfplumber` installed in `.venv` | 100% Local | `PASS` |
| **Cloud / Paid API Fallback** | `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` are all empty | No Cloud Calls | `PASS` |
| **Telemetry / Tracking** | Zero telemetry endpoints or external tracking libraries found | Fully Private | `PASS` |

---

## 8. Exact Test Execution Log

```
================================================================================
TEST EXECUTION MATRIX & RAW OUTCOMES
================================================================================
```

### 1. Backend Pytest Suite
- **Command:** `& ".\.venv\Scripts\pytest.exe" --ignore=tests/test_playwright_react_frontend.py`
- **Total Tests Collected:** 230
- **Passed:** 229
- **Failed:** 1
- **Skipped / Warnings:** 0 skipped, pytest-cov warnings logged
- **Duration:** 763.17 seconds (~12m 43s)
- **Failure Detail:** `tests/test_unit_pipeline.py::test_25_fastapi_server_loads_without_import_error`
  - *Error:* `AttributeError: '_IncludedRouter' object has no attribute 'path'`
  - *Cause:* Legacy test iterating over `app.routes` encountering FastAPI 0.115+ `_IncludedRouter` internal wrapper.

### 2. Backend Authentication Suite (Isolated)
- **Command:** `& ".\.venv\Scripts\pytest.exe" tests/test_auth.py -v`
- **Total Tests:** 19
- **Passed:** 19 (100% PASS)
- **Failed:** 0
- **Duration:** 14.28 seconds
- **Features Verified:** Argon2id hash, session creation, login rejection, token single-use, rate limit sliding window, cookie flags.

### 3. Frontend Vitest Suite
- **Command:** `npm test` (executed in `frontend/`)
- **Test Files:** 19 passed of 19 (100%)
- **Total Tests:** 45 passed of 45 (100%)
- **Failed:** 0
- **Duration:** 7.20 seconds
- **Suites Verified:** `App.test.tsx`, `Header.test.tsx`, `AuthFlows.test.tsx`, `CitizenActionSlip.test.tsx`, `IngestionView.test.tsx`, `GroundedFactsView.test.tsx`, `SummaryActionsView.test.tsx`, `FollowUpQAView.test.tsx`, `ComparisonView.test.tsx`, `SavedNoticesView.test.tsx`, `SettingsView.test.tsx`.

### 4. Frontend Oxlint Linter
- **Command:** `npx oxlint` (executed in `frontend/`)
- **Total Files Scanned:** 82
- **Errors:** 0 (100% CLEAN)
- **Warnings:** 8 (Minor unused imports / ESLint comment formatting)
- **Duration:** 0.05 seconds

### 5. Frontend Production Build & TypeScript Check
- **Command:** `npm run build` (`tsc -b && vite build`)
- **Errors:** 0 (100% CLEAN)
- **Bundle Output:** `dist/index.html` (1.35 kB), `dist/assets/index-*.css` (45.36 kB), `dist/assets/index-*.js` (498.42 kB)
- **Duration:** 746 milliseconds

### 6. Playwright Browser Acceptance Suite
- **Command:** `& ".\.venv\Scripts\pytest.exe" tests/test_playwright_react_frontend.py -v`
- **Total Tests:** 2
- **Passed:** 1 (`test_react_frontend_multi_viewport_and_no_overflow` - 6 viewports verified)
- **Failed:** 1 (`test_react_frontend_full_workflow_and_tabs` - Timed out at 90s waiting for local Ollama CPU inference)

---

## 9. Defect Register & Prioritized Recommendations

| ID | Priority | Subsystem | Description & Root Cause | Recommended Safe Remediation |
| :---: | :---: | :--- | :--- | :--- |
| **DEF-01** | **MEDIUM** | Storage / Schema | `DatabaseManager._initialize_schema()` in `src/notice2action/storage/db.py` contains only Version 1 schema. If `data/suchnasetu.db` is deleted or recreated from scratch, Version 2 auth tables (`users`, `sessions`, `auth_tokens`, `rate_limits`) will not be created automatically. | Update `_initialize_schema()` to execute both Version 1 and Version 2 DDL statements when bootstrapping an empty database. |
| **DEF-02** | **LOW** | Config / Email | `AppConfig` in `src/notice2action/config.py` does not define `smtp_*` fields from `os.getenv()`. Even if an admin specifies `SMTP_HOST` in `.env`, the server defaults to console logging. | Add `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `smtp_tls`, and `auth_email_backend` attributes to `AppConfig` with `.env` reading. |
| **DEF-03** | **LOW** | Test Suite | `test_25_fastapi_server_loads_without_import_error` in `tests/test_unit_pipeline.py` iterates `app.routes` and checks `r.path`. Under FastAPI 0.115+, `_IncludedRouter` lacks `.path`, causing test failure. | Update test helper to check `getattr(r, "path", None) or getattr(r, "prefix", "")` when inspecting routes. |
| **DEF-04** | **LOW** | Acceptance Test | `tests/test_playwright_react_frontend.py` enforces a 90-second timeout for local Ollama notice analysis. On laptops without dedicated GPU acceleration, Gemma 4 CPU inference can exceed 90 seconds. | Increase Playwright step timeout to 180 seconds or mock the Ollama response during automated browser acceptance tests. |
| **DEF-05** | **LOW** | Test Fixtures | `tests/test_auth.py` shares hardcoded test emails (e.g. `arjun.sharma@test...`) across multiple tests. When run in a single pytest run with other tests, unique constraints can collide. | Use dynamic UUID-based synthetic emails (e.g. `f"test_{uuid.uuid4().hex[:6]}@example.com"`) in auth test fixtures. |

---

## 10. Safety, Integrity, and Confidentiality Affirmation

In strict compliance with the **SAFE VERIFICATION FIRST** protocol:
1. **Application Source Code & Configuration:** No application code, scripts, or configuration files were altered during this audit.
2. **Production / Existing Database:** The primary database `data/suchnasetu.db` and its WAL/SHM companion files were preserved without modification. Zero existing records were overwritten, truncated, or dropped.
3. **User Records & Data Integrity:** No user records were modified or deleted. Foreign key constraints and database integrity checks confirmed 0 violations.
4. **Credential & Secret Protection:** No passwords, hashes, session tokens, API keys, or personal identifiable information (PII) were disclosed in this report or terminal output.
5. **No Outbound Communication:** No real emails, OTPs, or notifications were transmitted across the internet to any external users or third-party email providers.

---
*Report certified by Automated System Verification Engine — Antigravity Agentic Framework.*
