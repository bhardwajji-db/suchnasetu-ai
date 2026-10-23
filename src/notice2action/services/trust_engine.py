"""
Evidence-First Trust Engine.
Verifies claims and excerpts against the ground truth notice text,
attributing line numbers, detecting ungrounded citations, and ensuring
documents are handled as inert, untrusted data.
"""

from __future__ import annotations

import difflib
import re
import uuid
from typing import Optional, Tuple, List

from notice2action.schemas import (
    TrustEvidence,
    EvidenceVerificationStatus,
    VerifyEvidenceResponse,
)
from notice2action.security import detect_prompt_injection


class TrustEngine:
    """Verifies that evidence excerpts exist verbatim in source documents."""

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return " ".join(text.split())

    @classmethod
    def find_excerpt_lines(cls, source_text: str, excerpt: str) -> Tuple[Optional[int], Optional[int]]:
        """Finds 1-based start and end line numbers for an excerpt in source_text."""
        if not source_text or not excerpt:
            return None, None

        source_lines = source_text.splitlines()
        norm_excerpt = cls._normalize_whitespace(excerpt).lower()

        # Try exact line-substring search first
        for idx, line in enumerate(source_lines, start=1):
            if norm_excerpt in cls._normalize_whitespace(line).lower():
                return idx, idx

        # Try sliding window over lines (up to 6 lines for multiline quotes)
        for window_size in range(2, min(7, len(source_lines) + 1)):
            for i in range(len(source_lines) - window_size + 1):
                window_text = cls._normalize_whitespace(" ".join(source_lines[i : i + window_size])).lower()
                if norm_excerpt in window_text:
                    return i + 1, i + window_size

        return None, None

    @classmethod
    def verify_excerpt(
        cls,
        source_text: str,
        excerpt: str,
        claim_text: str = "",
        source_doc_title: str = "Active Notice",
        source_doc_id: Optional[str] = None,
        page_number: Optional[int] = 1,
    ) -> VerifyEvidenceResponse:
        """
        Validates whether an excerpt is legitimately grounded in source_text.
        Distinguishes exact quotes, OCR noise/fuzzy matches, and ungrounded hallucinations.
        """
        evidence_id = str(uuid.uuid4())[:8]

        # 1. Check prompt injection safety
        injection_warning = detect_prompt_injection(excerpt) if excerpt else None
        is_inert_safe = injection_warning is None

        if not excerpt or not excerpt.strip():
            evidence = TrustEvidence(
                evidence_id=evidence_id,
                claim_text=claim_text,
                source_doc_id=source_doc_id,
                source_doc_title=source_doc_title,
                page_number=page_number,
                verbatim_excerpt="",
                verification_status=EvidenceVerificationStatus.UNVERIFIED,
                confidence_rationale="No supporting excerpt provided; claim is ungrounded.",
                is_inert_safe=is_inert_safe,
            )
            return VerifyEvidenceResponse(is_valid=False, evidence=evidence)

        if not source_text or not source_text.strip():
            evidence = TrustEvidence(
                evidence_id=evidence_id,
                claim_text=claim_text,
                source_doc_id=source_doc_id,
                source_doc_title=source_doc_title,
                page_number=page_number,
                verbatim_excerpt=excerpt,
                verification_status=EvidenceVerificationStatus.UNVERIFIED,
                confidence_rationale="Source notice document is empty.",
                is_inert_safe=is_inert_safe,
            )
            return VerifyEvidenceResponse(is_valid=False, evidence=evidence)

        norm_source = cls._normalize_whitespace(source_text)
        norm_excerpt = cls._normalize_whitespace(excerpt)

        # 2. Exact match check
        if norm_excerpt.lower() in norm_source.lower():
            start_line, end_line = cls.find_excerpt_lines(source_text, excerpt)
            line_str = f"lines {start_line}-{end_line}" if start_line != end_line else f"line {start_line}"
            evidence = TrustEvidence(
                evidence_id=evidence_id,
                claim_text=claim_text,
                source_doc_id=source_doc_id,
                source_doc_title=source_doc_title,
                page_number=page_number,
                line_start=start_line,
                line_end=end_line,
                verbatim_excerpt=excerpt,
                verification_status=EvidenceVerificationStatus.VERIFIED_IN_SOURCE,
                confidence_rationale=f"Exact verbatim quotation verified in notice ({line_str}).",
                is_inert_safe=is_inert_safe,
            )
            return VerifyEvidenceResponse(is_valid=True, evidence=evidence)

        # 3. Fuzzy match check for OCR degradation (single-character errors, hyphenation)
        # Search sentences in source
        sentences = re.split(r"(?<=[.!?\n])\s+", source_text)
        best_ratio = 0.0
        best_match = ""
        for s in sentences:
            s_norm = cls._normalize_whitespace(s)
            if not s_norm:
                continue
            ratio = difflib.SequenceMatcher(None, norm_excerpt.lower(), s_norm.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = s_norm

        if best_ratio >= 0.78:
            start_line, end_line = cls.find_excerpt_lines(source_text, best_match)
            evidence = TrustEvidence(
                evidence_id=evidence_id,
                claim_text=claim_text,
                source_doc_id=source_doc_id,
                source_doc_title=source_doc_title,
                page_number=page_number,
                line_start=start_line,
                line_end=end_line,
                verbatim_excerpt=best_match,
                verification_status=EvidenceVerificationStatus.UNCERTAIN_OCR,
                confidence_rationale=(
                    f"Fuzzy match detected ({int(best_ratio * 100)}% similarity). "
                    "Likely contains OCR artifact, hyphenation split, or minor transcription difference."
                ),
                is_inert_safe=is_inert_safe,
            )
            return VerifyEvidenceResponse(is_valid=True, evidence=evidence, suggested_match=best_match)

        # 4. Failed verification
        evidence = TrustEvidence(
            evidence_id=evidence_id,
            claim_text=claim_text,
            source_doc_id=source_doc_id,
            source_doc_title=source_doc_title,
            page_number=page_number,
            verbatim_excerpt=excerpt,
            verification_status=EvidenceVerificationStatus.UNVERIFIED,
            confidence_rationale="Citation failed verification: quoted text could not be located in the notice.",
            is_inert_safe=is_inert_safe,
        )
        return VerifyEvidenceResponse(is_valid=False, evidence=evidence)
