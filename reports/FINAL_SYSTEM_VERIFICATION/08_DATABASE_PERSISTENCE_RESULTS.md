# 08 — DATABASE PERSISTENCE & STORAGE AUDIT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Storage Layer Architecture

SochnaSetu AI employs an acid-compliant, local-first SQLite database architecture at `data/suchnasetu.db` with Write-Ahead Logging (WAL) enabled:

- **Database File:** `data/suchnasetu.db`
- **Engine:** Python standard `sqlite3` + WAL (`PRAGMA journal_mode=WAL`)
- **Foreign Keys:** Enforced (`PRAGMA foreign_keys=ON`)
- **Isolation:** Safe multi-threaded access protected via serialized connections.

---

## 2. Table Schema Inventory

```sql
-- 1. Ingested Documents
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT,
    content_type TEXT,
    file_size_bytes INTEGER,
    source_language TEXT DEFAULT 'en',
    detected_language TEXT,
    language_confidence REAL,
    raw_text TEXT,
    page_count INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

-- 2. Structured Notice Facts
CREATE TABLE IF NOT EXISTS structured_notices (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    issuing_authority TEXT,
    notice_reference_number TEXT,
    notice_date TEXT,
    deadline TEXT,
    fee_or_cost TEXT,
    eligibility TEXT,
    required_documents TEXT,
    required_actions TEXT,
    purpose TEXT,
    summary_en TEXT,
    summary_hi TEXT,
    created_at TEXT NOT NULL
);

-- 3. Action Plan Tasks
CREATE TABLE IF NOT EXISTS action_tasks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    task_order INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT,
    status TEXT DEFAULT 'PENDING',
    is_completed INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- 4. Tracked Deadlines
CREATE TABLE IF NOT EXISTS deadlines (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    deadline_date TEXT NOT NULL,
    deadline_time TEXT,
    timezone TEXT DEFAULT 'IST',
    is_ambiguous INTEGER DEFAULT 0,
    is_expired INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- 5. Proactive Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id TEXT PRIMARY KEY,
    deadline_id TEXT REFERENCES deadlines(id) ON DELETE CASCADE,
    scheduled_time TEXT NOT NULL,
    reminder_type TEXT NOT NULL,
    channel TEXT DEFAULT 'IN_APP',
    status TEXT DEFAULT 'PENDING',
    created_at TEXT NOT NULL
);

-- 6. Corrigendum Revisions
CREATE TABLE IF NOT EXISTS revisions (
    id TEXT PRIMARY KEY,
    source_doc_id TEXT REFERENCES documents(id),
    target_doc_id TEXT REFERENCES documents(id),
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_category TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

## 3. Persistence Across Restarts & Refreshes

Verification scenarios executed in `tests/test_storage_db.py` (6/6 passed):
1. **Document Insertion & Query:** Document record saved and retrieved with full raw text.
2. **Structured Notice Persistence:** Core facts and localized summaries saved and verified.
3. **Action Checklist Toggle:** Toggling a task from `is_completed = 0` to `is_completed = 1` survives simulated backend restart and re-query.
4. **Deadline & Reminder Scheduling:** Deadlines linked with reminders correctly query upcoming events.
5. **Revision Ledger Audit:** Field deltas between base and revised notice persist with foreign key integrity.
6. **Teardown & Concurrency:** Windows file locking prevented via explicit connection closing.
