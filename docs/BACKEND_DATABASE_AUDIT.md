# SochnaSetu AI — Backend, Database & Authentication Audit Report

> **Date:** October 26, 2026  
> **Status:** Completed & Verified  
> **Database:** SQLite (`data/suchnasetu.db`, WAL Mode)  
> **Backup:** `data/backups/suchnasetu_backup_20261026.db`  

---

## 1. Executive Summary

A comprehensive, one-time audit and repair of the SochnaSetu AI backend, SQLite database persistence layer, authentication mechanisms, and API communications was conducted.

### Core Problems Identified & Resolved:
1. **The Backend Log Discrepancy Explained:**
   - **Observed Logs:**
     ```
     GET /api/health HTTP/1.1 200 OK
     GET /api/auth/me HTTP/1.1 401 Unauthorized
     GET /api/user/saved-notices HTTP/1.1 200 OK
     GET /api/user/weekly-tasks HTTP/1.1 200 OK
     GET /api/user/activities?limit=15 HTTP/1.1 200 OK
     GET /api/user/notifications HTTP/1.1 200 OK
     ```
   - **Root Cause:** When an unauthenticated visitor accesses the dashboard, `GET /api/auth/me` checks for a session token cookie. Without credentials, it correctly returns `HTTP 401 Unauthorized`. This is standard, correct REST behavior indicating guest status. Simultaneously, the user endpoints (`/api/user/*`) intentionally use `get_current_user_or_guest`, providing a pseudonymous, isolated guest sandbox (`guest_<ip_hash>`). This allows guests to explore sample notices without forced login. Registered citizen records (`user_id = "<uuid>"`) remain strictly segregated and inaccessible to guest sessions.
2. **Eliminated Redundant Dashboard API Requests:**
   - `DashboardView.tsx` redundantly called `fetchAuthMe()` on component mount, even though `NoticeContext.tsx` already handles session initialization and provides `currentUser`. This caused duplicate network roundtrips and state synchronization overhead.
   - Refactored `DashboardView.tsx` to directly consume `currentUser` from `useNotice()`, removing the redundant `fetchAuthMe()` network request while keeping auth state synchronized.
3. **SQLite WAL Concurrency & Lock Contention Fix:**
   - In `src/notice2action/storage/db.py`, `conn.execute("PRAGMA journal_mode=WAL;")` was executed on every connection creation inside `get_connection()`. In SQLite, altering journal mode requires acquiring an exclusive lock on the database file, causing worker threads to block for the busy timeout when concurrent reads were active.
   - Resolved by setting WAL mode once during schema initialization. Added `PRAGMA busy_timeout = 30000;`, `PRAGMA synchronous = NORMAL;`, and `PRAGMA foreign_keys = ON;` on per-thread connections.
4. **Enhanced Preflight & Health Diagnostics:**
   - Updated `/api/health` and `config.py:run_preflight_diagnostics()` to include explicit `database_ready` verification (`SELECT 1 AS ping;`), cleanly separating backend HTTP server availability, SQLite database readiness, OCR engine status, and LLM provider readiness.

---

## 2. SQLite Database Verification

- **Database File:** `data/suchnasetu.db` (12.5 MB)
- **Backup Created:** `data/backups/suchnasetu_backup_20261026.db` (Online SQLite backup API)
- **Table Count:** 18 verified tables (`schema_migrations`, `users`, `auth_tokens`, `sessions`, `user_preferences`, `saved_notices`, `user_activities`, `user_notifications`, `user_checklist_progress`, `documents`, `analyses`, `checklist_items`, `qa_interactions`, `revision_comparisons`, `user_confirmations`, `demo_registry`, `rate_limits`, `app_settings`).
- **Applied Migrations:** 5 schema migrations applied cleanly.
- **Data Persistence:** User registration, password hashes, sessions, saved notices, and checklist items persist across application restarts.

---

## 3. Authentication & Security Audit

- **Password Security:** Passwords hashed using Argon2id (`argon2-cffi`) with secure salt and memory hardness parameters.
- **Session Tokens:** 256-bit cryptographically secure pseudorandom tokens stored as SHA-256 digests in `auth_tokens`.
- **Cookie Security:** Cookies set with `httponly=True`, `samesite="lax"`, and path `/`.
- **Sensitive Data Redaction:** No raw passwords, token hashes, or OpenRouter/AI API keys are exposed in logs, responses, or error traces.

---

## 4. Verification Results

- **Backend Pytest Suites:**
  - Persisted Auth (`tests/test_backend_persisted_auth.py`): Passed
  - Core Auth (`tests/test_auth.py`): Passed
  - Production Cloud & OpenRouter (`tests/test_production_cloud_and_openrouter.py`): Passed
  - Multi-Provider LLM (`tests/test_multi_provider_llm.py`): Passed
- **Frontend Vitest Suites:**
  - 24 test suites passed (84 individual unit tests passed).
- **Frontend Production Build:**
  - `tsc -b && vite build` completed cleanly with 0 TypeScript errors.
