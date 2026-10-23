"""
Session Store for SuchnaSetu AI.
Provides lightweight, thread-safe, local session isolation for notice analyses and Q&A history.
Stores session state in-memory with optional local JSON persistence.
"""

from __future__ import annotations

import os
import json
import time
import uuid
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from notice2action.config import config


class SessionState(BaseModel):
    """Holds active state for a user's notice analysis session."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    filename: Optional[str] = None
    raw_notice_text: Optional[str] = None
    fingerprint: Optional[str] = None
    reading_level: str = "standard"
    target_language: str = "en"
    structured_notice: Optional[Dict[str, Any]] = None
    summary_en: Optional[Dict[str, Any]] = None
    summary_hi: Optional[Dict[str, Any]] = None
    checklist_en: Optional[Dict[str, Any]] = None
    checklist_hi: Optional[Dict[str, Any]] = None
    user_confirmations: Dict[str, str] = Field(default_factory=dict)
    qa_history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionStore:
    """Thread-safe session storage supporting memory and local disk caching."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or config.session_storage_dir
        self._lock = threading.RLock()
        self._memory_cache: Dict[str, SessionState] = {}

        # Ensure directory exists
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _get_file_path(self, session_id: str) -> Path:
        # Sanitize session_id to prevent traversal
        safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
        return self.storage_dir / f"{safe_id}.json"

    def create_session(self, initial_data: Optional[Dict[str, Any]] = None) -> SessionState:
        """Creates a new isolated session."""
        with self._lock:
            data = initial_data or {}
            session = SessionState(**data)
            self._memory_cache[session.session_id] = session
            self._persist_to_disk(session)
            return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieves a session by ID from memory or disk."""
        if not session_id:
            return None

        with self._lock:
            # 1. Check memory cache
            if session_id in self._memory_cache:
                return self._memory_cache[session_id]

            # 2. Check disk
            file_path = self._get_file_path(session_id)
            if file_path.is_file():
                try:
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    session = SessionState(**data)
                    self._memory_cache[session_id] = session
                    return session
                except Exception:
                    return None

            return None

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[SessionState]:
        """Applies updates to an existing session."""
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                # Create session if it does not exist
                updates["session_id"] = session_id
                session = SessionState(**updates)
            else:
                for k, v in updates.items():
                    if hasattr(session, k):
                        setattr(session, k, v)
                session.updated_at = time.time()

            self._memory_cache[session_id] = session
            self._persist_to_disk(session)
            return session

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session from memory and disk."""
        with self._lock:
            if session_id in self._memory_cache:
                del self._memory_cache[session_id]

            file_path = self._get_file_path(session_id)
            if file_path.is_file():
                try:
                    file_path.unlink()
                    return True
                except Exception:
                    return False
            return True

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Returns brief summaries of active sessions."""
        with self._lock:
            summaries = []
            for s_id, s in self._memory_cache.items():
                summaries.append({
                    "session_id": s_id,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "filename": s.filename,
                    "has_notice": bool(s.raw_notice_text),
                })
            return summaries

    def _persist_to_disk(self, session: SessionState) -> None:
        """Writes session JSON to disk safely."""
        try:
            file_path = self._get_file_path(session.session_id)
            file_path.write_text(session.model_dump_json(indent=2), encoding="utf-8")
        except Exception:
            # Fallback: keep in-memory only if disk write fails
            pass


# Global singleton instance
session_store = SessionStore()
