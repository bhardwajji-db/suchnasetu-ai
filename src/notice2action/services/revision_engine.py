"""
Semantic Revision Ledger Engine for SuchnaSetu AI.
Computes field-by-field deltas between original and amended/revised notices,
capturing old vs new values, verbatim citations, and change classifications.
"""

from __future__ import annotations

import re
import datetime
from typing import List, Tuple, Optional
from notice2action.schemas import (
    StructuredNotice,
    RevisionLedger,
    RevisionEntry,
    ChangeCategory,
    NoticeRelationship,
    CertaintyStatus,
    NOT_STATED_LABEL,
)
from notice2action.services.relationship_engine import relationship_engine


class RevisionEngine:
    """
    Deterministic comparison engine for tracking modifications across notice versions.
    Enforces that numeric and date deltas are preserved accurately without hallucination.
    """

    FIELDS_TO_COMPARE = [
        ("purpose", "Main Purpose & Subject"),
        ("deadline", "Application Deadline & Key Dates"),
        ("eligibility", "Eligibility & Qualification Rules"),
        ("fee_or_cost", "Application Fee & Payment Terms"),
        ("required_documents", "Required Documents & Certificates"),
        ("required_actions", "Action Steps & Submission Mode"),
        ("contact_details", "Helpline & Contact Information"),
        ("issuing_authority", "Issuing Authority & Office"),
        ("notice_reference_number", "Notice Reference Number"),
    ]

    @classmethod
    def compare(
        cls,
        source_text: str,
        target_text: str,
        source_title: str = "Original Notice",
        target_title: str = "Revised Notice / Corrigendum",
    ) -> RevisionLedger:
        """Convenience method comparing two notice texts directly."""
        src_notice = cls._heuristic_extract_notice(source_text)
        tgt_notice = cls._heuristic_extract_notice(target_text)
        engine = cls()
        return engine.build_revision_ledger(
            source_id="source_doc",
            target_id="target_doc",
            source_notice=src_notice,
            target_notice=tgt_notice,
            source_raw_text=source_text,
            target_raw_text=target_text,
            source_title=source_title,
            target_title=target_title,
        )

    @classmethod
    def _heuristic_extract_notice(cls, text: str) -> StructuredNotice:
        """Deterministically extracts key facts for revision diffing without requiring live LLM."""
        from notice2action.schemas import ExtractedFact, SixCoreFields

        def make_fact(key: str, val: str, quote: Optional[str] = None):
            is_stated = val != NOT_STATED_LABEL and bool(val)
            return ExtractedFact(
                field_name=key,
                value=val if is_stated else NOT_STATED_LABEL,
                status=CertaintyStatus.STATED if is_stated else CertaintyStatus.NOT_STATED,
                evidence_quote=quote if is_stated else None,
            )

        # 1. Authority
        auth_match = re.search(r"(?:Department|Directorate|Ministry|Commission|Board|Authority)\s+of\s+[^\n,]+", text, re.IGNORECASE)
        auth_val = auth_match.group(0).strip() if auth_match else (text.strip().splitlines()[0] if text.strip() else NOT_STATED_LABEL)

        # 2. Ref no
        ref_match = re.search(r"(?:Advt\.?\s*No\.?|Ref(?:erence)?\s*(?:No\.?)?|Notification\s*No\.?)[:\s]+([^\n,;]+)", text, re.IGNORECASE)
        ref_val = ref_match.group(1).strip() if ref_match else NOT_STATED_LABEL

        # 3. Deadline
        dl_match = re.search(r"(?:deadline|last date|extended to)[^\n]*?\b([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]+,?\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b", text, re.IGNORECASE)
        dl_val = dl_match.group(1).strip() if dl_match else NOT_STATED_LABEL
        dl_quote = dl_match.group(0).strip() if dl_match else None

        # 4. Fee
        fee_match = re.search(r"(?:fee|charges|amount)[^\n\.]*?(?:Rs\.?|INR)?\s*(\d+)", text, re.IGNORECASE)
        fee_val = f"Rs. {fee_match.group(1)}" if fee_match else NOT_STATED_LABEL
        fee_quote = fee_match.group(0).strip() if fee_match else None

        # 5. Eligibility / Marks
        elig_match = re.search(r"(?:minimum|qualifying|aggregate|at least)?\s*(\d{1,2}(?:\.\d+)?)%\s*(?:marks|aggregate)?", text, re.IGNORECASE)
        if elig_match:
            elig_val = f"Minimum {elig_match.group(1)}% marks"
            elig_quote = elig_match.group(0).strip()
        else:
            deg_match = re.search(r"(?:Master['’]?s|Bachelor['’]?s|B\.Tech|Degree|Diploma)[^\n,.]*", text, re.IGNORECASE)
            elig_val = deg_match.group(0).strip() if deg_match else NOT_STATED_LABEL
            elig_quote = deg_match.group(0).strip() if deg_match else None

        # 6. Documents
        doc_match = re.search(r"(?:documents?|certificates?|marksheet|affidavit)[:\s]+([^\n.]+)", text, re.IGNORECASE)
        doc_val = doc_match.group(1).strip() if doc_match else NOT_STATED_LABEL

        purpose_val = text.strip().splitlines()[0] if text.strip() else NOT_STATED_LABEL

        return StructuredNotice(
            issuing_authority=make_fact("issuing_authority", auth_val),
            notice_reference_number=make_fact("notice_reference_number", ref_val),
            notice_date=make_fact("notice_date", NOT_STATED_LABEL),
            recipient=make_fact("recipient", "All Candidates"),
            main_subject=make_fact("main_subject", purpose_val),
            required_action_and_deadline=make_fact("required_action_and_deadline", dl_val, dl_quote),
            purpose=make_fact("purpose", purpose_val),
            eligibility=make_fact("eligibility", elig_val, elig_quote),
            deadline=make_fact("deadline", dl_val, dl_quote),
            fee_or_cost=make_fact("fee_or_cost", fee_val, fee_quote),
            required_documents=make_fact("required_documents", doc_val),
            required_actions=make_fact("required_actions", dl_val),
            contact_details=make_fact("contact_details", NOT_STATED_LABEL),
            important_conditions=make_fact("important_conditions", NOT_STATED_LABEL),
        )

    def build_revision_ledger(
        self,
        source_id: str,
        target_id: str,
        source_notice: StructuredNotice,
        target_notice: StructuredNotice,
        source_raw_text: str = "",
        target_raw_text: str = "",
        source_title: str = "Original Notice",
        target_title: str = "Revised Notice / Corrigendum",
    ) -> RevisionLedger:
        """
        Builds a comprehensive RevisionLedger comparing source_notice and target_notice.
        """
        # 1. Detect notice relationship
        rel = relationship_engine.detect_relationship(
            source_id=source_id,
            target_id=target_id,
            source_text=source_raw_text or source_notice.purpose.value,
            target_text=target_raw_text or target_notice.purpose.value,
        )

        # 2. Compare fields
        entries: List[RevisionEntry] = []
        modified_count = 0
        added_count = 0
        removed_count = 0

        for field_key, display_name in self.FIELDS_TO_COMPARE:
            old_fact = getattr(source_notice, field_key, None)
            new_fact = getattr(target_notice, field_key, None)

            old_val = self._get_fact_value(old_fact)
            new_val = self._get_fact_value(new_fact)

            old_quote = getattr(old_fact, "evidence_quote", None) if old_fact else None
            new_quote = getattr(new_fact, "evidence_quote", None) if new_fact else None

            old_page = getattr(old_fact, "page_number", None) if old_fact else None
            new_page = getattr(new_fact, "page_number", None) if new_fact else None

            category, requires_review, explanation = self._classify_change(
                field_key, old_val, new_val, old_fact, new_fact
            )

            if category == ChangeCategory.MODIFIED:
                modified_count += 1
            elif category == ChangeCategory.ADDED:
                added_count += 1
            elif category == ChangeCategory.REMOVED:
                removed_count += 1

            entries.append(
                RevisionEntry(
                    field_name=field_key,
                    display_name=display_name,
                    old_value=old_val,
                    new_value=new_val,
                    change_category=category,
                    old_evidence_quote=old_quote,
                    new_evidence_quote=new_quote,
                    old_page=old_page,
                    new_page=new_page,
                    requires_review=requires_review,
                    explanation=explanation,
                )
            )

        # 3. Build summary
        summary = self._generate_summary(
            rel, modified_count, added_count, removed_count, entries
        )

        return RevisionLedger(
            source_notice_id=source_id,
            target_notice_id=target_id,
            source_title=source_title,
            target_title=target_title,
            relationship=rel,
            entries=entries,
            summary_of_changes=summary,
            created_at=datetime.datetime.utcnow().isoformat() + "Z",
        )

    def _get_fact_value(self, fact) -> str:
        if fact is None:
            return NOT_STATED_LABEL
        if getattr(fact, "user_confirmed", False) and getattr(fact, "confirmed_value", None):
            return fact.confirmed_value
        return fact.value or NOT_STATED_LABEL

    def _classify_change(
        self,
        field_key: str,
        old_val: str,
        new_val: str,
        old_fact,
        new_fact,
    ) -> Tuple[ChangeCategory, bool, str]:
        old_norm = self._normalize_string(old_val)
        new_norm = self._normalize_string(new_val)

        old_is_unstated = (
            old_norm in ("", "not stated in the notice", "not stated")
            or (old_fact and old_fact.status == CertaintyStatus.NOT_STATED)
        )
        new_is_unstated = (
            new_norm in ("", "not stated in the notice", "not stated")
            or (new_fact and new_fact.status == CertaintyStatus.NOT_STATED)
        )

        # Case 1: Both unstated
        if old_is_unstated and new_is_unstated:
            return ChangeCategory.UNCHANGED, False, "Not specified in either notice version."

        # Case 2: Added in revised notice
        if old_is_unstated and not new_is_unstated:
            return ChangeCategory.ADDED, False, "Newly introduced in the revised circular."

        # Case 3: Removed or omitted in revised notice
        if not old_is_unstated and new_is_unstated:
            return (
                ChangeCategory.REMOVED,
                True,
                "Clause was present in the base notice but is omitted or silent in the revised circular.",
            )

        # Case 4: Identical normalized content
        if old_norm == new_norm:
            return ChangeCategory.UNCHANGED, False, "Terms remain identical across notice versions."

        # Case 5: Uncertain status in either notice
        old_uncertain = old_fact and old_fact.status in (CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING)
        new_uncertain = new_fact and new_fact.status in (CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING)
        if old_uncertain or new_uncertain:
            return (
                ChangeCategory.UNCERTAIN,
                True,
                "One or both notices report uncertain or tentative values for this field; official verification advised.",
            )

        # Case 6: Modified terms (e.g. deadline extended, fee altered)
        if field_key == "deadline":
            return (
                ChangeCategory.MODIFIED,
                False,
                "Submission timeline or key date was modified in the revised circular.",
            )
        if field_key == "fee_or_cost":
            return (
                ChangeCategory.MODIFIED,
                False,
                "Fee structure or financial requirement was modified.",
            )

        return (
            ChangeCategory.MODIFIED,
            False,
            "Requirement terms differ between notice versions.",
        )

    def _normalize_string(self, s: str) -> str:
        """Removes punctuation, excess spaces, and lowercases for deterministic equality checks."""
        if not s:
            return ""
        s = s.lower()
        s = re.sub(r"[^\w\s\d]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _generate_summary(
        self,
        rel: NoticeRelationship,
        modified: int,
        added: int,
        removed: int,
        entries: List[RevisionEntry],
    ) -> str:
        parts = []
        if rel.relationship_type.value in ("AMENDMENT", "EXTENSION", "CANCELLATION"):
            parts.append(f"Relationship: {rel.relationship_type.value} ({rel.confidence} confidence).")
        else:
            parts.append(f"Notices compared ({rel.relationship_type.value}).")

        # Specific deadline notice
        dl_entry = next((e for e in entries if e.field_name == "deadline"), None)
        if dl_entry and dl_entry.change_category == ChangeCategory.MODIFIED:
            parts.append(f"Key change: Deadline updated to '{dl_entry.new_value}'.")

        changes_desc = []
        if modified > 0:
            changes_desc.append(f"{modified} modified")
        if added > 0:
            changes_desc.append(f"{added} added")
        if removed > 0:
            changes_desc.append(f"{removed} removed")

        if changes_desc:
            parts.append("Deltas detected: " + ", ".join(changes_desc) + ".")
        else:
            parts.append("No material differences detected between notice fields.")

        return " ".join(parts)


revision_engine = RevisionEngine()
