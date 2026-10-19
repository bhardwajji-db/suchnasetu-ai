"""
Evidence Grounding Engine for Notice2Action AI.
Verifies quotations against source notice text, prevents hallucinated dates/fees/documents,
and calibrates certainty states.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple, List, Dict, Any

from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    StructuredNotice,
    NOT_STATED_LABEL,
    NEEDS_CONFIRMATION_LABEL,
)


def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace for reliable verbatim matching."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def locate_quote_in_text(quote: str, raw_text: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if a quote exists verbatim or normalized in the notice.
    Returns (found: bool, location_description: Optional[str]).
    """
    if not quote or not raw_text:
        return False, None

    norm_quote = normalize_whitespace(quote).lower()
    norm_text = normalize_whitespace(raw_text).lower()

    if norm_quote not in norm_text:
        return False, None

    # Find line numbers in the original raw text
    lines = raw_text.splitlines()
    matching_lines: List[int] = []
    cleaned_quote = quote.strip().lower()

    for idx, line in enumerate(lines, 1):
        if cleaned_quote in line.lower() or any(
            part.strip() and part.strip().lower() in line.lower()
            for part in cleaned_quote.split("\n")
        ):
            matching_lines.append(idx)

    if matching_lines:
        if len(matching_lines) == 1:
            loc = f"Line {matching_lines[0]}"
        else:
            loc = f"Lines {matching_lines[0]}-{matching_lines[-1]}"
        return True, loc

    return True, "Found in notice"


def extract_critical_tokens(text: str) -> List[str]:
    """
    Extracts dates, years, numbers, percentages, and monetary amounts
    from text to verify factual consistency.
    """
    # Matches dates (e.g. 15-11-2026, Nov 15, 2026), percentages (85%), amounts (Rs. 500, $1000, 50,000)
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b",
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4}\b",
        r"(?:rs\.?|inr|₹|\$)\s*\d+(?:,\d+)*(?:\.\d+)?",
        r"\b\d+%\b",
        r"\b\d{4,}\b",
    ]
    tokens = []
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            tokens.append(match.group(0).lower().strip())
    return tokens


def check_uncertainty_markers(text: str) -> bool:
    """Checks for phrases indicating tentative or uncertain information."""
    markers = [
        r"\btentative\b",
        r"\bsubject to change\b",
        r"\bto be announced\b",
        r"\btba\b",
        r"\btbd\b",
        r"\bprovisional\b",
        r"\bapprox(?:imate)?\b",
        r"\bunconfirmed\b",
        r"\blikely\b",
    ]
    for m in markers:
        if re.search(m, text, re.IGNORECASE):
            return True
    return False


