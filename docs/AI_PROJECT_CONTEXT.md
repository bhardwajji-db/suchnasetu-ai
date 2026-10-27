# SuchnaSetu AI — Authoritative Project Knowledge Base
> **AI_PROJECT_CONTEXT.md** — Evidence-based architecture reference generated from direct code inspection.
> Last verified: 2026-10-27 | Schema version: 5 | API version: 2.1.0
>
> **Rules for all future AI tasks:** Read this file first. Then read only the specific files needed for the task. Do not repeat a repository-wide analysis. Update this file only when architecture, API contracts, DB schema, config, or commands change.

---

## 1. Project Purpose & Status

**SuchnaSetu AI** (Notice-to-Action) is an accessibility-first platform that transforms dense government/institutional notices (PDFs, scans, Hindi/English text) into:
- Six structured legal core fields (authority, ref number, date, recipient, subject, action+deadline)
- Evidence-grounded plain-language summaries (Simple / Standard / Detailed reading levels)
- Action checklists with iCalendar export
- Eligibility engine (applicant profile vs. notice criteria)
- Revision ledger / corrigendum diffing
- Grounded Q&A (strict notice-text only, no hallucination)
- Cross-notice timeline workspace
- Multilingual support (10 Indian languages via i18n + backend translation)
- Voice guidance via Web Speech API

**Event:** Hacktoberfest 2026 HackDay — Track 1: Best Use of Gemma 4  
**Default inference:** 100% local air-gapped via Ollama (`gemma4:latest`)  
**Cloud providers:** OpenRouter, Google Gemini, Hugging Face (optional, key-required)

**Implementation status (verified):**
- ✅ Full FastAPI backend with all documented routes implemented in `server.py` (3940 lines)
- ✅ SQLite persistence with 5 applied schema migrations
- ✅ Auth system: Argon2id, HttpOnly session cookies, OTP email verification
- ✅ React 19 frontend with 12 views, tab-based navigation, i18n (10 languages)
- ✅ OCR: Tesseract + auto-detect + image preprocessing
- ✅ Multi-provider LLM factory (Ollama / OpenRouter / Gemini / HuggingFace)
- ✅ Evidence service, session store, relationship engine, revision engine
- ✅ Extensive test suite (~55 test files in `tests/`)
- ⚠️ `docs/PROJECT_CONTEXT.md` contains stale module paths (references non-existent `core/`, `cli/` dirs) — this file (`AI_PROJECT_CONTEXT.md`) is the authoritative source

---

## 2. Repository Structure

