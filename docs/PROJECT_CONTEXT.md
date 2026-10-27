# SochnaSetu AI — Project Context & System Architecture

> **Purpose:** Single source of truth for the SochnaSetu AI codebase architecture, database schemas, authentication lifecycle, API routing, and test commands. Refer to this document before making changes to avoid redundant audits.

---

## 1. System Overview

SochnaSetu AI is an accessibility-first "Notice-to-Action" platform that converts dense, complex government, civic, and institutional notices (PDFs, scanned images, Devanagari/English text) into structured facts, eligibility criteria, required documents, actionable checklists, timeline milestones, and multilingual plain-language summaries.

- **Stack:**
  - **Frontend:** React 19, TypeScript, Vite 8, Tailwind CSS v4, Lucide React icons, Vitest.
  - **Backend:** Python 3.11, FastAPI, Uvicorn, SQLite (WAL mode), Pydantic v2.
  - **OCR Engine:** Tesseract OCR (with `hin.traineddata` + `eng.traineddata`, OpenCV deskew/denoise preprocessing).
  - **AI Inference:** Multi-provider architecture supporting Local Ollama (`gemma2:2b`, `qwen2.5:3b`, `mistral:7b`), OpenRouter Cloud API (`google/gemini-2.0-flash-001`, `meta-llama/llama-3.3-70b-instruct`, etc.), and offline heuristic fallback.

---

## 2. Directory Layout

```
ps2/
├── data/
│   ├── suchnasetu.db              # Primary SQLite database (WAL mode, persistent)
│   ├── backups/                   # Online SQLite backups (gitignored)
│   └── samples/                   # Sample notices (synthetic & real gazettes)
├── docs/                          # Architecture, workflows, deployment guides
│   ├── PROJECT_CONTEXT.md         # Architecture, DB schema, auth flow, routes (this file)
│   ├── WORKFLOW.md                # AGY development workflow & rules
│   ├── BACKEND_DATABASE_AUDIT.md  # Detailed SQLite & auth verification audit
│   └── DEPLOYMENT_GUIDE.md        # Cloudflare Pages + Render deployment instructions
├── frontend/
│   ├── src/
│   │   ├── components/            # UI components (Header, Dropzone, OCRPanel, etc.)
│   │   ├── context/               # NoticeContext.tsx (Global state, auth, language)
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── i18n/                  # Translation engine (English, Hindi, etc.)
│   │   ├── services/              # apiClient.ts, api.ts (Backend communication)
│   │   ├── types/                 # TypeScript interfaces and DTOs
│   │   └── views/                 # Tab views (DashboardView, IngestionView, etc.)
│   ├── package.json               # Frontend dependencies & scripts
│   └── vite.config.ts             # Vite 8 config with proxy to backend (port 8000)
├── src/notice2action/
│   ├── api/
│   │   ├── server.py              # FastAPI application, CORS, routers, lifespans
│   │   └── auth_routes.py         # Registration, login, logout, me, sessions
│   ├── cli/                       # Command-line interface tools
│   ├── core/                      # Extraction pipelines, prompt builders, schemas
│   ├── llm/                       # Provider drivers (Ollama, OpenRouter, Fallback)
│   ├── ocr/                       # Tesseract wrapper and image preprocessors
│   ├── storage/
│   │   └── db.py                  # SQLite connection manager, schema migrations, WAL
│   ├── config.py                  # Settings, preflight diagnostics, env configuration
│   └── models.py                  # Pydantic models for domain entities
├── tests/                         # Pytest backend test suites
│   ├── test_backend_persisted_auth.py
│   ├── test_auth.py
│   ├── test_production_cloud_and_openrouter.py
│   └── test_multi_provider_llm.py
├── render.yaml                    # Infrastructure-as-code for Render deployment
└── start_all.bat                  # One-click Windows development supervisor
```

---

## 3. Database Architecture (SQLite)

- **Engine:** SQLite 3.x using write-ahead logging (`PRAGMA journal_mode=WAL`).
- **Path:** Controlled via `DATABASE_PATH` env var, defaults to `data/suchnasetu.db`.
- **Concurrency & Pragmas:**
  - `PRAGMA busy_timeout = 30000;` (Prevents database locked errors under load)
  - `PRAGMA synchronous = NORMAL;` (High write throughput while preserving integrity)
  - `PRAGMA foreign_keys = ON;` (Referential integrity enforced)
  - `PRAGMA cache_size = -64000;` (64MB in-memory page cache)

### Schema Inventory (18 Tables)

