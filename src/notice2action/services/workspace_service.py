"""
Cross-Notice Intelligence & Workspace Service.
Maintains a multi-document workspace, infers chronological timelines,
maps inter-document relationship graphs with defensible confidence states,
and flags cross-notice contradictions and conflicts.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from notice2action.schemas import (
    NoticeMetadata,
    CrossNoticeRelationship,
    RelationshipType,
    RelationshipConfidence,
    TimelineEvent,
    CrossNoticeConflict,
    WorkspaceTimelineReport,
)
from notice2action.services.relationship_engine import relationship_engine


class WorkspaceService:
    """Manages multi-notice workspaces, graphs, timelines, and cross-notice conflicts."""

    def __init__(self, workspace_id: str = "default_workspace"):
        self.workspace_id = workspace_id
        self._notices: Dict[str, NoticeMetadata] = {}

    @staticmethod
    def _compute_fingerprint(text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]

    @classmethod
    def extract_metadata(cls, text: str, title: Optional[str] = None, doc_id: Optional[str] = None) -> NoticeMetadata:
        """Heuristically extracts official metadata from notice text."""
        doc_id = doc_id or f"doc_{uuid.uuid4().hex[:6]}"
        fp = cls._compute_fingerprint(text)

        # 1. Authority
        authority = "Government Authority"
        auth_match = re.search(
            r"(?:directorate|department|ministry|commission|corporation|board|university|authority)\s+of\s+[^\n,]+",
            text,
            re.IGNORECASE,
        )
        if auth_match:
            authority = auth_match.group(0).strip()
        else:
            first_lines = text.strip().splitlines()[:3]
            for l in first_lines:
                if len(l.strip()) > 5:
                    authority = l.strip()
                    break

        # 2. Reference Number
        ref_match = re.search(
            r"(?:Ref(?:erence)?\s*(?:No\.?|Number)|Advt\.?\s*No\.?|Notification\s*No\.?)[:\s]+([A-Z0-9/\-_.]+)",
            text,
            re.IGNORECASE,
        )
        ref_no = ref_match.group(1).strip() if ref_match else None

        # 3. Notice Date
        date_match = re.search(
            r"(?:dated|date)[:\s]+([^\n\.,;]+(?:202\d))",
            text,
            re.IGNORECASE,
        )
        notice_date = date_match.group(1).strip() if date_match else "Date Not Stated"

        # 4. Document Type
        text_upper = text.upper()
        if "CORRIGENDUM" in text_upper:
            doc_type = "CORRIGENDUM"
        elif "ADDENDUM" in text_upper:
            doc_type = "ADDENDUM"
        elif "EXTENSION" in text_upper and "DEADLINE" in text_upper:
            doc_type = "EXTENSION"
        elif "CANCELLATION" in text_upper:
            doc_type = "CANCELLATION"
        else:
            doc_type = "ORIGINAL_NOTICE"

        extracted_title = title or (f"{doc_type.replace('_', ' ').title()}: {ref_no or authority}")

        return NoticeMetadata(
            id=doc_id,
            title=extracted_title,
            reference_number=ref_no,
            issuing_authority=authority,
            notice_date=notice_date,
            ingested_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            char_count=len(text),
            raw_text=text,
            fingerprint=fp,
            document_type=doc_type,
        )

    def add_notice(self, text: str, title: Optional[str] = None, doc_id: Optional[str] = None) -> NoticeMetadata:
        """Adds a notice to the workspace registry."""
        meta = self.extract_metadata(text, title=title, doc_id=doc_id)
        self._notices[meta.id] = meta
        return meta

    def get_notices(self) -> List[NoticeMetadata]:
        return list(self._notices.values())

    def clear(self):
        self._notices.clear()

    def build_report(self, active_notice_id: Optional[str] = None) -> WorkspaceTimelineReport:
        """
        Builds the complete cross-notice intelligence report,
        generating relationships, timeline events, and conflict records.
        """
        notices_list = list(self._notices.values())
        relationships: List[CrossNoticeRelationship] = []
        timeline: List[TimelineEvent] = []
        conflicts: List[CrossNoticeConflict] = []

        # 1. Timeline events
        for doc in notices_list:
            timeline.append(
                TimelineEvent(
                    id=f"evt_{doc.id}",
                    date=doc.notice_date or "Unknown Date",
                    notice_id=doc.id,
                    notice_title=doc.title,
                    event_type=doc.document_type,
                    summary=f"{doc.issuing_authority} issued {doc.document_type.lower()}: {doc.reference_number or 'Circular'}",
                    evidence_quote=f"Dated: {doc.notice_date or 'N/A'}, Ref: {doc.reference_number or 'N/A'}",
                    is_active=True,
                )
            )

        # 2. Cross-Document Pairwise Analysis
        for i in range(len(notices_list)):
            for j in range(i + 1, len(notices_list)):
                doc_a = notices_list[i]
                doc_b = notices_list[j]

                # Run relationship_engine detection in both directions
                rel_ab = relationship_engine.detect_relationship(
                    source_id=doc_a.id,
                    target_id=doc_b.id,
                    source_text=doc_a.raw_text,
                    target_text=doc_b.raw_text,
                )
                rel_ba = relationship_engine.detect_relationship(
                    source_id=doc_b.id,
                    target_id=doc_a.id,
                    source_text=doc_b.raw_text,
                    target_text=doc_a.raw_text,
                )

                chosen_rel = rel_ba if rel_ba.relationship_type not in [RelationshipType.UNRESOLVED, RelationshipType.RELATED] else (
                    rel_ab if rel_ab.relationship_type != RelationshipType.UNRESOLVED else rel_ba
                )
                source_id = doc_b.id if chosen_rel is rel_ba else doc_a.id
                target_id = doc_a.id if chosen_rel is rel_ba else doc_b.id

                # Assign confidence level
                if chosen_rel.is_explicit or chosen_rel.confidence == "HIGH":
                    conf_level = RelationshipConfidence.VERIFIED
                    precedence = "SOURCE_SUPERSEDED_BY_TARGET" if chosen_rel.relationship_type in [
                        RelationshipType.AMENDMENT, RelationshipType.REPLACEMENT, RelationshipType.CANCELLATION
                    ] else "PARALLEL"
                elif chosen_rel.confidence == "MEDIUM":
                    conf_level = RelationshipConfidence.STRONG_CANDIDATE
                    precedence = "PARALLEL"
                elif chosen_rel.relationship_type != RelationshipType.UNRESOLVED:
                    conf_level = RelationshipConfidence.POSSIBLE
                    precedence = "PARALLEL"
                else:
                    conf_level = RelationshipConfidence.UNKNOWN
                    precedence = "INDEPENDENT"

                relationships.append(
                    CrossNoticeRelationship(
                        id=f"rel_{doc_a.id}_{doc_b.id}",
                        source_notice_id=source_id,
                        target_notice_id=target_id,
                        relationship_type=chosen_rel.relationship_type,
                        confidence_level=conf_level,
                        evidence_quote=chosen_rel.evidence_quote or "",
                        rationale=chosen_rel.explanation,
                        precedence_status=precedence,
                    )
                )

                # 3. Conflict Detection Check
                # If both notices have deadlines but neither explicitly references or cancels the other
                deadline_pattern = r"(?:deadline|last date|closing date)[^\n\.;]*?(?:[:=]|\b(?:is|shall be)\b)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|[^\n\.;]+)"
                dl_a = re.search(deadline_pattern, doc_a.raw_text, re.IGNORECASE)
                dl_b = re.search(deadline_pattern, doc_b.raw_text, re.IGNORECASE)

                if dl_a and dl_b and dl_a.group(1).strip() != dl_b.group(1).strip():
                    if chosen_rel.relationship_type not in [RelationshipType.AMENDMENT, RelationshipType.EXTENSION]:
                        conflicts.append(
                            CrossNoticeConflict(
                                id=f"cnf_{doc_a.id}_{doc_b.id}",
                                notice_a_id=doc_a.id,
                                notice_b_id=doc_b.id,
                                field_name="Application Deadline",
                                value_a=dl_a.group(1).strip(),
                                value_b=dl_b.group(1).strip(),
                                evidence_a=dl_a.group(0).strip(),
                                evidence_b=dl_b.group(0).strip(),
                                conflict_severity="CRITICAL",
                                resolution_guidance=(
                                    "Both notices state conflicting submission deadlines without an explicit "
                                    "cross-referencing corrigendum clause. Verification with issuing office is recommended."
                                ),
                                status="UNRESOLVED",
                            )
                        )

        return WorkspaceTimelineReport(
            workspace_id=self.workspace_id,
            notices=notices_list,
            relationships=relationships,
            timeline=timeline,
            conflicts=conflicts,
            active_notice_id=active_notice_id or (notices_list[0].id if notices_list else None),
        )


# Global workspace singleton for standard session
_GLOBAL_WORKSPACE = WorkspaceService("default_workspace")


def get_workspace() -> WorkspaceService:
    return _GLOBAL_WORKSPACE
