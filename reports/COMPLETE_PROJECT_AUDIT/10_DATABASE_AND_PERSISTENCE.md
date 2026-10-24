# 10. DATABASE & PERSISTENCE AUDIT — SOCHNASETU AI

**Database Engine:** SQLite 3  
**Database File:** `suchnasetu.db` (Local file persistence)  
**Session Storage:** `.sessions/` directory (Isolated JSON session caches)

---

## 1. SQLite Schema Architecture

The database manages 5 core persistence tables:
1. `documents`: Ingested notices, file hashes, timestamps, character counts, and raw texts.
2. `analyses`: Extracted structured facts, 6 core fields, and plain-language summaries.
3. `qa_history`: Conversational questions, grounded answers, evidence quotes, and support flags.
4. `confirmations`: Human-in-the-loop overrides, original values, confirmed values, and timestamps.
5. `demo_registry`: Catalog of demo library items, metadata, categories, and tags.

---

## 2. Persistence Across Server Restarts

- **Test Case:** Verified via `pytest tests/test_storage_db.py::test_database_persistence_across_restart`.
- **Method:**
  1. Wrote notice analysis record with 6 core fields into `suchnasetu.db`.
  2. Disconnected and purged database session connection objects.
  3. Re-initialized database service and queried document by session ID.
  4. Asserted retrieved fields match written facts exactly.
- **Result:** **PASSED.** All facts, confirmed values, and checklists persist intact across process restarts.
