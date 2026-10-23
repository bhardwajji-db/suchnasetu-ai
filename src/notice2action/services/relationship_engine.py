"""
Relationship Detection Engine for SuchnaSetu AI.
Identifies relationships between official administrative circulars,
such as Base Notices, Corrigenda, Amendments, Extensions, and Cancellations.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple
from notice2action.schemas import (
    RelationshipType,
    NoticeRelationship,
)


class RelationshipEngine:
    """
    Deterministic rule-based and citation-backed engine for identifying
    administrative notice relationships (AMENDMENT, EXTENSION, CANCELLATION, etc.).
    """

    def detect_relationship(
        self,
        source_id: str,
        target_id: str,
        source_text: str,
        target_text: str,
    ) -> NoticeRelationship:
        """
        Analyzes source_text (e.g., earlier or base notice) and target_text (e.g., subsequent circular)
        to identify the relationship type and extract verbatim citation evidence.
        """
        # Search target notice (typically the newer circular) for references to source
        rel_type, conf, is_explicit, quote, ref, explanation = self._classify_from_text(
            target_text, base_text=source_text
        )

        # If target text was not the amendment, check if source text references target
        if rel_type in (RelationshipType.RELATED, RelationshipType.UNRESOLVED):
            rev_type, rev_conf, rev_explicit, rev_quote, rev_ref, rev_exp = self._classify_from_text(
                source_text, base_text=target_text
            )
            if rev_explicit or rev_conf == "HIGH":
                rel_type = rev_type
                conf = rev_conf
                is_explicit = rev_explicit
                quote = rev_quote
                ref = rev_ref
                explanation = f"Notice A references Notice B: {rev_exp}"

        return NoticeRelationship(
            source_notice_id=source_id,
            target_notice_id=target_id,
            relationship_type=rel_type,
            confidence=conf,
            is_explicit=is_explicit,
            evidence_quote=quote,
            source_reference=ref,
            explanation=explanation,
        )

    def _classify_from_text(
        self,
        text: str,
        base_text: str = "",
    ) -> Tuple[RelationshipType, str, bool, str, Optional[str], str]:
        """
        Internal classifier scanning for explicit administrative patterns.
        """
        clean_text = text.strip()
        if not clean_text:
            return (
                RelationshipType.UNRESOLVED,
                "LOW",
                False,
                "",
                None,
                "No text available to evaluate relationship.",
            )

        # 1. Check for explicit Cancellation
        cancel_patterns = [
            r"(hereby\s+cancelled|stands\s+cancelled|withdrawn\s+with\s+immediate\s+effect)",
            r"(annulled|revoked\s+in\s+its\s+entirety|advertisement\s+is\s+cancelled)",
            r"(निरस्त\s+किया\s+जाता\s+है|रद्द\s+किया\s+जाता\s+है)",
        ]
        for pat in cancel_patterns:
            m = re.search(pat, clean_text, re.IGNORECASE)
            if m:
                sentence = self._extract_surrounding_sentence(clean_text, m.start())
                ref = self._extract_reference_number(clean_text)
                return (
                    RelationshipType.CANCELLATION,
                    "HIGH",
                    ref is not None,
                    sentence,
                    ref,
                    "Document explicitly cancels or withdraws the referenced notice.",
                )

        # 2. Check for explicit Corrigendum / Amendment
        amend_patterns = [
            r"(in\s+partial\s+modification\s+to|corrigendum\s+to|addendum\s+to)",
            r"(amendment\s+to\s+advertisement|amendment\s+notice|modification\s+notice)",
            r"(संशोधन\s+सूचना|शुद्धिपत्र|आंशिक\s+संशोधन)",
        ]
        for pat in amend_patterns:
            m = re.search(pat, clean_text, re.IGNORECASE)
            if m:
                sentence = self._extract_surrounding_sentence(clean_text, m.start())
                ref = self._extract_reference_number(clean_text)
                return (
                    RelationshipType.AMENDMENT,
                    "HIGH",
                    ref is not None,
                    sentence,
                    ref,
                    "Document explicitly modifies, amends, or adds terms to the referenced notice.",
                )

        # 3. Check for Deadline Extension
        extension_patterns = [
            r"(last\s+date\s+(?:for\s+submission\s+)?is\s+hereby\s+extended)",
            r"(extended\s+up\s+to|extended\s+till|deadline\s+is\s+extended)",
            r"(अंतिम\s+तिथि\s+विस्तारित|अंतिम\s+तिथि\s+बढ़ाई\s+जाती\s+है)",
        ]
        for pat in extension_patterns:
            m = re.search(pat, clean_text, re.IGNORECASE)
            if m:
                sentence = self._extract_surrounding_sentence(clean_text, m.start())
                ref = self._extract_reference_number(clean_text)
                return (
                    RelationshipType.EXTENSION,
                    "HIGH",
                    ref is not None,
                    sentence,
                    ref,
                    "Document extends the final submission date or timeline.",
                )

        # 4. Check for Replacement / Supersession
        replacement_patterns = [
            r"(in\s+supersession\s+of|supersedes\s+all\s+previous|replaces\s+notice)",
            r"(पूर्व\s+सभी\s+आदेशों\s+के\s+अतिक्रमण\s+में)",
        ]
        for pat in replacement_patterns:
            m = re.search(pat, clean_text, re.IGNORECASE)
            if m:
                sentence = self._extract_surrounding_sentence(clean_text, m.start())
                ref = self._extract_reference_number(clean_text)
                return (
                    RelationshipType.REPLACEMENT,
                    "HIGH",
                    ref is not None,
                    sentence,
                    ref,
                    "Document supersedes and replaces previous circulars in full.",
                )

        # 5. Check if reference numbers match directly
        ref_source = self._extract_reference_number(base_text)
        ref_target = self._extract_reference_number(clean_text)
        if ref_source and ref_target and ref_source.lower() in clean_text.lower():
            # Exact reference found in text
            return (
                RelationshipType.AMENDMENT,
                "HIGH",
                True,
                f"Referenced circular: {ref_source}",
                ref_source,
                f"Document explicitly references Notice ID '{ref_source}'.",
            )

        # Default fallback: Related or Unresolved
        if base_text and len(clean_text) > 20:
            return (
                RelationshipType.RELATED,
                "MEDIUM",
                False,
                "",
                None,
                "Both notices share domain context, but no explicit corrigendum link was detected.",
            )

        return (
            RelationshipType.UNRESOLVED,
            "LOW",
            False,
            "",
            None,
            "Insufficient evidence to establish relationship between notices.",
        )

    def _extract_surrounding_sentence(self, text: str, pos: int) -> str:
        """Extracts the complete sentence containing the regex match position."""
        start = text.rfind(".", 0, pos)
        if start == -1:
            start = text.rfind("\n", 0, pos)
        start = 0 if start == -1 else start + 1

        end = text.find(".", pos)
        if end == -1:
            end = text.find("\n", pos)
        end = len(text) if end == -1 else end + 1

        sentence = text[start:end].strip()
        # Clean up excessive newlines
        return re.sub(r"\s+", " ", sentence)

    def _extract_reference_number(self, text: str) -> Optional[str]:
        """Extracts official notification reference ID (e.g. Advt No. 05/2026)."""
        patterns = [
            r"(?:Advt\.?\s*No\.?|Notice\s*No\.?|Notification\s*No\.?|Ref\s*No\.?|Circular\s*No\.?)\s*[:\-]?\s*([A-Za-z0-9\/\-\.]+)",
            r"(?:संख्या|क्रमांक)\s*[:\-]?\s*([A-Za-z0-9\/\-\.]+)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        return None


relationship_engine = RelationshipEngine()