def verify_fact_grounding(fact: ExtractedFact, raw_notice_text: str) -> ExtractedFact:
    """
    Verifies an extracted fact against raw notice text:
    1. Checks if it represents an unstated field.
    2. Validates evidence quotation presence.
    3. Detects altered numbers, dates, or amounts.
    4. Detects tentative or contradictory markers.
    """
    val_lower = fact.value.lower()

    # Case 1: Unstated
    if (
        fact.status == CertaintyStatus.NOT_STATED
        or "not stated" in val_lower
        or "not mentioned" in val_lower
        or "n/a" == val_lower.strip()
        or not fact.value.strip()
    ):
        return ExtractedFact(
            field_name=fact.field_name,
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
            evidence_quote=None,
            source_location=None,
            requires_confirmation=False,
            user_confirmed=fact.user_confirmed,
            explanation="This information is not stated in the supplied notice.",
        )

    # Case 2: Evidence Quote Verification
    if not fact.evidence_quote or not fact.evidence_quote.strip():
        # No evidence quote provided for a claimed fact
        return ExtractedFact(
            field_name=fact.field_name,
            value=fact.value,
            status=CertaintyStatus.UNCERTAIN,
            evidence_quote=None,
            source_location=None,
            requires_confirmation=True,
            user_confirmed=fact.user_confirmed,
            explanation="No direct quotation from the notice was provided to substantiate this claim.",
        )

    found, loc = locate_quote_in_text(fact.evidence_quote, raw_notice_text)
    if not found:
        # Quote does not exist in the source notice! Hallucination / invention.
        return ExtractedFact(
            field_name=fact.field_name,
            value=fact.value,
            status=CertaintyStatus.UNCERTAIN,
            evidence_quote=fact.evidence_quote,
            source_location=None,
            requires_confirmation=True,
            user_confirmed=fact.user_confirmed,
            explanation="The provided evidence quotation could not be found anywhere in the notice text.",
        )

    # Case 3: Critical Entity Verification (dates, amounts, numbers)
    # Ensure critical numbers in the extracted value exist in the quote or notice
    fact_tokens = extract_critical_tokens(fact.value)
    notice_tokens = extract_critical_tokens(raw_notice_text)
    quote_tokens = extract_critical_tokens(fact.evidence_quote)

    for tok in fact_tokens:
        # If a critical token is in the fact but not in the quote or notice, it was altered/invented
        if tok not in quote_tokens and tok not in notice_tokens:
            return ExtractedFact(
                field_name=fact.field_name,
                value=fact.value,
                status=CertaintyStatus.CONFLICTING,
                evidence_quote=fact.evidence_quote,
                source_location=loc,
                requires_confirmation=True,
                user_confirmed=fact.user_confirmed,
                explanation=f"Critical detail '{tok}' was not found in the verified source quotation.",
            )

    # Case 4: Uncertainty markers
    if check_uncertainty_markers(fact.evidence_quote) or check_uncertainty_markers(fact.value):
        return ExtractedFact(
            field_name=fact.field_name,
            value=fact.value,
            status=CertaintyStatus.UNCERTAIN,
            evidence_quote=fact.evidence_quote,
            source_location=loc,
            requires_confirmation=True,
            user_confirmed=fact.user_confirmed,
            explanation="The notice indicates this detail is provisional, tentative, or subject to change.",
        )

    # Verified grounded fact
    req_confirmation = fact.requires_confirmation or (fact.status in [CertaintyStatus.CONFLICTING, CertaintyStatus.UNCERTAIN])
    return ExtractedFact(
        field_name=fact.field_name,
        value=fact.value,
        status=fact.status,
        evidence_quote=fact.evidence_quote,
        source_location=loc,
        requires_confirmation=req_confirmation,
        user_confirmed=fact.user_confirmed,
        explanation=fact.explanation,
    )


def verify_structured_notice(notice: StructuredNotice, raw_text: str) -> StructuredNotice:
    """
    Runs evidence verification across all structured fields of a notice.
    Automatically audits missing fields and uncertain details lists.
    """
    verified_purpose = verify_fact_grounding(notice.purpose, raw_text)
    verified_eligibility = verify_fact_grounding(notice.eligibility, raw_text)
    verified_deadline = verify_fact_grounding(notice.deadline, raw_text)
    verified_fee = verify_fact_grounding(notice.fee_or_cost, raw_text)
    verified_documents = verify_fact_grounding(notice.required_documents, raw_text)
    verified_contact = verify_fact_grounding(notice.contact_details, raw_text)
    verified_actions = verify_fact_grounding(notice.required_actions, raw_text)
    verified_conditions = verify_fact_grounding(notice.important_conditions, raw_text)

    # Recalculate missing information
    missing_items: List[str] = list(notice.missing_information)
    fields = [
        ("Purpose", verified_purpose),
        ("Eligibility", verified_eligibility),
        ("Deadline", verified_deadline),
        ("Application Fee", verified_fee),
        ("Required Documents", verified_documents),
        ("Official Contact", verified_contact),
        ("Required Actions", verified_actions),
    ]
    for fname, fval in fields:
        if fval.status == CertaintyStatus.NOT_STATED and fname not in missing_items:
            missing_items.append(fname)

    # Recalculate uncertain details
    uncertain_items: List[str] = list(notice.uncertain_or_conflicting_details)
    for fname, fval in fields:
        if fval.requires_confirmation and fname not in uncertain_items:
            uncertain_items.append(f"{fname}: {fval.explanation or 'Needs confirmation'}")

    return StructuredNotice(
        purpose=verified_purpose,
        eligibility=verified_eligibility,
        deadline=verified_deadline,
        fee_or_cost=verified_fee,
        required_documents=verified_documents,
        contact_details=verified_contact,
        required_actions=verified_actions,
        important_conditions=verified_conditions,
        missing_information=missing_items,
        uncertain_or_conflicting_details=uncertain_items,
        raw_notice_text=raw_text,
    )