1. `schema_migrations`: Version tracking for database migrations.
2. `users`: User identity (`id`, `username`, `email`, `password_hash`, `role`, `is_active`, `created_at`, `updated_at`). Passwords hashed with Argon2id.
3. `auth_tokens`: Persistent sessions (`token_hash`, `user_id`, `created_at`, `expires_at`, `last_used_at`, `user_agent`, `ip_address`).
4. `sessions`: Session tracking tokens.
5. `user_preferences`: Citizen settings (`user_id`, `theme`, `language`, `email_notifications`, `sms_notifications`, `auto_save_notices`, `high_contrast`, `font_size`).
6. `saved_notices`: Bookmarked and analyzed notices (`id`, `user_id`, `document_id`, `title`, `issuing_authority`, `category`, `notice_date`, `deadline`, `summary`, `tags`, `is_starred`, `created_at`, `updated_at`).
7. `user_activities`: Audit log of user actions (`id`, `user_id`, `activity_type`, `title`, `description`, `document_id`, `metadata`, `created_at`).
8. `user_notifications`: User-directed alerts and milestone reminders (`id`, `user_id`, `title`, `message`, `type`, `is_read`, `link_url`, `created_at`).
9. `user_checklist_progress`: Checkbox completion states for user action plans (`user_id`, `task_id`, `completed`, `completed_at`).
10. `documents`: Ingested document records and raw text (`id`, `user_id`, `filename`, `file_hash`, `file_size`, `mime_type`, `raw_text`, `created_at`).
11. `analyses`: AI extraction results and structured JSON (`id`, `document_id`, `user_id`, `status`, `summary`, `facts`, `deadlines`, `eligibility`, `checklist`, `model_name`, `provider`, `created_at`).
12. `checklist_items`: Action plan items generated from notices.
13. `qa_interactions`: Question-and-answer exchanges anchored to document evidence.
14. `revision_comparisons`: Structural diffs between document versions.
15. `user_confirmations`: User confirmations of uncertain or inferred facts.
16. `demo_registry`: Tracked demo documents and sample fixtures.
17. `rate_limits`: IP-based rate limiting buckets.
18. `app_settings`: Global persistent runtime configuration.

---

## 4. Authentication Lifecycle & Guest Sandbox

### Registered Citizen Flow
1. **Registration (`POST /api/auth/register`):**
   - Requires `username`, `email`, `password`.
   - Validates email format, password complexity (min 8 chars, mixed case, digit).
   - Hashes password with Argon2id (`argon2-cffi`).
   - Automatically sets a secure `session_token` HttpOnly cookie.
2. **Login (`POST /api/auth/login`):**
   - Accepts username or email + password.
   - Verifies against Argon2id hash.
   - Generates high-entropy token, stores SHA-256 hash in `auth_tokens`.
   - Returns HttpOnly cookie `session_token` (and `access_token` in JSON body).
3. **Session Verification (`GET /api/auth/me`):**
   - Validates token against SQLite `auth_tokens`.
   - Returns authenticated user profile (`id`, `username`, `email`, `role`).
   - Returns `HTTP 401 Unauthorized` if no cookie is present (Standard REST behavior).
4. **Logout (`POST /api/auth/logout`):**
   - Deletes token record from SQLite.
   - Clears `session_token` cookie.

### Guest Sandbox Flow
- Unauthenticated visitors receive `HTTP 401` on `/api/auth/me`.
- Public dashboard endpoints (`/api/user/saved-notices`, `/api/user/weekly-tasks`, `/api/user/notifications`, `/api/user/activities`) use FastAPI's `get_current_user_or_guest`.
- Generates a deterministic pseudonymous guest ID (`guest_<sha256(ip)>`).
- Allows guests to interact with the dashboard, read sample fixtures, and test OCR without forced login.
- **Strict Isolation:** Guest queries filter by `user_id = "guest_..."`. Registered user data (`user_id = "<uuid>"`) is never visible to guest sessions.

---

## 5. API Route Inventory

| Route | Method | Description | Auth Mode |
|---|---|---|---|
| `/api/health` | GET | Preflight diagnostic (SQLite, OCR, LLM readiness) | Public |
| `/api/providers` | GET | List available LLM providers & active model | Public |
| `/api/samples` | GET | List built-in synthetic notices & gazettes | Public |
| `/api/auth/register` | POST | Register new account with Argon2id | Public |
| `/api/auth/login` | POST | Authenticate and issue session cookie | Public |
| `/api/auth/logout` | POST | Invalidate session token & clear cookie | Public |
| `/api/auth/me` | GET | Get current authenticated user profile | Required (401 if guest) |
| `/api/ingest/upload` | POST | Upload PDF or image for OCR processing | Guest or Authenticated |
| `/api/analyze` | POST | Run structured extraction pipeline | Guest or Authenticated |
| `/api/qa` | POST | Grounded Q&A against document evidence | Guest or Authenticated |
| `/api/compare` | POST | Compare two document revisions | Guest or Authenticated |
| `/api/user/saved-notices` | GET/POST | Manage bookmarked notices | Guest or Authenticated |
| `/api/user/weekly-tasks` | GET | Get upcoming deadlines & milestones | Guest or Authenticated |
| `/api/user/activities` | GET | Get recent user action history | Guest or Authenticated |
| `/api/user/notifications` | GET/POST | Fetch & mark notifications as read | Guest or Authenticated |
| `/api/user/checklist-progress` | GET/POST | Read & toggle checklist checkboxes | Authenticated Only |

---

## 6. Verification & Test Commands

### Backend Tests
```bash
# Full test suite
.\.venv\Scripts\python.exe -m pytest tests/

# Targeted authentication & persistence tests
.\.venv\Scripts\python.exe -m pytest tests/test_backend_persisted_auth.py tests/test_auth.py

# Multi-provider & Cloud deployment tests
.\.venv\Scripts\python.exe -m pytest tests/test_production_cloud_and_openrouter.py tests/test_multi_provider_llm.py
```

### Frontend Tests & Build
```bash
# Run Vitest unit tests
npm --prefix frontend test -- --run

# Run TypeScript compilation and Vite production build
npm --prefix frontend run build
```
