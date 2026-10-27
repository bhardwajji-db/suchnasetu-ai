"""

SQLite Database and Local File Storage Engine for SuchnaSetu AI.

Provides local-first, zero-cloud, ACID-compliant persistence for:

1. Uploaded/ingested notice documents & original binary files.

2. OCR and text extraction results with confidence & language telemetry.

3. Decoupled Document Source Language and User Target/Output Language.

4. Grounded structured notice facts and six core canonical fields.

5. Action checklist steps and persistence of completion status across restarts.

6. User verification and confirmations for uncertain extracted facts.

7. Follow-up Q&A interactions and source citations.

8. Notice revision diffing and corrigendum comparison records.

9. Persistent Demo Library registry and metadata.

10. Application settings and accessibility preferences.

"""



from __future__ import annotations



import os

import json

import time

import uuid

import hashlib

import sqlite3

import threading

from pathlib import Path

from dataclasses import dataclass, field, asdict

from typing import Dict, Any, List, Optional, Tuple



from notice2action.config import PROJECT_ROOT





DEFAULT_DB_PATH = Path(os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "data" / "suchnasetu.db")))

DEFAULT_UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", str(PROJECT_ROOT / "data" / "uploads")))

SCHEMA_VERSION = 5





@dataclass

class DocumentRecord:

    id: str

    filename: str

    file_path: Optional[str]

    file_hash: str

    file_size_bytes: int

    mime_type: str

    source_language: str

    detected_language: str

    language_confidence: float

    is_mixed_language: bool

    raw_text: str

    ocr_confidence: Optional[float]

    ocr_engine: Optional[str]

    created_at: float

    updated_at: float



    def to_dict(self) -> Dict[str, Any]:

        return asdict(self)





@dataclass

class AnalysisRecord:

    id: str

    document_id: Optional[str]

    session_id: str

    fingerprint: str

    reading_level: str

    source_language: str

    output_language: str

    structured_notice: Dict[str, Any]

    six_core_fields: Dict[str, Any]

    summary: Dict[str, Any]

    action_checklist: Dict[str, Any]

    model_used: str

    inference_duration: Optional[float]

    is_stale: bool

    created_at: float



    def to_dict(self) -> Dict[str, Any]:

        return asdict(self)





@dataclass

class ChecklistItemRecord:

    id: str

    analysis_id: str

    document_id: Optional[str]

    fingerprint: str

    step_number: int

    title: str

    action: str

    deadline: Optional[str]

    mandatory: bool

    completed: bool

    completed_at: Optional[float]



    def to_dict(self) -> Dict[str, Any]:

        return asdict(self)





