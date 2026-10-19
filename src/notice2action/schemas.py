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


class FollowUpAnswer(BaseModel):
    """Notice-grounded answer to a user's follow-up question."""
    question: str
    answer: str
    is_supported: bool = True
    evidence_quote: Optional[str] = None
    unsupported_message: Optional[str] = None