```
ps2/
├── src/notice2action/          # Python backend package
│   ├── api/
│   │   ├── server.py           # FastAPI app, all routes (~3940 lines)
│   │   └── auth_routes.py      # Auth endpoints (/api/auth/*)
│   ├── auth/
│   │   ├── auth_service.py     # AuthService: register, login, verify, session mgmt
│   │   ├── email_service.py    # Email delivery (console/SMTP backends)
│   │   ├── schemas.py          # Auth Pydantic schemas
│   │   └── security.py        # Argon2id hashing, token generation
│   ├── llm/
│   │   ├── base.py             # BaseLLMClient + exception hierarchy
│   │   ├── factory.py          # get_llm_client(), get_all_provider_statuses()
│   │   ├── ollama_client.py    # OllamaClient (local, gemma4:latest)
│   │   ├── openrouter_client.py
│   │   ├── gemini_client.py
│   │   └── huggingface_client.py
│   ├── services/
│   │   ├── evidence_service.py     # EvidenceService: line indexing, keyword search
│   │   ├── session_store.py        # SessionStore: thread-safe .sessions/ persistence
│   │   ├── eligibility_engine.py   # EligibilityEngine: criteria extraction + eval
│   │   ├── revision_engine.py      # RevisionEngine: field diffing between notices
│   │   ├── relationship_engine.py  # RelationshipEngine: AMENDMENT/EXTENSION/etc.
│   │   ├── trust_engine.py         # TrustEngine: evidence verification
│   │   ├── impact_engine.py        # PersonalImpactEngine: revision → user impact
│   │   ├── action_navigator_service.py  # ActionNavigatorService: personalized roadmap
│   │   ├── workspace_service.py    # Multi-notice workspace
│   │   └── weekly_planner_service.py   # 7-day task planner
│   ├── storage/
│   │   └── db.py               # DatabaseManager (SQLite, WAL, 5 migrations, ~2844 lines)
│   ├── analysis.py             # NoticeAnalyzer: LLM-based structured notice extraction
│   ├── checklist.py            # generate_action_checklist()
│   ├── config.py               # AppConfig dataclass, run_preflight_diagnostics()
│   ├── evaluator.py            # Evaluation / scoring
│   ├── followup.py             # FollowUpAssistant: grounded Q&A
│   ├── grounding.py            # Evidence grounding utilities
│   ├── ingestion.py            # ingest_pasted_text(), ingest_uploaded_file()
│   ├── language_detection.py   # detect_document_language()
│   ├── ocr.py                  # extract_text_from_image(), get_ocr_engine()
│   ├── schemas.py              # Core Pydantic schemas (StructuredNotice, SixCoreFields, etc.)
│   ├── security.py             # validate_uploaded_file(), SecurityValidationError
│   ├── summary.py              # generate_deterministic_summary()
│   ├── translation.py          # translate_summary(), translate_checklist(), SUPPORTED_LANGUAGES
│   └── tts.py                  # generate_audio_bytes() — gTTS wrapper
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Root: <I18nProvider><NoticeProvider><ApplicationLayout/>
│   │   ├── components/
│   │   │   ├── ApplicationLayout.tsx  # Tab router (switch on activeTab 0–11, 99=auth)
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MobileBottomNav.tsx
│   │   │   ├── auth/           # AuthLayout, AuthModal, Login/Signup/Verify/Reset pages
│   │   │   └── [12 other components]
│   │   ├── context/
│   │   │   └── NoticeContext.tsx  # Global state (~1262 lines), all app state + actions
│   │   ├── services/
│   │   │   ├── api.ts          # Auth API calls (loginAccount, registerAccount, fetchAuthMe, etc.)
│   │   │   └── apiClient.ts    # All backend API calls via typed apiClient object (~841 lines)
│   │   ├── views/              # 12 tab views (see Tab Map below)
│   │   ├── i18n/               # I18nContext, 10 language locales (en/hi/bn/ta/te/mr/gu/pa/kn/ur)
│   │   └── types/
│   │       ├── api.ts          # TypeScript interfaces matching backend schemas
│   │       └── index.ts
│   ├── package.json            # React 19, Vite 8, Tailwind 4, Vitest 5, TypeScript 6
│   └── vite.config.ts          # Vite config (proxy, env vars)
├── tests/                      # ~55 pytest test files
├── data/
│   ├── suchnasetu.db           # SQLite database (auto-created at startup)
│   └── uploads/                # Uploaded files (auto-created)
├── .sessions/                  # SessionStore JSON files (auto-created)
├── assets/tessdata/            # Optional local Tesseract language data
├── docs/                       # Architecture docs (see below)
├── scripts/                    # process_supervisor.py, setup.ps1, etc.
├── .env.example                # Canonical env variable reference
├── pyproject.toml              # Python package: notice2action, deps, pytest config
├── requirements.txt            # Pinned production dependencies
├── Procfile                    # Render/Heroku: uvicorn notice2action.api.server:app
├── Dockerfile                  # Multi-stage container build
├── docker-compose.yml          # App + Ollama containers
├── run_app.bat                 # Windows launcher → run_sochnasetu.ps1
├── start_all.bat               # Windows launcher → scripts/process_supervisor.py
└── run_sochnasetu.ps1          # PowerShell unified launcher
```

---

## 3. Frontend Architecture & Tab Routing

### Application Shell
- **Entry:** `main.tsx` → `App.tsx` → `I18nProvider` → `NoticeProvider` → `ApplicationLayout`
- **Routing:** Tab-based (integer `activeTab` in context, NOT React Router paths)
- **Tab 99:** Special — full-screen `AuthPageView` (login/signup)

### Tab Map (in `ApplicationLayout.tsx`)
| Tab | View | Purpose |
|-----|------|---------|
| 0 | `DashboardView` | Home, recent analyses, stats |
| 1 | `IngestionView` | Text paste / file upload / OCR |
| 2 | `GroundedFactsView` | Six core fields + evidence citations |
| 3 | `SummaryActionsView` | Plain language summary + checklist |
| 4 | `RevisionLedgerView` | Notice corrigendum comparison |
| 5 | `EligibilityEngineView` | Applicant profile + eligibility |
| 6 | `FollowUpQAView` | Grounded Q&A chat |
| 7 | `PersonalizedActionNavigatorView` | Personalized action roadmap |
| 8 | `CrossNoticeTimelineView` | Multi-notice workspace timeline |
| 9 | `NoticeHistoryView` | Saved/history notice list |
| 10 | `SettingsView` | Preferences, theme, accessibility |
| 11 | `DemoLibraryView` | Curated demo notices |
| 99 | `AuthPageView` | Auth (login / signup) |

### State Management
- **`NoticeContext.tsx`** (~1262 lines): Single React Context with 60+ state vars
- Key state: `sessionId`, `rawNoticeText`, `ocrResult`, `structuredNotice`, `sixCoreFields`, `summaryEn/Hi`, `checklistEn/Hi`, `currentUser`, `activeTab`, `providers`, `selectedLang`, `readingLevel`, `evidenceDrawer`
- Checklist completion persisted in `localStorage` (key: `suchnasetu_checklist_completed_<fingerprint>`)
- History persisted in `localStorage` (key: `notice2action_history`)
- Theme persisted in `localStorage` (key: `suchnasetu_theme`)

