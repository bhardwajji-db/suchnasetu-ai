"""
Evidence Service for SuchnaSetu AI.
Stores, segments, searches, and verifies notice-derived evidence.
Provides strictly grounded text snippets and line-numbered citations.
"""

from __future__ import annotations

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class EvidenceSegment(BaseModel):
    """A discrete line or segment of notice text with positional metadata."""
    segment_id: int
    line_number: int
    text: str
    char_start: int
    char_end: int


class EvidenceCitation(BaseModel):
    """A citation referencing specific evidence in the notice."""
    line_number: int
    quote: str
    relevance_score: float = 1.0


class NoticeEvidenceStore(BaseModel):
    """Structured evidence repository derived from a single notice document."""
    fingerprint: str
    total_lines: int
    total_chars: int
    segments: List[EvidenceSegment] = Field(default_factory=list)
    fact_citations: Dict[str, str] = Field(default_factory=dict)


class EvidenceService:
    """Manages ingestion, indexing, and retrieval of ground-truth notice evidence."""

    def __init__(self):
        # In-memory index of loaded documents by fingerprint
        self._stores: Dict[str, NoticeEvidenceStore] = {}

    def index_notice(self, notice_text: str) -> NoticeEvidenceStore:
        """
        Segments raw notice text into line-numbered evidence units
        and indexes them by document fingerprint.
        """
        clean_text = notice_text.strip()
        fp = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()

        if fp in self._stores:
            return self._stores[fp]

        lines = notice_text.splitlines()
        segments: List[EvidenceSegment] = []
        char_cursor = 0

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            char_len = len(line)
            if line_str:  # Only index non-empty lines
                segments.append(
                    EvidenceSegment(
                        segment_id=len(segments) + 1,
                        line_number=idx,
                        text=line_str,
                        char_start=char_cursor,
                        char_end=char_cursor + char_len,
                    )
                )
            char_cursor += char_len + 1  # Account for newline

        store = NoticeEvidenceStore(
            fingerprint=fp,
            total_lines=len(lines),
            total_chars=len(notice_text),
            segments=segments,
        )
        self._stores[fp] = store
        return store

    def get_evidence_store(self, fingerprint: str) -> Optional[NoticeEvidenceStore]:
        """Retrieves stored evidence index by document fingerprint."""
        return self._stores.get(fingerprint)

    def search_evidence(
        self,
        query: str,
        notice_text: str,
        max_results: int = 5,
    ) -> List[EvidenceCitation]:
        """
        Searches notice text for lines relevant to a user query.
        Uses token overlap and keyword matching.
        """
        store = self.index_notice(notice_text)
        query_words = set(re.findall(r"\w+", query.lower()))
        # Remove low-value stop words
        stop_words = {"the", "a", "an", "is", "are", "in", "on", "at", "to", "for", "of", "and", "or", "what", "where", "how", "when", "can", "i"}
        query_terms = query_words - stop_words

        if not query_terms:
            return []

        scored_segments: List[Tuple[float, EvidenceSegment]] = []
        for seg in store.segments:
            seg_words = set(re.findall(r"\w+", seg.text.lower()))
            overlap = len(query_terms.intersection(seg_words))
            if overlap > 0:
                score = overlap / len(query_terms)
                scored_segments.append((score, seg))

        # Sort descending by relevance score
        scored_segments.sort(key=lambda x: x[0], reverse=True)

        citations: List[EvidenceCitation] = []
        for score, seg in scored_segments[:max_results]:
            citations.append(
                EvidenceCitation(
                    line_number=seg.line_number,
                    quote=seg.text,
                    relevance_score=round(score, 2),
                )
            )

        return citations

    def verify_quote(self, quote: str, notice_text: str) -> Tuple[bool, Optional[int]]:
        """
        Verifies whether an alleged quote exists verbatim in the notice text.
        Returns (exists: bool, line_number: Optional[int]).
        """
        if not quote or not quote.strip() or not notice_text:
            return False, None

        q_clean = quote.strip()
        lines = notice_text.splitlines()

        # 1. Exact substring check in full text
        if q_clean in notice_text:
            for idx, line in enumerate(lines, start=1):
                if q_clean in line:
                    return True, idx
            # If multi-line quote
            return True, 1

        # 2. Case-insensitive check
        q_lower = q_clean.lower()
        for idx, line in enumerate(lines, start=1):
            if q_lower in line.lower():
                return True, idx

        # 3. Normalized whitespace check
        norm_q = " ".join(q_clean.split())
        norm_text = " ".join(notice_text.split())
        if norm_q.lower() in norm_text.lower():
            return True, None

        return False, None


# Global singleton instance
evidence_service = EvidenceService()
