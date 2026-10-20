"""
Strict Data Schemas for Notice2Action AI.
Enforces evidence grounding, uncertainty states, and explicit missing-field tracking.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CertaintyStatus(str, Enum):
    STATED = "stated"
    NOT_STATED = "not_stated"
    UNCERTAIN = "uncertain"
    CONFLICTING = "conflicting"
    UNREADABLE = "unreadable"


NOT_STATED_LABEL = "Not stated in the notice."
NEEDS_CONFIRMATION_LABEL = "Needs confirmation."


class ExtractedFact(BaseModel):
    """Represents a discrete semantic fact extracted from a notice."""
    field_name: str = Field(description="Name of the extracted notice attribute")
    value: str = Field(description="Extracted value or explicit 'Not stated in the notice.'")
    status: CertaintyStatus = Field(
        default=CertaintyStatus.STATED,
        description="Grounding status: stated, not_stated, uncertain, conflicting, unreadable"
    )
    evidence_quote: Optional[str] = Field(
        default=None,
        description="Exact quote from the notice text supporting this fact"
    )
    source_location: Optional[str] = Field(
        default=None,
        description="Line number or section in notice where evidence was found"
    )
    requires_confirmation: bool = Field(
        default=False,
        description="True if the fact is uncertain, conflicting, unreadable, or missing critical specifics"
    )
    user_confirmed: bool = Field(
        default=False,
        description="True once the user explicitly verifies this detail"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why this detail is uncertain, conflicting, or missing"
    )

    @field_validator("value")
    @classmethod
    def validate_value_not_empty(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            return NOT_STATED_LABEL
        return v_clean


def normalize_string_list_entry(item: Any) -> Optional[str]:
    """
    Normalizes a single entry from missing_information or uncertain_or_conflicting_details
    into a meaningful, non-empty string.
    Safely handles dicts, strings, and other primitives. Never returns 'None' or empty strings.
    """
    if item is None:
        return None

    if isinstance(item, str):
        cleaned = item.strip()
        if not cleaned or cleaned.lower() in ("none", "null", "undefined", "n/a"):
            return None
        return cleaned

    if isinstance(item, dict):
        # Look for primary fact/description keys in order of precedence
        primary_val: Optional[str] = None
        for key in ("fact", "value", "description", "detail", "item", "text", "name", "field"):
            v = item.get(key)
            if v is not None and isinstance(v, str) and v.strip():
                clean_v = v.strip()
                if clean_v.lower() not in ("none", "null", "undefined", "n/a"):
                    primary_val = clean_v
                    break

        # Look for supplementary context (e.g. explanation, reason, notes)
        context_val: Optional[str] = None
        for ctx_key in ("explanation", "reason", "notes", "uncertainty", "comment"):
            cv = item.get(ctx_key)
            if cv is not None and isinstance(cv, str) and cv.strip():
                clean_cv = cv.strip()
                if clean_cv.lower() not in ("none", "null", "undefined", "n/a") and clean_cv != primary_val:
                    context_val = clean_cv
                    break

        if primary_val:
            if context_val:
                return f"{primary_val} ({context_val})"
            return primary_val

        # If no primary key was found, check all string values in the dict
        val_candidates: List[str] = []
        for k, v in item.items():
            if k == "evidence_quote" and (v is None or not str(v).strip()):
                continue
            if v is not None and isinstance(v, str):
                c = v.strip()
                if c and c.lower() not in ("none", "null", "undefined", "n/a"):
                    val_candidates.append(c)

        if val_candidates:
            return " — ".join(val_candidates)

        return None

    cleaned_str = str(item).strip()
    if not cleaned_str or cleaned_str.lower() in ("none", "null", "undefined", "n/a"):
        return None
    return cleaned_str


def normalize_string_list(items: Any) -> List[str]:
    """
    Converts arbitrary model output (list of strings, list of dicts, single item, etc.)
    into a clean, deduplicated list of non-empty strings.
    """
    if items is None:
        return []

    if isinstance(items, (str, dict)):
        items = [items]

    if not isinstance(items, (list, tuple, set)):
        return []

    normalized: List[str] = []
    for it in items:
        entry = normalize_string_list_entry(it)
        if entry and entry not in normalized:
            normalized.append(entry)

    return normalized


class StructuredNotice(BaseModel):
    """Complete structured breakdown of a processed notice."""
    purpose: ExtractedFact
    eligibility: ExtractedFact
    deadline: ExtractedFact
    fee_or_cost: ExtractedFact
    required_documents: ExtractedFact
    contact_details: ExtractedFact
    required_actions: ExtractedFact
    important_conditions: ExtractedFact
    missing_information: List[str] = Field(
        default_factory=list,
        description="List of critical aspects completely absent from the notice"
    )
    uncertain_or_conflicting_details: List[str] = Field(
        default_factory=list,
        description="List of aspects that are ambiguous, contradictory, or need verification"
    )
    raw_notice_text: str = Field(
        default="",
        description="Original notice text used as ground truth for evidence checks"
    )

    @field_validator("missing_information", "uncertain_or_conflicting_details", mode="before")
    @classmethod
    def validate_and_normalize_string_list(cls, v: Any) -> List[str]:
        return normalize_string_list(v)


class PlainLanguageSummary(BaseModel):
    """Concise, plain-language summary answering the 7 core user questions."""
    about: str = Field(description="What is this notice about?")
    eligible: str = Field(description="Who is eligible?")
    actions: str = Field(description="What must the reader do?")
    documents: str = Field(description="What documents are needed?")
    deadline: str = Field(description="What is the deadline?")
    help_contact: str = Field(description="Where can the reader get help?")
    missing: str = Field(description="What important information is missing?")


class ChecklistItem(BaseModel):
    """A single sequential action required by the notice."""
    step_number: int
    action: str
    category: str = Field(
        default="application",
        description="Category: eligibility, documents, application, submission, clarification"
    )
    is_mandatory: bool = True
    requires_confirmation: bool = False
    is_completed: bool = False
    grounded_quote: Optional[str] = None
    notes: Optional[str] = None


class ActionChecklist(BaseModel):
    """Ordered action checklist derived strictly from grounded facts."""
    items: List[ChecklistItem] = Field(default_factory=list)

    def to_ics_bytes(self, title: str = "Notice Action Plan") -> bytes:
        """Generates an iCalendar (.ics) byte payload for calendar integration."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Notice2Action AI//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]
        for it in self.items:
            mand = "Mandatory" if it.is_mandatory else "Advisory"
            lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:Step {it.step_number}: {it.action}",
                f"DESCRIPTION:[{mand}] Category: {it.category}",
                "STATUS:CONFIRMED",
                "END:VEVENT",
            ])
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines).encode("utf-8")


class FollowUpAnswer(BaseModel):
    """Notice-grounded answer to a user's follow-up question."""
    question: str
    answer: str
    is_supported: bool = True
    evidence_quote: Optional[str] = None
    unsupported_message: Optional[str] = None