### API Clients (Frontend)
- **`services/api.ts`**: Auth-only calls (`loginAccount`, `registerAccount`, `fetchAuthMe`, `logoutAccount`, `requestPasswordReset`, `completePasswordReset`, `verifyEmailAddress`, `resendEmailVerification`, `fetchGuestStatus`)
- **`services/apiClient.ts`**: All other backend calls (all methods on `apiClient` object). Base URL auto-resolved from `VITE_API_BASE_URL` env var, or origin-relative, or `http://127.0.0.1:8000` fallback.

### i18n
- 10 languages: `en`, `hi`, `bn`, `ta`, `te`, `mr`, `gu`, `pa`, `kn`, `ur`
- Urdu uses RTL (`dir="rtl"`)
- `I18nContext.tsx` with `useTranslation()` hook
- Language persisted to `localStorage` (`suchnasetu_user_language`) and synced with backend preferences if authenticated

---

## 4. Backend Architecture & API Endpoints

**Entry point:** `src/notice2action/api/server.py`  
**Module:** `notice2action.api.server:app`  
**Start command:** `python -m uvicorn notice2action.api.server:app --app-dir src --host 0.0.0.0 --port 8000`

### Middleware Stack (applied in order)
1. `CORSMiddleware` — configured from `config.get_cors_origins()` + RFC1918 dev regex
2. `request_id_and_audit_logging` — attaches `X-Request-ID`, times requests, redacts sensitive query params
3. `verify_csrf_and_origin` — blocks state-changing requests from untrusted origins in production

### All Verified API Routes

**Health & System**
| Method | Path | Handler | Notes |
|--------|------|---------|-------|
| GET | `/health` | `root_health_check` | Lightweight 200 OK for load balancers |
| GET | `/healthz` | `root_health_check` | Alias |
| GET | `/api/health` | `get_health` | Full preflight diagnostics |
| GET | `/api/providers` | `get_providers` | All LLM provider statuses |
| POST | `/api/providers/select` | `select_provider` | Switch active LLM provider |
| GET | `/api/models/status` | `get_models_status` | Ollama loaded models / VRAM |
| POST | `/api/models/warmup` | `warmup_model_endpoint` | Preload Ollama model |
| POST | `/api/models/unload` | `unload_model_endpoint` | Free VRAM |

**Authentication** (prefix: `/api/auth`)
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/auth/register` | Argon2id hash, sets HttpOnly cookie |
| POST | `/api/auth/verify-email` | Token or 6-digit code |
| POST | `/api/auth/resend-verification` | Rate-limited |
| POST | `/api/auth/login` | Argon2id verify, sets session cookie |
| POST | `/api/auth/logout` | Deletes session + cookie |
| GET | `/api/auth/me` | Returns `UserPublic` (auth required) |
| POST | `/api/auth/forgot-password` | OTP or link |
| POST | `/api/auth/reset-password` | Argon2id re-hash, revoke old sessions |
| GET | `/api/auth/guest-status` | Remaining guest quota |

**Notice Processing**
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/samples` | List demo fixtures |
| GET | `/api/samples/{filename}` | Fetch fixture content |
| POST | `/api/ingest/text` | Sanitize + SHA-256 fingerprint |
| POST | `/api/ingest/upload` | File upload (PDF/image/text) |
| POST | `/api/ocr` | Tesseract / RapidOCR on image |
| POST | `/api/analyze` | Main analysis: LLM + summary + checklist |
| POST | `/api/confirm` | Confirm uncertain OCR field → regenerate |
| POST | `/api/summary/reading-level` | Adjust reading level |
| POST | `/api/followup` | Grounded Q&A |
| POST | `/api/tts` | Text-to-speech (gTTS) |
| POST | `/api/language/detect` | Detect document language |
| GET | `/api/documents` | List persisted documents |

**Evidence**
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/evidence/search` | Keyword/semantic evidence search |
| POST | `/api/trust/verify-evidence` | Verify excerpt against source text |

**Revision & Relationships**
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/relationships/detect` | AMENDMENT/EXTENSION/etc. detection |
| POST | `/api/revision-ledger/compare` | Field-by-field diff |
| POST | `/api/impact/evaluate` | Personal impact of revisions |

**Eligibility & Actions**
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/eligibility/extract-criteria` | Extract machine-evaluable criteria |
| POST | `/api/eligibility/evaluate` | Evaluate applicant profile |
| POST | `/api/actions/generate` | Personalized action roadmap |
| POST | `/api/actions/update-status` | Update action item status |

**Workspace**
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/workspace/notices` | Multi-notice workspace list |
| POST | `/api/workspace/notices` | Add to workspace |
| GET | `/api/workspace/timeline` | Cross-notice timeline |
| POST | `/api/workspace/clear` | Clear workspace |

