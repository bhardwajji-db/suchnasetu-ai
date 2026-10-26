"""

Verification tests for database initialization, schema versioning, and migration safety.

All tests execute strictly against isolated temporary databases, preserving production data.

"""



import tempfile

import sqlite3

import pytest

from pathlib import Path



from notice2action.storage.db import DatabaseManager, SCHEMA_VERSION





def test_fresh_database_initialization():

    """A brand new empty database receives the full schema including version 1 and version 2 tables."""

    with tempfile.TemporaryDirectory() as tmpdir:

        db_path = Path(tmpdir) / "fresh.db"

        uploads_dir = Path(tmpdir) / "uploads"

        

        # Initialize

        mgr = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)

        conn = mgr.get_connection()

        

        # Check migrations table

        cur = conn.execute("SELECT version, description FROM schema_migrations ORDER BY version ASC;")

        migrations = cur.fetchall()

        versions = [m["version"] for m in migrations]

        assert versions == [1, 2, 3, 4, 5], f"Expected migrations [1, 2, 3, 4, 5], got {versions}"

        

        # Check v1 tables

        v1_tables = ["documents", "analyses", "checklist_items", "user_confirmations", "qa_interactions", "demo_registry", "app_settings"]

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

        tables = {row["name"] for row in cur.fetchall()}

        for t in v1_tables:

            assert t in tables, f"V1 table '{t}' is missing from fresh database"

            

        # Check v2 tables

        v2_tables = ["users", "sessions", "auth_tokens", "rate_limits"]

        for t in v2_tables:

            assert t in tables, f"V2 table '{t}' is missing from fresh database"

            

        # Check SQLite integrity

        cur = conn.execute("PRAGMA integrity_check;")

        assert cur.fetchone()[0] == "ok"

        

        # Check foreign keys

        cur = conn.execute("PRAGMA foreign_key_check;")

        assert len(cur.fetchall()) == 0

        

        mgr.close()





def test_v1_database_upgrades_to_v2_safely():

    """An existing database at schema Version 1 cleanly upgrades to Version 2 without data loss."""

    with tempfile.TemporaryDirectory() as tmpdir:

        db_path = Path(tmpdir) / "legacy_v1.db"

        uploads_dir = Path(tmpdir) / "uploads"

        

        # Manually create a v1-only database

        raw_conn = sqlite3.connect(str(db_path))

        with raw_conn:

            raw_conn.execute("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, applied_at REAL NOT NULL, description TEXT);")

            raw_conn.execute("INSERT INTO schema_migrations VALUES (1, 1000.0, 'Initial schema');")

            raw_conn.execute("""

                CREATE TABLE documents (

                    id TEXT PRIMARY KEY, filename TEXT NOT NULL, file_path TEXT, file_hash TEXT NOT NULL,

                    file_size_bytes INTEGER NOT NULL, mime_type TEXT NOT NULL, source_language TEXT NOT NULL DEFAULT 'en',

                    detected_language TEXT NOT NULL DEFAULT 'en', language_confidence REAL NOT NULL DEFAULT 1.0,

                    is_mixed_language INTEGER NOT NULL DEFAULT 0, raw_text TEXT NOT NULL, ocr_confidence REAL,

                    ocr_engine TEXT, created_at REAL NOT NULL, updated_at REAL NOT NULL

                );

            """)

            raw_conn.execute("""

                INSERT INTO documents (id, filename, file_hash, file_size_bytes, mime_type, raw_text, created_at, updated_at)

                VALUES ('doc_v1_test', 'test.txt', 'hash123', 10, 'text/plain', 'Original text preserved', 1000.0, 1000.0);

            """)

        raw_conn.close()

        

        # Run DatabaseManager on this legacy DB

        mgr = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)

        conn = mgr.get_connection()

        

        # Verify migrations updated

        cur = conn.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")

        versions = [row["version"] for row in cur.fetchall()]

        assert versions == [1, 2, 3, 4, 5]

        

        # Verify legacy data preserved

        cur = conn.execute("SELECT id, raw_text FROM documents WHERE id = 'doc_v1_test';")

        doc = cur.fetchone()

        assert doc is not None

        assert doc["raw_text"] == "Original text preserved"

        

        # Verify v2 tables exist and work

        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

        tables = {row["name"] for row in cur.fetchall()}

        assert "users" in tables

        assert "sessions" in tables

        assert "auth_tokens" in tables

        assert "rate_limits" in tables

        assert "saved_notices" in tables

        

        # Verify write to new v2 tables

        with conn:

            conn.execute(

                "INSERT INTO users (id, email, name, password_hash, is_verified, created_at, updated_at) VALUES (?, ?, ?, ?, 1, ?, ?)",

                ("usr_1", "citizen@example.com", "Test Citizen", "argon2_hash", "2026-10-25T00:00:00Z", "2026-10-25T00:00:00Z")

            )

        cur = conn.execute("SELECT email, name FROM users WHERE id = 'usr_1';")

        user = cur.fetchone()

        assert user["email"] == "citizen@example.com"

        

        mgr.close()





def test_idempotent_migration_no_duplicates():

    """Re-instantiating DatabaseManager on an already current database is completely idempotent."""

    with tempfile.TemporaryDirectory() as tmpdir:

        db_path = Path(tmpdir) / "current.db"

        uploads_dir = Path(tmpdir) / "uploads"

        

        mgr1 = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)

        mgr1.close()

        

        # Open again

        mgr2 = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)

        conn = mgr2.get_connection()

        

        cur = conn.execute("SELECT version FROM schema_migrations;")

        rows = cur.fetchall()

        assert len(rows) == 5, f"Expected exactly 5 migration records, found {len(rows)}"

        

        # Pragmas

        cur = conn.execute("PRAGMA integrity_check;")

        assert cur.fetchone()[0] == "ok"

        

        mgr2.close()





def test_foreign_key_cascade_behavior():

    """Verify foreign keys are enforced and cascade deletions work as designed in v2 tables."""

    with tempfile.TemporaryDirectory() as tmpdir:

        db_path = Path(tmpdir) / "fk_test.db"

        uploads_dir = Path(tmpdir) / "uploads"

        

        mgr = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)

        conn = mgr.get_connection()

        

        with conn:

            conn.execute(

                "INSERT INTO users (id, email, name, password_hash, is_verified, created_at, updated_at) VALUES ('u1', 'fk@test.com', 'FK User', 'hash', 1, 'now', 'now')"

            )

            conn.execute(

                "INSERT INTO sessions (id, user_id, session_token_hash, expires_at, created_at) VALUES ('s1', 'u1', 'token_hash_1', 'future', 'now')"

            )

            conn.execute(

                "INSERT INTO auth_tokens (id, user_id, token_type, token_hash, expires_at, created_at) VALUES ('t1', 'u1', 'verify', 'thash', 'future', 'now')"

            )

            

        cur = conn.execute("SELECT COUNT(*) FROM sessions WHERE user_id = 'u1';")

        assert cur.fetchone()[0] == 1

        

        # Delete user -> cascades to sessions and auth_tokens

        with conn:

            conn.execute("DELETE FROM users WHERE id = 'u1';")

            

        cur = conn.execute("SELECT COUNT(*) FROM sessions WHERE user_id = 'u1';")

        assert cur.fetchone()[0] == 0

        

        cur = conn.execute("SELECT COUNT(*) FROM auth_tokens WHERE user_id = 'u1';")

        assert cur.fetchone()[0] == 0

        

        mgr.close()