class DatabaseManager:

    """Thread-safe SQLite database manager for SuchnaSetu AI."""



    def __init__(

        self,

        db_path: Optional[Path] = None,

        uploads_dir: Optional[Path] = None,

    ):

        self.db_path = Path(db_path or DEFAULT_DB_PATH)

        self.uploads_dir = Path(uploads_dir or DEFAULT_UPLOADS_DIR)

        self._lock = threading.RLock()

        self._local = threading.local()



        # Ensure directories exist

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.uploads_dir.mkdir(parents=True, exist_ok=True)



        # Attempt durable restore from R2/S3 if local database is missing
        try:
            from notice2action.storage.storage_sync import storage_sync
            storage_sync.restore_database_if_missing(self.db_path)
        except Exception:
            pass

        # Initialize schema

        self._initialize_schema()



    def close(self) -> None:
        """Closes thread-local database connection if open."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None

    def backup_to_remote_storage(self) -> bool:
        """Triggers an atomic backup to R2/S3 if remote storage is configured."""
        try:
            from notice2action.storage.storage_sync import storage_sync
            return storage_sync.backup_database(self.db_path)
        except Exception:
            return False

    def restore_from_remote_storage(self) -> bool:
        """Triggers a restore from R2/S3 if remote storage is configured."""
        try:
            from notice2action.storage.storage_sync import storage_sync
            return storage_sync.download_file("suchnasetu.db", self.db_path)
        except Exception:
            return False

    def get_connection(self) -> sqlite3.Connection:

        """Returns a thread-local SQLite connection configured with WAL and busy timeout."""

        conn = getattr(self._local, "conn", None)

        if conn is None:

            conn = sqlite3.connect(

                str(self.db_path),

                timeout=30.0,

                check_same_thread=False,

            )

            conn.row_factory = sqlite3.Row

            conn.execute("PRAGMA busy_timeout=30000;")

            conn.execute("PRAGMA synchronous=NORMAL;")

            conn.execute("PRAGMA foreign_keys=ON;")

            self._local.conn = conn

        return conn



    def _initialize_schema(self) -> None:

        """Applies database schema migrations safely and idempotently."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    CREATE TABLE IF NOT EXISTS schema_migrations (

                        version INTEGER PRIMARY KEY,

                        applied_at REAL NOT NULL,

                        description TEXT

                    );

                    """

                )

                cur = conn.execute("SELECT version FROM schema_migrations;")

                applied_versions = {row[0] for row in cur.fetchall()}



                if 1 not in applied_versions:

                    conn.executescript(

                        """

                        CREATE TABLE IF NOT EXISTS documents (

                            id TEXT PRIMARY KEY,

                            filename TEXT NOT NULL,

                            file_path TEXT,

                            file_hash TEXT NOT NULL,

                            file_size_bytes INTEGER NOT NULL,

                            mime_type TEXT NOT NULL,

                            source_language TEXT NOT NULL DEFAULT 'en',

                            detected_language TEXT NOT NULL DEFAULT 'en',

                            language_confidence REAL NOT NULL DEFAULT 1.0,

                            is_mixed_language INTEGER NOT NULL DEFAULT 0,

                            raw_text TEXT NOT NULL,

                            ocr_confidence REAL,

                            ocr_engine TEXT,

                            created_at REAL NOT NULL,

                            updated_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);

                        CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at);



                        CREATE TABLE IF NOT EXISTS analyses (

                            id TEXT PRIMARY KEY,

                            document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,

                            session_id TEXT NOT NULL,

                            fingerprint TEXT NOT NULL,

                            reading_level TEXT NOT NULL DEFAULT 'standard',

                            source_language TEXT NOT NULL DEFAULT 'en',

                            output_language TEXT NOT NULL DEFAULT 'en',

                            structured_notice_json TEXT NOT NULL,

                            six_core_fields_json TEXT NOT NULL,

                            summary_json TEXT NOT NULL,

                            action_checklist_json TEXT NOT NULL,

                            model_used TEXT NOT NULL,

                            inference_duration REAL,

                            is_stale INTEGER NOT NULL DEFAULT 0,

                            created_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_analyses_fingerprint ON analyses(fingerprint);

                        CREATE INDEX IF NOT EXISTS idx_analyses_doc ON analyses(document_id);

                        CREATE INDEX IF NOT EXISTS idx_analyses_session ON analyses(session_id);



                        CREATE TABLE IF NOT EXISTS checklist_items (

                            id TEXT PRIMARY KEY,

                            analysis_id TEXT REFERENCES analyses(id) ON DELETE CASCADE,

                            document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,

                            fingerprint TEXT NOT NULL,

                            step_number INTEGER NOT NULL,

                            title TEXT NOT NULL,

                            action TEXT NOT NULL,

                            deadline TEXT,

                            mandatory INTEGER NOT NULL DEFAULT 1,

                            completed INTEGER NOT NULL DEFAULT 0,

                            completed_at REAL

                        );



                        CREATE INDEX IF NOT EXISTS idx_checklist_fp ON checklist_items(fingerprint);

                        CREATE INDEX IF NOT EXISTS idx_checklist_analysis ON checklist_items(analysis_id);



                        CREATE TABLE IF NOT EXISTS user_confirmations (

                            id TEXT PRIMARY KEY,

                            document_id TEXT,

                            field_name TEXT NOT NULL,

                            original_value TEXT,

                            confirmed_value TEXT NOT NULL,

                            created_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_confirmations_doc ON user_confirmations(document_id);



                        CREATE TABLE IF NOT EXISTS qa_interactions (

                            id TEXT PRIMARY KEY,

                            document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,

                            session_id TEXT NOT NULL,

                            question TEXT NOT NULL,

                            answer TEXT NOT NULL,

                            is_supported INTEGER NOT NULL DEFAULT 1,

                            evidence_quote TEXT,

                            target_lang TEXT NOT NULL DEFAULT 'en',

                            created_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_qa_session ON qa_interactions(session_id);

                        CREATE INDEX IF NOT EXISTS idx_qa_doc ON qa_interactions(document_id);



                        CREATE TABLE IF NOT EXISTS revision_comparisons (

                            id TEXT PRIMARY KEY,

                            base_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,

                            revised_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,

                            comparison_data_json TEXT NOT NULL,

                            created_at REAL NOT NULL

                        );



                        CREATE TABLE IF NOT EXISTS demo_registry (

                            id TEXT PRIMARY KEY,

                            title TEXT NOT NULL,

                            category TEXT NOT NULL,

                            source_file TEXT NOT NULL,

                            format TEXT NOT NULL,

                            source_lang TEXT NOT NULL,

                            target_lang TEXT NOT NULL,

                            is_synthetic INTEGER NOT NULL DEFAULT 1,

                            manifest_data_json TEXT NOT NULL,

                            created_at REAL NOT NULL

                        );



                        CREATE TABLE IF NOT EXISTS app_settings (

                            key TEXT PRIMARY KEY,

                            value_json TEXT NOT NULL,

                            updated_at REAL NOT NULL

                        );



                        INSERT INTO schema_migrations (version, applied_at, description)

                        VALUES (1, strftime('%s', 'now'), 'Initial SuchnaSetu AI production schema');

                        """

                    )



                if 2 not in applied_versions:

                    conn.executescript(

                        """

                        CREATE TABLE IF NOT EXISTS users (

                            id TEXT PRIMARY KEY,

                            email TEXT UNIQUE NOT NULL,

                            name TEXT NOT NULL,

                            password_hash TEXT NOT NULL,

                            is_verified INTEGER NOT NULL DEFAULT 0,

                            created_at TEXT NOT NULL,

                            updated_at TEXT NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);



                        CREATE TABLE IF NOT EXISTS sessions (

                            id TEXT PRIMARY KEY,

                            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

                            session_token_hash TEXT UNIQUE NOT NULL,

                            user_agent TEXT,

                            ip_address TEXT,

                            expires_at TEXT NOT NULL,

                            created_at TEXT NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token_hash);

                        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);



                        CREATE TABLE IF NOT EXISTS auth_tokens (

                            id TEXT PRIMARY KEY,

                            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

                            token_type TEXT NOT NULL,

                            token_hash TEXT NOT NULL,

                            attempts INTEGER NOT NULL DEFAULT 0,

                            max_attempts INTEGER NOT NULL DEFAULT 5,

                            expires_at TEXT NOT NULL,

                            used_at TEXT,

                            created_at TEXT NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_auth_tokens_lookup ON auth_tokens(token_type, token_hash);

                        CREATE INDEX IF NOT EXISTS idx_auth_tokens_user ON auth_tokens(user_id, token_type);



                        CREATE TABLE IF NOT EXISTS rate_limits (

                            key TEXT PRIMARY KEY,

                            count INTEGER NOT NULL DEFAULT 1,

                            window_start REAL NOT NULL

                        );



                        INSERT INTO schema_migrations (version, applied_at, description)

                        VALUES (2, strftime('%s', 'now'), 'Add authentication, sessions, tokens, and rate limits');

                        """

                    )



                if 3 not in applied_versions:

                    conn.executescript(

                        """

                        CREATE TABLE IF NOT EXISTS saved_notices (

                            id TEXT PRIMARY KEY,

                            user_id TEXT NOT NULL,

                            document_id TEXT NOT NULL,

                            title TEXT NOT NULL,

                            authority TEXT,

                            deadline TEXT,

                            raw_text TEXT,

                            assignment_title TEXT,

                            submission_date TEXT,

                            is_ambiguous_date INTEGER NOT NULL DEFAULT 0,

                            created_at REAL NOT NULL,

                            UNIQUE(user_id, document_id)

                        );



                        CREATE INDEX IF NOT EXISTS idx_saved_notices_user ON saved_notices(user_id);

                        CREATE INDEX IF NOT EXISTS idx_saved_notices_doc ON saved_notices(document_id);



                        INSERT INTO schema_migrations (version, applied_at, description)

                        VALUES (3, strftime('%s', 'now'), 'Add user-isolated saved notices and weekly action planner');

                        """

                    )



                if 4 not in applied_versions:

                    conn.executescript(

                        """

                        CREATE TABLE IF NOT EXISTS user_notifications (

                            id TEXT PRIMARY KEY,

                            user_id TEXT NOT NULL,

                            title TEXT NOT NULL,

                            message TEXT NOT NULL,

                            type TEXT NOT NULL DEFAULT 'info',

                            document_id TEXT,

                            is_read INTEGER NOT NULL DEFAULT 0,

                            is_dismissed INTEGER NOT NULL DEFAULT 0,

                            created_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_notifications_user ON user_notifications(user_id, is_dismissed);



                        CREATE TABLE IF NOT EXISTS user_activities (

                            id TEXT PRIMARY KEY,

                            user_id TEXT NOT NULL,

                            activity_type TEXT NOT NULL,

                            title TEXT NOT NULL,

                            description TEXT NOT NULL,

                            document_id TEXT,

                            created_at REAL NOT NULL

                        );



                        CREATE INDEX IF NOT EXISTS idx_activities_user ON user_activities(user_id, created_at);



                        INSERT INTO schema_migrations (version, applied_at, description)

                        VALUES (4, strftime('%s', 'now'), 'Add user notifications and activity timeline');

                        """

                    )


                if 5 not in applied_versions:
                    conn.executescript(
                        """
                        CREATE TABLE IF NOT EXISTS user_preferences (
                            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                            preferences_json TEXT NOT NULL,
                            updated_at REAL NOT NULL
                        );

                        CREATE TABLE IF NOT EXISTS user_checklist_progress (
                            user_id TEXT NOT NULL,
                            item_id TEXT NOT NULL,
                            completed INTEGER NOT NULL DEFAULT 1,
                            completed_at REAL NOT NULL,
                            PRIMARY KEY(user_id, item_id)
                        );

                        CREATE INDEX IF NOT EXISTS idx_user_checklist_user ON user_checklist_progress(user_id);

                        INSERT INTO schema_migrations (version, applied_at, description)
                        VALUES (5, strftime('%s', 'now'), 'Add user preferences and persistent checklist progress');
                        """
                    )

            # Seed demo library notices if available

            self.seed_demo_library()

            # Ensure single default citizen exists in background
            self._ensure_default_citizen()



    # -------------------------------------------------------------------------

    # File Storage Helpers

    # -------------------------------------------------------------------------



    def store_file(self, content_bytes: bytes, original_filename: str) -> Tuple[Path, str]:

        """

        Stores binary document bytes safely in managed directory named by SHA-256.

        Prevents path traversal and filename collisions.

        """

        file_hash = hashlib.sha256(content_bytes).hexdigest()

        ext = Path(original_filename).suffix.lower()

        if not ext or len(ext) > 10:

            ext = ".bin"

        safe_filename = f"{file_hash[:16]}_{int(time.time())}{ext}"

        target_path = self.uploads_dir / safe_filename

        target_path.write_bytes(content_bytes)

        return target_path, file_hash



    # -------------------------------------------------------------------------

    # Document Operations

    # -------------------------------------------------------------------------



    def save_document(

        self,

        raw_text: str,

        filename: str = "notice.txt",

        content_bytes: Optional[bytes] = None,

        mime_type: str = "text/plain",

        source_language: str = "en",

        detected_language: str = "en",

        language_confidence: float = 1.0,

        is_mixed_language: bool = False,

        ocr_confidence: Optional[float] = None,

        ocr_engine: Optional[str] = None,

        doc_id: Optional[str] = None,

    ) -> DocumentRecord:

        """Saves a document and its raw extracted text persistently."""

        with self._lock:

            doc_id = doc_id or str(uuid.uuid4())

            stored_path_str = None

            if content_bytes is not None:

                path, f_hash = self.store_file(content_bytes, filename)

                try:

                    stored_path_str = str(path.relative_to(PROJECT_ROOT))

                except Exception:

                    stored_path_str = str(path)

                file_size = len(content_bytes)

            else:

                f_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

                file_size = len(raw_text.encode("utf-8"))



            now = time.time()

            record = DocumentRecord(

                id=doc_id,

                filename=filename,

                file_path=stored_path_str,

                file_hash=f_hash,

                file_size_bytes=file_size,

                mime_type=mime_type,

                source_language=source_language,

                detected_language=detected_language,

                language_confidence=language_confidence,

                is_mixed_language=is_mixed_language,

                raw_text=raw_text,

                ocr_confidence=ocr_confidence,

                ocr_engine=ocr_engine,

                created_at=now,

                updated_at=now,

            )



            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO documents (

                        id, filename, file_path, file_hash, file_size_bytes,

                        mime_type, source_language, detected_language, language_confidence,

                        is_mixed_language, raw_text, ocr_confidence, ocr_engine,

                        created_at, updated_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(id) DO UPDATE SET

                        filename=excluded.filename,

                        raw_text=excluded.raw_text,

                        source_language=excluded.source_language,

                        detected_language=excluded.detected_language,

                        language_confidence=excluded.language_confidence,

                        is_mixed_language=excluded.is_mixed_language,

                        ocr_confidence=excluded.ocr_confidence,

                        updated_at=excluded.updated_at;

                    """,

                    (

                        record.id,

                        record.filename,

                        record.file_path,

                        record.file_hash,

                        record.file_size_bytes,

                        record.mime_type,

                        record.source_language,

                        record.detected_language,

                        record.language_confidence,

                        1 if record.is_mixed_language else 0,

                        record.raw_text,

                        record.ocr_confidence,

                        record.ocr_engine,

                        record.created_at,

                        record.updated_at,

                    ),

                )

            return record



    def get_document(self, doc_id: str) -> Optional[DocumentRecord]:

        """Retrieves a document by ID."""

        conn = self.get_connection()

        cur = conn.execute("SELECT * FROM documents WHERE id = ?;", (doc_id,))

        row = cur.fetchone()

        if not row:

            return None

        return DocumentRecord(

            id=row["id"],

            filename=row["filename"],

            file_path=row["file_path"],

            file_hash=row["file_hash"],

            file_size_bytes=row["file_size_bytes"],

            mime_type=row["mime_type"],

            source_language=row["source_language"],

            detected_language=row["detected_language"],

            language_confidence=row["language_confidence"],

            is_mixed_language=bool(row["is_mixed_language"]),

            raw_text=row["raw_text"],

            ocr_confidence=row["ocr_confidence"],

            ocr_engine=row["ocr_engine"],

            created_at=row["created_at"],

            updated_at=row["updated_at"],

        )



    def list_documents(self, limit: int = 50, offset: int = 0) -> List[DocumentRecord]:

        """Lists saved documents ordered by most recent."""

        conn = self.get_connection()

        cur = conn.execute(

            "SELECT * FROM documents ORDER BY created_at DESC LIMIT ? OFFSET ?;",

            (limit, offset),

        )

        records = []

        for row in cur.fetchall():

            records.append(

                DocumentRecord(

                    id=row["id"],

                    filename=row["filename"],

                    file_path=row["file_path"],

                    file_hash=row["file_hash"],

                    file_size_bytes=row["file_size_bytes"],

                    mime_type=row["mime_type"],

                    source_language=row["source_language"],

                    detected_language=row["detected_language"],

                    language_confidence=row["language_confidence"],

                    is_mixed_language=bool(row["is_mixed_language"]),

                    raw_text=row["raw_text"],

                    ocr_confidence=row["ocr_confidence"],

                    ocr_engine=row["ocr_engine"],

                    created_at=row["created_at"],

                    updated_at=row["updated_at"],

                )

            )

        return records



    # -------------------------------------------------------------------------

    # Analysis & Grounded Facts Operations

    # -------------------------------------------------------------------------



    def save_analysis(

        self,

        session_id: str,

        fingerprint: str,

        structured_notice: Dict[str, Any],

        six_core_fields: Dict[str, Any],

        summary: Dict[str, Any],

        action_checklist: Dict[str, Any],

        document_id: Optional[str] = None,

        reading_level: str = "standard",

        source_language: str = "en",

        output_language: str = "en",

        model_used: str = "gemma4:latest",

        inference_duration: Optional[float] = None,

        analysis_id: Optional[str] = None,

    ) -> AnalysisRecord:

        """Saves a complete grounded analysis, extracted fields, and checklist steps."""

        with self._lock:

            analysis_id = analysis_id or str(uuid.uuid4())

            now = time.time()



            record = AnalysisRecord(

                id=analysis_id,

                document_id=document_id,

                session_id=session_id,

                fingerprint=fingerprint,

                reading_level=reading_level,

                source_language=source_language,

                output_language=output_language,

                structured_notice=structured_notice,

                six_core_fields=six_core_fields,

                summary=summary,

                action_checklist=action_checklist,

                model_used=model_used,

                inference_duration=inference_duration,

                is_stale=False,

                created_at=now,

            )



            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO analyses (

                        id, document_id, session_id, fingerprint, reading_level,

                        source_language, output_language, structured_notice_json,

                        six_core_fields_json, summary_json, action_checklist_json,

                        model_used, inference_duration, is_stale, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);

                    """,

                    (

                        record.id,

                        record.document_id,

                        record.session_id,

                        record.fingerprint,

                        record.reading_level,

                        record.source_language,

                        record.output_language,

                        json.dumps(record.structured_notice, ensure_ascii=False),

                        json.dumps(record.six_core_fields, ensure_ascii=False),

                        json.dumps(record.summary, ensure_ascii=False),

                        json.dumps(record.action_checklist, ensure_ascii=False),

                        record.model_used,

                        record.inference_duration,

                        0,

                        record.created_at,

                    ),

                )



                # Persist individual checklist items into checklist_items table

                items = action_checklist.get("items", [])

                for idx, item in enumerate(items, 1):

                    item_id = item.get("id") or f"{analysis_id}_step_{idx}"

                    title = item.get("title") or f"Step {idx}"

                    action = item.get("action") or ""

                    deadline = item.get("deadline")

                    mandatory = 1 if item.get("is_mandatory", True) else 0



                    conn.execute(

                        """

                        INSERT INTO checklist_items (

                            id, analysis_id, document_id, fingerprint, step_number,

                            title, action, deadline, mandatory, completed, completed_at

                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                        ON CONFLICT(id) DO UPDATE SET

                            title=excluded.title,

                            action=excluded.action,

                            deadline=excluded.deadline;

                        """,

                        (

                            item_id,

                            record.id,

                            record.document_id,

                            record.fingerprint,

                            idx,

                            title,

                            action,

                            deadline,

                            mandatory,

                            0,

                            None,

                        ),

                    )



            return record



    def get_analysis_by_fingerprint(self, fingerprint: str) -> Optional[AnalysisRecord]:

        """Retrieves the latest analysis matching the notice text fingerprint."""

        conn = self.get_connection()

        cur = conn.execute(

            """

            SELECT * FROM analyses

            WHERE fingerprint = ?

            ORDER BY created_at DESC LIMIT 1;

            """,

            (fingerprint,),

        )

        row = cur.fetchone()

        if not row:

            return None

        return self._row_to_analysis_record(row)



    def get_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:

        """Retrieves an analysis by ID."""

        conn = self.get_connection()

        cur = conn.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,))

        row = cur.fetchone()

        if not row:

            return None

        return self._row_to_analysis_record(row)



    def _row_to_analysis_record(self, row: sqlite3.Row) -> AnalysisRecord:

        return AnalysisRecord(

            id=row["id"],

            document_id=row["document_id"],

            session_id=row["session_id"],

            fingerprint=row["fingerprint"],

            reading_level=row["reading_level"],

            source_language=row["source_language"],

            output_language=row["output_language"],

            structured_notice=json.loads(row["structured_notice_json"]),

            six_core_fields=json.loads(row["six_core_fields_json"]),

            summary=json.loads(row["summary_json"]),

            action_checklist=json.loads(row["action_checklist_json"]),

            model_used=row["model_used"],

            inference_duration=row["inference_duration"],

            is_stale=bool(row["is_stale"]),

            created_at=row["created_at"],

        )



    # -------------------------------------------------------------------------

    # Checklist Item State Persistence

    # -------------------------------------------------------------------------



    def set_checklist_item_completed(self, item_id: str, completed: bool) -> bool:

        """Updates the completion state of a checklist item persistently."""

        with self._lock:

            conn = self.get_connection()

            now = time.time() if completed else None

            with conn:

                cur = conn.execute(

                    """

                    UPDATE checklist_items

                    SET completed = ?, completed_at = ?

                    WHERE id = ?;

                    """,

                    (1 if completed else 0, now, item_id),

                )

                return cur.rowcount > 0



    def get_checklist_items_for_fingerprint(self, fingerprint: str) -> List[ChecklistItemRecord]:

        """Gets all persisted checklist items for a given notice fingerprint."""

        conn = self.get_connection()

        cur = conn.execute(

            """

            SELECT * FROM checklist_items

            WHERE fingerprint = ?

            ORDER BY step_number ASC;

            """,

            (fingerprint,),

        )

        items = []

        for row in cur.fetchall():

            items.append(

                ChecklistItemRecord(

                    id=row["id"],

                    analysis_id=row["analysis_id"],

                    document_id=row["document_id"],

                    fingerprint=row["fingerprint"],

                    step_number=row["step_number"],

                    title=row["title"],

                    action=row["action"],

                    deadline=row["deadline"],

                    mandatory=bool(row["mandatory"]),

                    completed=bool(row["completed"]),

                    completed_at=row["completed_at"],

                )

            )

        return items



    # -------------------------------------------------------------------------

    # User Confirmations & Follow-up Q&A

    # -------------------------------------------------------------------------



    def save_user_confirmation(

        self,

        field_name: str,

        confirmed_value: str,

        original_value: Optional[str] = None,

        document_id: Optional[str] = None,

    ) -> str:

        """Stores user corrections/confirmations for ambiguous fields."""

        with self._lock:

            conf_id = str(uuid.uuid4())

            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO user_confirmations (

                        id, document_id, field_name, original_value, confirmed_value, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?);

                    """,

                    (conf_id, document_id, field_name, original_value, confirmed_value, time.time()),

                )

            return conf_id



    def save_qa_interaction(

        self,

        session_id: str,

        question: str,

        answer: str,

        is_supported: bool,

        evidence_quote: Optional[str] = None,

        target_lang: str = "en",

        document_id: Optional[str] = None,

    ) -> str:

        """Persists a grounded Q&A interaction."""

        with self._lock:

            qa_id = str(uuid.uuid4())

            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO qa_interactions (

                        id, document_id, session_id, question, answer,

                        is_supported, evidence_quote, target_lang, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);

                    """,

                    (

                        qa_id,

                        document_id,

                        session_id,

                        question,

                        answer,

                        1 if is_supported else 0,

                        evidence_quote,

                        target_lang,

                        time.time(),

                    ),

                )

            return qa_id



    def get_qa_history(self, session_id: str) -> List[Dict[str, Any]]:

        """Retrieves Q&A history for a session."""

        conn = self.get_connection()

        cur = conn.execute(

            """

            SELECT * FROM qa_interactions

            WHERE session_id = ?

            ORDER BY created_at ASC;

            """,

            (session_id,),

        )

        res = []

        for r in cur.fetchall():

            res.append({

                "id": r["id"],

                "question": r["question"],

                "answer": r["answer"],

                "is_supported": bool(r["is_supported"]),

                "evidence_quote": r["evidence_quote"],

                "target_lang": r["target_lang"],

                "created_at": r["created_at"],

            })

        return res



    # -------------------------------------------------------------------------

    # Demo Library Registry

    # -------------------------------------------------------------------------



    def register_demo(

        self,

        demo_id: str,

        title: str,

        category: str,

        source_file: str,

        format_type: str,

        source_lang: str,

        target_lang: str,

        manifest_data: Dict[str, Any],

        is_synthetic: bool = True,

    ) -> None:

        """Registers a sample demo notice in the persistent registry."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO demo_registry (

                        id, title, category, source_file, format,

                        source_lang, target_lang, is_synthetic, manifest_data_json, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(id) DO UPDATE SET

                        title=excluded.title,

                        category=excluded.category,

                        source_file=excluded.source_file,

                        format=excluded.format,

                        source_lang=excluded.source_lang,

                        target_lang=excluded.target_lang,

                        manifest_data_json=excluded.manifest_data_json;

                    """,

                    (

                        demo_id,

                        title,

                        category,

                        source_file,

                        format_type,

                        source_lang,

                        target_lang,

                        1 if is_synthetic else 0,

                        json.dumps(manifest_data, ensure_ascii=False),

                        time.time(),

                    ),

                )



    def list_demos(

        self,

        category: Optional[str] = None,

        source_lang: Optional[str] = None,

        format_type: Optional[str] = None,

        search_query: Optional[str] = None,

    ) -> List[Dict[str, Any]]:

        """Searches and filters registered demo library notices."""

        conn = self.get_connection()

        query = "SELECT * FROM demo_registry WHERE 1=1"

        params: List[Any] = []



        if category:

            query += " AND category = ?"

            params.append(category)

        if source_lang:

            query += " AND source_lang = ?"

            params.append(source_lang)

        if format_type:

            query += " AND format = ?"

            params.append(format_type)

        if search_query:

            query += " AND (title LIKE ? OR manifest_data_json LIKE ?)"

            term = f"%{search_query}%"

            params.extend([term, term])



        query += " ORDER BY id ASC;"

        cur = conn.execute(query, params)

        demos = []

        for r in cur.fetchall():

            demos.append({

                "id": r["id"],

                "title": r["title"],

                "category": r["category"],

                "source_file": r["source_file"],

                "format": r["format"],

                "source_lang": r["source_lang"],

                "target_lang": r["target_lang"],

                "is_synthetic": bool(r["is_synthetic"]),

                "manifest_data": json.loads(r["manifest_data_json"]),

                "created_at": r["created_at"],

            })

        return demos



    def seed_demo_library(self, manifest_path: Optional[Path] = None) -> int:

        """Reads demo library manifest.json and registers all notices into SQLite."""

        target_manifest = manifest_path or (PROJECT_ROOT / "tests" / "fixtures" / "demo_library" / "manifest.json")

        if not target_manifest.is_file():

            return 0

        try:

            items = json.loads(target_manifest.read_text(encoding="utf-8"))

            count = 0

            for item in items:

                self.register_demo(

                    demo_id=item["id"],

                    title=item["title"],

                    category=item["category"],

                    source_file=item["file_path"],

                    format_type=item["format"],

                    source_lang=item["source_language"],

                    target_lang=item["suggested_output_language"],

                    manifest_data=item,

                    is_synthetic=item.get("is_synthetic", True),

                )

                count += 1

            return count

        except Exception:

            return 0



    # -------------------------------------------------------------------------

    def _ensure_default_citizen(self) -> None:
        """
        Ensures the single default citizen user (diwakarbhardwaj477@gmail.com)
        is permanently established in SQLite with verified status and Argon2id hash.
        This guarantees the user can always log in without setup friction.
        """
        email = "diwakarbhardwaj477@gmail.com"
        name = "Diwakar Bhardwaj"
        raw_password = "Diwakar@123"
        citizen_id = "e60d74f2-f629-4753-9272-6fa3e65cb61a"

        try:
            from notice2action.auth.security import hash_password, verify_password
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password_hash, is_verified FROM users WHERE lower(email) = lower(?)",
                (email,)
            )
            existing = cursor.fetchone()
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            now_epoch = time.time()

            with conn:
                if not existing:
                    pwd_hash = hash_password(raw_password)
                    conn.execute(
                        """
                        INSERT INTO users (id, email, name, password_hash, is_verified, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 1, ?, ?)
                        """,
                        (citizen_id, email, name, pwd_hash, now_iso, now_iso),
                    )
                    prefs_json = '{"theme": "dark", "language": "en", "reading_level": "standard", "high_contrast": false}'
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO user_preferences (user_id, preferences_json, updated_at)
                        VALUES (?, ?, ?)
                        """,
                        (citizen_id, prefs_json, now_epoch),
                    )
                else:
                    user_id = existing["id"] if isinstance(existing, sqlite3.Row) else existing[0]
                    pwd_hash = existing["password_hash"] if isinstance(existing, sqlite3.Row) else existing[1]
                    is_verified = existing["is_verified"] if isinstance(existing, sqlite3.Row) else existing[2]

                    if not is_verified or not verify_password(raw_password, pwd_hash):
                        new_pwd_hash = hash_password(raw_password)
                        conn.execute(
                            """
                            UPDATE users SET password_hash = ?, is_verified = 1, updated_at = ? WHERE id = ?
                            """,
                            (new_pwd_hash, now_iso, user_id),
                        )
        except Exception:
            pass

        # App Settings & Preferences

    # -------------------------------------------------------------------------



    def set_setting(self, key: str, value: Any) -> None:

        """Sets an application setting."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                conn.execute(

                    """

                    INSERT INTO app_settings (key, value_json, updated_at)

                    VALUES (?, ?, ?)

                    ON CONFLICT(key) DO UPDATE SET

                        value_json=excluded.value_json,

                        updated_at=excluded.updated_at;

                    """,

                    (key, json.dumps(value, ensure_ascii=False), time.time()),

                )



    def get_setting(self, key: str, default: Any = None) -> Any:

        """Gets an application setting."""

        conn = self.get_connection()

        cur = conn.execute("SELECT value_json FROM app_settings WHERE key = ?;", (key,))

        row = cur.fetchone()

        if not row:

            return default

        try:

            return json.loads(row["value_json"])

        except Exception:

            return default



    # -------------------------------------------------------------------------

    # Saved Notices & Weekly Action Planner Operations

    # -------------------------------------------------------------------------



    def save_notice_for_user(

        self,

        user_id: str,

        document_id: str,

        title: str,

        authority: Optional[str] = None,

        deadline: Optional[str] = None,

        raw_text: Optional[str] = None,

        assignment_title: Optional[str] = None,

        submission_date: Optional[str] = None,

        is_ambiguous_date: bool = False,

    ) -> Dict[str, Any]:

        """Saves a notice for a specific user with deduplication and metadata extraction."""

        with self._lock:

            conn = self.get_connection()

            rec_id = f"sn_{uuid.uuid4().hex[:12]}"

            now = time.time()

            with conn:

                conn.execute(

                    """

                    INSERT INTO saved_notices (

                        id, user_id, document_id, title, authority, deadline,

                        raw_text, assignment_title, submission_date, is_ambiguous_date, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(user_id, document_id) DO UPDATE SET

                        title=excluded.title,

                        authority=excluded.authority,

                        deadline=excluded.deadline,

                        raw_text=excluded.raw_text,

                        assignment_title=excluded.assignment_title,

                        submission_date=excluded.submission_date,

                        is_ambiguous_date=excluded.is_ambiguous_date;

                    """,

                    (

                        rec_id,

                        user_id,

                        document_id,

                        title,

                        authority or "",

                        deadline or "",

                        raw_text or "",

                        assignment_title or "",

                        submission_date or "",

                        1 if is_ambiguous_date else 0,

                        now,

                    ),

                )

            return {

                "id": rec_id,

                "user_id": user_id,

                "document_id": document_id,

                "title": title,

                "authority": authority or "",

                "deadline": deadline or "",

                "assignment_title": assignment_title or "",

                "submission_date": submission_date or "",

                "is_ambiguous_date": is_ambiguous_date,

                "created_at": now,

            }



    def unsave_notice_for_user(self, user_id: str, document_id: str) -> bool:

        """Removes a saved notice strictly for the specified user."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                cur = conn.execute(

                    "DELETE FROM saved_notices WHERE user_id = ? AND document_id = ?;",

                    (user_id, document_id),

                )

                return cur.rowcount > 0



    def list_saved_notices_for_user(

        self, user_id: str, search_query: Optional[str] = None

    ) -> List[Dict[str, Any]]:

        """Retrieves all saved notices belonging strictly to the specified user."""

        with self._lock:

            conn = self.get_connection()

            if search_query and search_query.strip():

                pattern = f"%{search_query.strip().lower()}%"

                cur = conn.execute(

                    """

                    SELECT id, user_id, document_id, title, authority, deadline,

                           assignment_title, submission_date, is_ambiguous_date, created_at

                    FROM saved_notices

                    WHERE user_id = ? AND (

                        lower(title) LIKE ? OR

                        lower(authority) LIKE ? OR

                        lower(deadline) LIKE ? OR

                        lower(assignment_title) LIKE ? OR

                        lower(raw_text) LIKE ?

                    )

                    ORDER BY created_at DESC;

                    """,

                    (user_id, pattern, pattern, pattern, pattern, pattern),

                )

            else:

                cur = conn.execute(

                    """

                    SELECT id, user_id, document_id, title, authority, deadline,

                           assignment_title, submission_date, is_ambiguous_date, created_at

                    FROM saved_notices

                    WHERE user_id = ?

                    ORDER BY created_at DESC;

                    """,

                    (user_id,),

                )

            rows = cur.fetchall()

            return [

                {

                    "id": row["id"],

                    "user_id": row["user_id"],

                    "document_id": row["document_id"],

                    "title": row["title"],

                    "authority": row["authority"],

                    "deadline": row["deadline"],

                    "assignment_title": row["assignment_title"],

                    "submission_date": row["submission_date"],

                    "is_ambiguous_date": bool(row["is_ambiguous_date"]),

                    "created_at": row["created_at"],

                }

                for row in rows

            ]



    def is_notice_saved_for_user(self, user_id: str, document_id: str) -> bool:

        """Checks if a document is saved for a specific user."""

        with self._lock:

            conn = self.get_connection()

            cur = conn.execute(

                "SELECT 1 FROM saved_notices WHERE user_id = ? AND document_id = ? LIMIT 1;",

                (user_id, document_id),

            )

            return cur.fetchone() is not None



    # -------------------------------------------------------------------------

    # Data Purge & Reset

    # -------------------------------------------------------------------------



    # -------------------------------------------------------------------------

    # Notification Operations

    # -------------------------------------------------------------------------



    def create_notification(

        self,

        user_id: str,

        title: str,

        message: str,

        type: str = "info",

        document_id: Optional[str] = None,

    ) -> Dict[str, Any]:

        """Creates a persistent user notification."""

        with self._lock:

            conn = self.get_connection()

            notif_id = f"notif_{uuid.uuid4().hex[:12]}"

            now = time.time()

            with conn:

                conn.execute(

                    """

                    INSERT INTO user_notifications (

                        id, user_id, title, message, type, document_id, is_read, is_dismissed, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?);

                    """,

                    (notif_id, user_id, title, message, type, document_id, now),

                )

            return {

                "id": notif_id,

                "user_id": user_id,

                "title": title,

                "message": message,

                "type": type,

                "document_id": document_id,

                "is_read": False,

                "is_dismissed": False,

                "created_at": now,

            }



    def list_notifications_for_user(

        self, user_id: str, include_dismissed: bool = False

    ) -> List[Dict[str, Any]]:

        """Lists notifications for a user, sorted newest first."""

        with self._lock:

            conn = self.get_connection()

            query = """

                SELECT id, user_id, title, message, type, document_id, is_read, is_dismissed, created_at

                FROM user_notifications

                WHERE user_id = ?

            """

            params: List[Any] = [user_id]

            if not include_dismissed:

                query += " AND is_dismissed = 0"

            query += " ORDER BY created_at DESC LIMIT 50;"

            cur = conn.execute(query, params)

            return [

                {

                    "id": row["id"],

                    "user_id": row["user_id"],

                    "title": row["title"],

                    "message": row["message"],

                    "type": row["type"],

                    "document_id": row["document_id"],

                    "is_read": bool(row["is_read"]),

                    "is_dismissed": bool(row["is_dismissed"]),

                    "created_at": row["created_at"],

                }

                for row in cur.fetchall()

            ]



    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:

        """Marks a notification as read."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                cur = conn.execute(

                    "UPDATE user_notifications SET is_read = 1 WHERE id = ? AND user_id = ?;",

                    (notification_id, user_id),

                )

                return cur.rowcount > 0



    def mark_all_notifications_read(self, user_id: str) -> int:

        """Marks all active notifications as read for a user."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                cur = conn.execute(

                    "UPDATE user_notifications SET is_read = 1 WHERE user_id = ? AND is_dismissed = 0;",

                    (user_id,),

                )

                return cur.rowcount



    def dismiss_notification(self, user_id: str, notification_id: str) -> bool:

        """Dismisses a notification (soft delete)."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                cur = conn.execute(

                    "UPDATE user_notifications SET is_dismissed = 1 WHERE id = ? AND user_id = ?;",

                    (notification_id, user_id),

                )

                return cur.rowcount > 0



    # -------------------------------------------------------------------------

    # Activity Timeline Operations

    # -------------------------------------------------------------------------



    def record_activity(

        self,

        user_id: str,

        activity_type: str,

        title: str,

        description: str,

        document_id: Optional[str] = None,

    ) -> Dict[str, Any]:

        """Records an audit event in the user activity timeline."""

        with self._lock:

            conn = self.get_connection()

            act_id = f"act_{uuid.uuid4().hex[:12]}"

            now = time.time()

            with conn:

                conn.execute(

                    """

                    INSERT INTO user_activities (

                        id, user_id, activity_type, title, description, document_id, created_at

                    ) VALUES (?, ?, ?, ?, ?, ?, ?);

                    """,

                    (act_id, user_id, activity_type, title, description, document_id, now),

                )

            return {

                "id": act_id,

                "user_id": user_id,

                "activity_type": activity_type,

                "title": title,

                "description": description,

                "document_id": document_id,

                "created_at": now,

            }



    def list_activities_for_user(

        self, user_id: str, limit: int = 20

    ) -> List[Dict[str, Any]]:

        """Lists chronological activities for a user, newest first."""

        with self._lock:

            conn = self.get_connection()

            cur = conn.execute(

                """

                SELECT id, user_id, activity_type, title, description, document_id, created_at

                FROM user_activities

                WHERE user_id = ?

                ORDER BY created_at DESC

                LIMIT ?;

                """,

                (user_id, limit),

            )

            return [

                {

                    "id": row["id"],

                    "user_id": row["user_id"],

                    "activity_type": row["activity_type"],

                    "title": row["title"],

                    "description": row["description"],

                    "document_id": row["document_id"],

                    "created_at": row["created_at"],

                }

                for row in cur.fetchall()

            ]



    def close(self) -> None:

        """Closes the current thread-local connection if open."""

        conn = getattr(self._local, "conn", None)

        if conn is not None:

            try:

                conn.close()

            except Exception:

                pass

            self._local.conn = None



    def purge_all_data(self) -> None:

        """Purges all user documents, analyses, checklists, Q&A, keeping migrations and demo registry."""

        with self._lock:

            conn = self.get_connection()

            with conn:

                conn.execute("DELETE FROM checklist_items;")

                conn.execute("DELETE FROM user_confirmations;")

                conn.execute("DELETE FROM qa_interactions;")

                conn.execute("DELETE FROM revision_comparisons;")

                conn.execute("DELETE FROM analyses;")

                conn.execute("DELETE FROM documents;")

                conn.execute("VACUUM;")



    # -------------------------------------------------------------------------
    # User Preferences & Checklist Progress (Migration 5)
    # -------------------------------------------------------------------------

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Returns persisted user preferences (language, accessibility, theme) or empty dict."""
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("SELECT preferences_json FROM user_preferences WHERE user_id = ?;", (user_id,))
            row = cur.fetchone()
            if row and row["preferences_json"]:
                try:
                    return json.loads(row["preferences_json"])
                except Exception:
                    return {}
            return {}

    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Upserts user preferences for an authenticated citizen."""
        with self._lock:
            conn = self.get_connection()
            now = time.time()
            pref_json = json.dumps(preferences)
            with conn:
                conn.execute(
                    """
                    INSERT INTO user_preferences (user_id, preferences_json, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        preferences_json = excluded.preferences_json,
                        updated_at = excluded.updated_at;
                    """,
                    (user_id, pref_json, now),
                )
            return True

    def get_user_checklist_progress(self, user_id: str) -> Dict[str, bool]:
        """Returns a map of {item_id: completed_boolean} for the current user."""
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute(
                "SELECT item_id, completed FROM user_checklist_progress WHERE user_id = ?;",
                (user_id,),
            )
            return {row["item_id"]: bool(row["completed"]) for row in cur.fetchall()}

    def set_user_checklist_progress(self, user_id: str, item_id: str, completed: bool) -> bool:
        """Persists the completion state of a checklist task for a specific user."""
        with self._lock:
            conn = self.get_connection()
            now = time.time()
            with conn:
                conn.execute(
                    """
                    INSERT INTO user_checklist_progress (user_id, item_id, completed, completed_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, item_id) DO UPDATE SET
                        completed = excluded.completed,
                        completed_at = excluded.completed_at;
                    """,
                    (user_id, item_id, 1 if completed else 0, now),
                )
            return True


    def backup_database(self, destination_path: Path) -> None:

        """Creates a hot, online backup of the SQLite database."""

        with self._lock:

            conn = self.get_connection()

            dest_conn = sqlite3.connect(str(destination_path))

            with dest_conn:

                conn.backup(dest_conn)

            dest_conn.close()





# Global Singleton instance

_db_manager_instance: Optional[DatabaseManager] = None

_db_lock = threading.Lock()





def get_db() -> DatabaseManager:

    """Returns the global singleton DatabaseManager instance."""

    global _db_manager_instance

    if _db_manager_instance is None:

        with _db_lock:

            if _db_manager_instance is None:

                _db_manager_instance = DatabaseManager()

    return _db_manager_instance