**User-Specific (auth required)**
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/user/saved-notices` | List saved notices |
| POST | `/api/user/saved-notices/{doc_id}` | Save notice |
| DELETE | `/api/user/saved-notices/{doc_id}` | Unsave notice |
| GET | `/api/user/weekly-tasks` | 7-day task planner |
| POST | `/api/user/weekly-tasks/query` | NL query on tasks |
| GET | `/api/user/notifications` | User notifications |
| PUT | `/api/user/notifications/{id}/read` | Mark notification read |
| POST | `/api/user/notifications/mark-all-read` | |
| DELETE | `/api/user/notifications/{id}` | Dismiss |
| GET | `/api/user/activities` | Activity audit trail |
| GET | `/api/user/preferences` | Load preferences |
| POST | `/api/user/preferences` | Save preferences |

**Export & Checklist**
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/export/markdown` | Export dossier as .md |
| POST | `/api/export/ics` | Export checklist as .ics |
| POST | `/api/checklist/{id}/toggle` | Persist checklist item completion |

**Demo Library**
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/demo-library` | List demo notices (filter by lang/format/category) |
| POST | `/api/demo-library/{id}/load` | Load a demo item |

**Static SPA serving** (production): FastAPI serves the Vite build at `/*`

---

## 5. Database

### Location Resolution
- **Env var:** `DATABASE_PATH` (default: `data/suchnasetu.db` relative to project root)
- **Runtime:** `DEFAULT_DB_PATH = Path(os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "data" / "suchnasetu.db")))`
- **`PROJECT_ROOT`** = `Path(__file__).resolve().parent.parent.parent` from `config.py` (= root of `ps2/`)
- **Uploads dir:** `UPLOADS_DIR` env var (default: `data/uploads/`)

### DatabaseManager (`storage/db.py`)
- `DatabaseManager` class: thread-safe via `threading.RLock()` + `threading.local()` per-thread connections
- WAL mode: `PRAGMA journal_mode=WAL` not explicitly set but `PRAGMA busy_timeout=30000` and `PRAGMA synchronous=NORMAL` are
- `PRAGMA foreign_keys=ON` enabled
- `row_factory = sqlite3.Row` (dict-like row access)
- Singleton access via `get_db()` function

### Schema Migrations (version tracking in `schema_migrations` table)

| Version | Tables Created | Description |
|---------|---------------|-------------|
| 1 | `documents`, `analyses`, `checklist_items`, `user_confirmations`, `qa_interactions`, `revision_comparisons`, `demo_registry`, `app_settings` | Initial production schema |
| 2 | `users`, `sessions`, `auth_tokens`, `rate_limits` | Auth + session persistence |
| 3 | `saved_notices` | User-isolated saved notices |
| 4 | `user_notifications`, `user_activities` | Notifications + activity timeline |
| 5 | `user_preferences`, `user_checklist_progress` | Preferences + persistent checklist |

### Current Schema Version: **5**

### Key Table Relationships
```
users (id) ──→ sessions (user_id) ON DELETE CASCADE
users (id) ──→ auth_tokens (user_id) ON DELETE CASCADE
users (id) ──→ user_preferences (user_id) ON DELETE CASCADE
documents (id) ←── analyses (document_id) ON DELETE SET NULL
analyses (id) ──→ checklist_items (analysis_id) ON DELETE CASCADE
documents (id) ←── qa_interactions (document_id) ON DELETE SET NULL
documents (id) ←── saved_notices (document_id), UNIQUE(user_id, document_id)
```

### Important: `saved_notices.user_id` is a plain `TEXT` (not FK to `users`)
This means saves persist even if a user account is deleted (no cascade).

---

## 6. Authentication

### Flow
1. **Register:** `POST /api/auth/register` → Argon2id hash → user in `users` table → session token in `sessions` → HttpOnly cookie set
2. **Email verification:** Optional (OTP code or link token stored in `auth_tokens` with `token_type='verify'`). Registration creates authenticated session immediately.
3. **Login:** `POST /api/auth/login` → Argon2id verify → session token in `sessions` → HttpOnly cookie
4. **Session resolution:** `_extract_session_token()` checks: cookie `suchnasetu_session` → `Authorization: Bearer <token>` → `X-Session-Token` header
5. **Current user:** `auth_service.get_user_by_session_token(token)` — looks up `sessions` table by `HMAC-SHA256(token)` hash
6. **Guest mode:** `get_current_user_or_guest()` dependency allows unauthenticated access with IP-based rate limiting
7. **Logout:** `POST /api/auth/logout` → `auth_service.logout_session(token)` → delete cookie

### FastAPI Dependencies
- `get_current_user(request)` — strict auth, raises HTTP 401 if no valid session
- `get_current_user_or_guest(request)` — auth OR guest (with remaining quota)
- `get_optional_current_user(request)` — returns `None` for guests

### Cookie Configuration
- Name: `suchnasetu_session` (from `config.auth_cookie_name`)
- `httponly=True`, `path="/"`
- `secure=`: auto-detected from HTTPS/proxy headers or `AUTH_COOKIE_SECURE` env
- `samesite=`: `AUTH_COOKIE_SAMESITE` env (default: `"lax"`)
- Default session expire: 168 hours (7 days); `remember_me=True` → 720 hours (30 days)

### Security
- Passwords: Argon2id via `argon2-cffi`
- Session tokens: stored as `HMAC-SHA256` hash in DB (plain tokens never stored)
- OTP codes: 6-digit, HMAC-SHA256 hashed in `auth_tokens`
- CSRF protection: middleware blocks state-changing requests from untrusted origins in production
- File uploads: `validate_uploaded_file()` in `security.py` (size, extension, mime type checks)

---

## 7. AI & OCR Processing Pipelines

### OCR Pipeline
1. File arrives at `POST /api/ocr` (multipart form)
2. `validate_uploaded_file()` → size/extension/mime checks
3. `extract_text_from_image(image_bytes, lang, enhance_contrast, engine)` in `ocr.py`
4. Preprocessing: deskew, denoise, contrast enhancement (Pillow/OpenCV)
5. Tesseract: `pytesseract.image_to_data()` with confidence scoring
6. Uncertainty detection: low confidence scores, tentative/ambiguous terms
7. Returns `OCRResponse` with: `extracted_text`, `confidence_score`, `is_uncertain`, `uncertain_spans`, `engine_used`
8. Auto-fallback: if RapidOCR requested but unavailable → falls back to Tesseract

### Analysis Pipeline
1. `POST /api/analyze` with `notice_text`, `reading_level`, `target_language`, optional `session_id`
2. `detect_document_language(text)` → source language detection
3. `NoticeAnalyzer(llm_client).analyze(text)` → `StructuredNotice` + `SixCoreFields`
4. `generate_deterministic_summary(notice, reading_level)` → `PlainLanguageSummary` (EN)
5. `generate_action_checklist(notice)` → `ActionChecklist` (EN)
6. `translate_summary_to_hindi(summary)` + `translate_checklist_to_hindi(checklist)` → Hindi versions
7. If `target_language ≠ "en"` and `≠ "hi"`: `translate_summary(summary, lang)` + `translate_checklist(checklist, lang)`
8. `evidence_service.index(text)` → builds in-memory line/token index
9. Persist to `analyses` and `checklist_items` tables
10. Returns `AnalyzeResponse` with all versions + `session_id` + `fingerprint` + `duration_seconds`

### LLM Factory
```python
# factory.py
PROVIDER_MAP = {
    "ollama": OllamaClient,
    "openrouter": OpenRouterClient,
    "gemini": GeminiClient,
    "huggingface": HuggingFaceClient,
}
# get_llm_client(provider_name?) → BaseLLMClient
```
- Active provider stored in `config.llm_provider` (mutable at runtime via `/api/providers/select`)
- Provider switch is thread-safe via `_PROVIDER_LOCK`

### Evidence Service
- `EvidenceService` singleton in `services/evidence_service.py`
- Indexes notice text into 1-based line numbers + token inverted index
- `evidence_service.search(query, notice_text, max_results)` → `List[EvidenceCitation]`
- Used for grounded Q&A to prevent hallucination

### Session Store
- `SessionStore` in `services/session_store.py`
- Stores session state in `.sessions/` directory as JSON files
- Thread-safe, TTL-based expiry (default 24h)
- Isolates analyses, Q&A context, evidence index per session

---

## 8. Configuration & Environment

### `AppConfig` Dataclass (`config.py`)
All values loaded from environment variables (via `python-dotenv` loading `.env`).

| Env Variable | Default | Description |
|-------------|---------|-------------|
| `APP_ENV` | `development` | `development`, `production`, `test` |
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `8000` | Server port |
| `AI_PROVIDER` / `LLM_PROVIDER` | `ollama` | Active LLM provider |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Local Ollama endpoint |
| `OLLAMA_MODEL` | `gemma4:latest` | Ollama model name |
| `OLLAMA_TIMEOUT_SECONDS` | `180` | Inference timeout |
| `GEMINI_API_KEY` | — | Google Gemini key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | |
| `OPENROUTER_API_KEY` | — | |
| `OPENROUTER_MODEL` | `google/gemma-4-26b-a4b-it:free` | |
| `HF_TOKEN` / `HUGGINGFACE_API_KEY` | — | HuggingFace token |
| `HF_MODEL_ID` / `HUGGINGFACE_MODEL` | `google/gemma-4-26B-A4B` | |
| `OCR_ENGINE` | `tesseract` | `tesseract` or `rapidocr` |
| `TESSERACT_CMD` | Auto-detected | Path to tesseract.exe |
| `TESSDATA_PREFIX` | Auto-detected | tessdata directory |
| `DATABASE_PATH` | `data/suchnasetu.db` | SQLite file path |
| `UPLOADS_DIR` | `data/uploads` | Uploaded files directory |
| `SESSION_STORAGE_DIR` | `.sessions` | SessionStore directory |
| `SESSION_TTL_HOURS` | `24` | Session expiry |
| `AUTH_SECRET_KEY` | `suchnasetu-dev-insecure-...` | **Change in production!** |
| `AUTH_COOKIE_SECURE` | `false` | HTTPS-only cookies |
| `AUTH_COOKIE_SAMESITE` | `lax` | Cookie SameSite policy |
| `AUTH_EMAIL_BACKEND` | `console` | `console` or `smtp` |
| `CORS_ALLOWED_ORIGINS` | localhost variants | Comma-separated list |
| `AUTH_PUBLIC_APP_URL` | `http://localhost:5173` | Frontend URL |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max file upload size |
| `MAX_PDF_PAGES` | `30` | PDF page limit |
| `GUEST_RATE_LIMIT_PER_WINDOW` | `10` | Guest analyses per 10 min |
| `DEV_UNLIMITED_GUEST_QUOTA` | `true` (non-prod) | Bypass guest quota in dev |

### Tesseract Auto-Detection (`_find_tesseract_cmd()`)
Order: `TESSERACT_CMD` env → Windows default paths → system PATH `shutil.which`

### Frontend Env Variable
| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Override backend URL (e.g. `http://localhost:8000`). If unset, uses origin-relative. |

---

## 9. Startup, Build & Test Commands

### Backend (Development)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
# or with uv:
uv sync

# Start backend
python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000 --reload

# Run tests
python -m pytest tests/ -v --tb=short
# Skip live Ollama-dependent tests:
python -m pytest tests/ -v --tb=short -m "not live"
```

### Frontend (Development)
```powershell
cd frontend
npm install
npm run dev         # Vite dev server on http://localhost:5173
npm run build       # TypeScript compile + Vite build
npm run test        # Vitest run (all tests)
npm run test:watch  # Vitest watch mode
npm run lint        # oxlint
npm run preview     # Preview production build
```

### Windows One-Click Launch
```batch
run_app.bat          # → run_sochnasetu.ps1 (preferred)
start_all.bat        # → scripts/process_supervisor.py (via .venv Python)
```

### Production (Docker)
```bash
docker-compose up --build   # App on :8000, Ollama on :11434
```

### Production (Render / Heroku)
```
# Procfile
web: python -m uvicorn notice2action.api.server:app --app-dir src --host 0.0.0.0 --port ${PORT:-8000}
```

---

## 10. Key Dependencies

### Backend (Python)
| Package | Version | Role |
|---------|---------|------|
| `fastapi` | ≥0.110.0 | REST framework |
| `uvicorn` | ≥0.29.0 | ASGI server |
| `pydantic` | ≥2.7.0 | Schema validation |
| `pytesseract` | ≥0.3.10 | OCR wrapper |
| `Pillow` | ≥10.0.0 | Image preprocessing |
| `requests` | ≥2.31.0 | HTTP client (Ollama, health checks) |
| `python-dotenv` | ≥1.0.0 | .env loading |
| `gTTS` | ≥2.5.0 | Text-to-speech |
| `pypdf` | ≥4.0.0 | PDF text extraction |
| `argon2-cffi` | ≥23.1.0 | Password hashing |
| `email-validator` | ≥2.0.0 | Email validation |
| `python-multipart` | ≥0.0.9 | File upload support |

### Frontend (Node)
| Package | Version | Role |
|---------|---------|------|
| `react` | ^19.3.1 | UI framework |
| `react-dom` | ^19.3.1 | DOM renderer |
| `react-router-dom` | ^7.18.4 | (installed but **not used for routing** — tab-based instead) |
| `tailwindcss` | ^4.3.3 | CSS utility framework |
| `lucide-react` | ^1.59.0 | Icons |
| `vite` | ^8.3.4 | Build tool |
| `typescript` | ~6.0.3 | Type checking |
| `vitest` | ^5.0.5 | Test runner |
| `@testing-library/react` | ^16.3.3 | Component testing |

---

## 11. Module Relationship Architecture Map

### Primary Data Flow
```
Frontend (NoticeContext.tsx)
  → apiClient.analyzeNotice(text, lang, level)
  → POST /api/analyze
  → server.py: analyze_notice()
      → detect_document_language() [language_detection.py]
      → NoticeAnalyzer(get_llm_client()) [analysis.py + llm/factory.py]
      → generate_deterministic_summary() [summary.py]
      → generate_action_checklist() [checklist.py]
      → translate_summary_to_hindi() [translation.py]
      → evidence_service.index(text) [services/evidence_service.py]
      → db.save_analysis() [storage/db.py]
  → AnalyzeResponse → NoticeContext state update → View re-render
```

### Auth Flow
```
Frontend (AuthPageView → LoginPage)
  → api.loginAccount(email, password)
  → POST /api/auth/login
  → auth_routes.py: login()
      → auth_service.login_user() [auth/auth_service.py]
          → DB query users table, Argon2id verify
          → Create session in sessions table
          → Return session_token
      → response.set_cookie(suchnasetu_session, token, httponly=True)
  → Frontend: fetchAuthMe() → GET /api/auth/me
  → NoticeContext.setCurrentUser(user)
```

### OCR Flow
```
Frontend (IngestionView/OCRPanel)
  → apiClient.runOCR(file, lang, enhance_contrast)
  → POST /api/ocr (multipart)
  → server.py: run_ocr_endpoint()
      → validate_uploaded_file() [security.py]
      → extract_text_from_image() [ocr.py]
          → Image preprocessing (deskew, denoise, contrast)
          → pytesseract or RapidOCR
          → Confidence scoring + uncertainty detection
  → OCRResponse → setOcrResult() → rawNoticeText updated
```

### Evidence Trust Verification
```
Frontend (EvidenceInspectorDrawer)
  → apiClient.verifyEvidence(noticeText, excerpt, claim)
  → POST /api/trust/verify-evidence
  → server.py: verify_evidence_endpoint()
      → TrustEngine.verify() [services/trust_engine.py]
          → Exact/fuzzy match excerpt against indexed notice
          → Confidence scoring
  → VerifyEvidenceResponse → EvidenceDrawer state
```

### Configuration → Service Initialization
```
AppConfig (config.py, loaded at import)
  ├── config.llm_provider → get_llm_client() → OllamaClient / GeminiClient / etc.
  ├── config.tesseract_cmd → pytesseract.pytesseract.tesseract_cmd
  ├── config.tessdata_dir → os.environ["TESSDATA_PREFIX"]
  ├── config.session_storage_dir → SessionStore path
  └── config.db_path (DEFAULT_DB_PATH) → DatabaseManager
```

---

## 12. Existing Tests

### Backend Tests (`tests/`)
~55 test files covering:
- `test_api_endpoints.py` — API route tests
- `test_auth.py`, `test_auth_and_real_db_persistence.py`, `test_backend_persisted_auth.py`, `test_deployment_and_auth_e2e.py` — Auth flows
- `test_storage_db.py`, `test_database_migrations.py` — DB & migrations
- `test_eligibility_engine.py`, `test_evidence_trust_engine.py` — Service engines
- `test_revision_ledger.py`, `test_cross_notice_intelligence.py` — Revision features
- `test_unit_pipeline.py`, `test_ncl_end_to_end_analysis.py`, `test_master_e2e_acceptance.py` — Pipeline
- `test_ollama_integration.py`, `test_live_gemma4.py`, `test_multi_provider_llm.py` — LLM (marked `live`)
- `test_gazette_ocr_benchmark.py`, `test_hindi_ocr.py`, `test_pdf_ingestion.py` — OCR
- `test_playwright_react_frontend.py`, `test_playwright_interactive_inventory.py`, `test_theme_playwright.py` — Browser E2E
- `test_security_remediations.py`, `test_reliability_and_privacy.py` — Security
- `test_weekly_planner_and_saved_notices.py`, `test_notifications_and_activities.py` — User features

### Frontend Tests (`frontend/src/test/`)
~24 Vitest/React Testing Library files covering each major component and view.

### Test Markers
- `live` marker: tests requiring live Ollama + Gemma 4 → skip with `-m "not live"`

### pytest Configuration (`pyproject.toml`)
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"
```

---

## 13. Known Issues & Limitations

### Verified
1. **`docs/PROJECT_CONTEXT.md` is stale**: References module paths (`core/`, `cli/`, `hooks/`) that don't exist in the actual codebase. Use `AI_PROJECT_CONTEXT.md` instead.
2. **`react-router-dom` installed but unused**: Navigation is purely tab-based (`activeTab` integer). Deep-linking to specific views via URL is not supported.
3. **Session provider override is runtime-only**: Changing `config.llm_provider` via `/api/providers/select` is in-process only — not persisted to disk. Restarts revert to `.env` setting.
4. **WAL mode not explicitly set**: `db.py` does not execute `PRAGMA journal_mode=WAL` — uses SQLite default (DELETE mode). This limits concurrent read/write performance.
5. **`saved_notices.user_id` is not a FK**: No ON DELETE CASCADE from `users`. Orphaned saves if user is deleted.
6. **Guest quota bypass in development**: `DEV_UNLIMITED_GUEST_QUOTA=true` by default in non-production — analysis quota is not enforced.
7. **`auth_cookie_name` attribute**: Code references `getattr(config, "auth_cookie_name", "suchnasetu_session")` but `auth_cookie_name` is not defined in `AppConfig` — always falls back to default `"suchnasetu_session"`.
8. **`auth_session_expire_hours` attribute**: Referenced via `getattr(config, "auth_session_expire_hours", 168)` but not defined in `AppConfig` — always uses default 168h.

### Unverified Areas
- Full implementation of `weekly_planner_service.py` (not inspected — assumed functional based on test file existence)
- `scripts/process_supervisor.py` internals
- Playwright test execution status (requires running frontend)
- Live Ollama/Gemma 4 inference behavior (not testable without model running)
- Email delivery via SMTP (not testable without mail server)

---

## 14. Security Considerations & Invariants

1. **Never commit real API keys** — all cloud provider keys via env vars only
2. **Auth secret key**: `AUTH_SECRET_KEY` must be changed for production — default `suchnasetu-dev-*` is explicitly detected and blocked in production mode
3. **CORS**: `allow_credentials=True` → wildcards forbidden → must list exact origins
4. **CSRF middleware**: Active for POST/PUT/DELETE/PATCH in production
5. **File uploads**: `validate_uploaded_file()` enforces size, extension allowlist, MIME type
6. **Session tokens**: Only HMAC-SHA256 hashes stored in DB — plain tokens never persisted
7. **Argon2id**: Industry-standard password hashing — no MD5/SHA1/bcrypt
8. **HttpOnly cookies**: Session token not accessible to JavaScript
9. **Guest rate limiting**: IP-based via `rate_limits` table — exhausted guests get HTTP 429
10. **OCR security warning**: Pasted text with suspicious patterns (possible injection) triggers `security_warning` in `IngestTextResponse`

---

## 15. Troubleshooting

### Backend Won't Start
- Check `python -m uvicorn notice2action.api.server:app --app-dir src` from project root
- Ensure `.venv` activated: `.\.venv\Scripts\Activate.ps1`
- Missing deps: `pip install -r requirements.txt`
- Port conflict: change `PORT` in `.env`

### Ollama Connection Error
- Start Ollama: `ollama serve`
- Pull model: `ollama run gemma4:latest`
- Check OLLAMA_BASE_URL in `.env` (default: `http://127.0.0.1:11434`)
- Verify: `curl http://127.0.0.1:11434/api/tags`

### OCR Not Working
- Tesseract not found: set `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`
- Hindi OCR fails: ensure `hin.traineddata` in tessdata dir
- Set `TESSDATA_PREFIX` to correct tessdata directory

### Auth Cookie Not Sent
- Vite proxy must forward `/api/*` requests to backend port 8000
- Check `vite.config.ts` for proxy configuration
- `CORS_ALLOWED_ORIGINS` must include frontend origin exactly
- `credentials: 'include'` must be on all fetch calls (verified in `api.ts` and `apiClient.ts`)

### Database Issues
- Auto-created on first startup at `data/suchnasetu.db`
- Schema migrations run automatically — no manual migration needed
- If corrupted: delete `data/suchnasetu.db` (data loss) — will recreate fresh

### Frontend Build Issues
- Ensure `node_modules` exists: `cd frontend && npm install`
- TypeScript errors: `npm run build` shows type errors
- Test failures: `npm run test` — check jsdom environment

---

## 16. Areas Requiring Special Care

1. **`server.py` is monolithic (3940 lines)**: All API routes in one file. Changes must be careful not to break unrelated routes. Always locate the specific route function before editing.
2. **`NoticeContext.tsx` is the single state store (1262 lines)**: Changes to the context interface ripple across all 12 views and many components.
3. **DB schema migrations**: New tables/columns must increment `SCHEMA_VERSION` and add a new `if N not in applied_versions` block in `_initialize_schema()`. Idempotent pattern is critical.
4. **Translation invariants**: `translation.py` must preserve all date/monetary/reference number entities without translation distortion. This is tested explicitly.
5. **Evidence grounding**: `FollowUpAssistant` and `TrustEngine` must ONLY cite verbatim content from the notice. Adding new AI calls in these paths risks hallucination.
6. **CORS + CSRF**: Any new non-production origin must be added to `CORS_ALLOWED_ORIGINS`. Any new state-changing endpoint is automatically protected by `verify_csrf_and_origin` middleware.
7. **Analysis cache**: `_ANALYSIS_CACHE` dict (max 64 entries, `_CACHE_LOCK`) is in-process only. Concurrent workers will have separate caches.
8. **Thread safety**: `DatabaseManager` uses `threading.local()` for per-thread connections + `threading.RLock()` for schema init. New DB methods must not create raw connections outside this pattern.
9. **Guest quota**: Analysis endpoint increments guest quota counter. Adding new LLM-calling endpoints should decide whether to apply quota.
10. **`pyproject.toml` vs `requirements.txt`**: Both maintained. `pyproject.toml` defines package; `requirements.txt` is for deployment pip installs.
