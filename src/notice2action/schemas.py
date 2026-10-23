"""
Strict Data Schemas for SuchnaSetu AI.
Enforces evidence grounding, uncertainty states, explicit missing-field tracking,
and the Six Core Notice Fields (issuing authority, reference number, notice date,
recipient, main subject, required action and deadline).
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


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
    confirmed_value: Optional[str] = Field(
        default=None,
        description="User-confirmed or corrected value, preserving original extracted value"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why this detail is uncertain, conflicting, or missing"
    )
    uncertainty_type: Optional[str] = Field(
        default=None,
        description="Category of uncertainty: 'ocr_quality', 'document_ambiguity', 'missing_in_text', 'conflict'"
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


class SixCoreFields(BaseModel):
    """The six structured fields specifically extracted from a legal/administrative notice."""
    issuing_authority: ExtractedFact = Field(
        description="1. Issuing authority or department (e.g. Department of Higher Education)"
    )
    notice_reference_number: ExtractedFact = Field(
        description="2. Notice or reference number, if available"
    )
    notice_date: ExtractedFact = Field(
        description="3. Notice date"
    )
    recipient: ExtractedFact = Field(
        description="4. Recipient or concerned party, if available"
    )
    main_subject: ExtractedFact = Field(
        description="5. Main issue, allegation, or subject"
    )
    required_action_and_deadline: ExtractedFact = Field(
        description="6. Required action and deadline, if specified"
    )


class StructuredNotice(BaseModel):
    """Complete structured breakdown of a processed notice."""
    # Six Core Fields (Friend Suggestion E)
    issuing_authority: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="issuing_authority",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )
    notice_reference_number: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="notice_reference_number",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )
    notice_date: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="notice_date",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )
    recipient: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="recipient",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )
    main_subject: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="main_subject",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )
    required_action_and_deadline: ExtractedFact = Field(
        default_factory=lambda: ExtractedFact(
            field_name="required_action_and_deadline",
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
        )
    )

    # Core procedural fields (retaining full backward compatibility with all UI components and tests)
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

    @model_validator(mode="after")
    def sync_core_fields(self) -> StructuredNotice:
        """Synchronizes main_subject and required_action_and_deadline if unpopulated."""
        if self.main_subject.value == NOT_STATED_LABEL and self.purpose.value != NOT_STATED_LABEL:
            self.main_subject = ExtractedFact(
                field_name="main_subject",
                value=self.purpose.value,
                status=self.purpose.status,
                evidence_quote=self.purpose.evidence_quote,
                requires_confirmation=self.purpose.requires_confirmation,
            )
        if self.required_action_and_deadline.value == NOT_STATED_LABEL:
            parts = []
            if self.required_actions.value != NOT_STATED_LABEL:
                parts.append(self.required_actions.value)
            if self.deadline.value != NOT_STATED_LABEL:
                parts.append(f"Deadline: {self.deadline.value}")
            if parts:
                self.required_action_and_deadline = ExtractedFact(
                    field_name="required_action_and_deadline",
                    value="; ".join(parts),
                    status=self.deadline.status if self.deadline.status != CertaintyStatus.NOT_STATED else self.required_actions.status,
                    evidence_quote=self.deadline.evidence_quote or self.required_actions.evidence_quote,
                    requires_confirmation=self.deadline.requires_confirmation or self.required_actions.requires_confirmation,
                )
        return self

    def to_six_core_fields(self) -> SixCoreFields:
        """Returns the Six Core Fields model."""
        return SixCoreFields(
            issuing_authority=self.issuing_authority,
            notice_reference_number=self.notice_reference_number,
            notice_date=self.notice_date,
            recipient=self.recipient,
            main_subject=self.main_subject,
            required_action_and_deadline=self.required_action_and_deadline,
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

    def to_ics_bytes(self, title: str = "Notice Action Plan") -> bytes:
        """Generates an iCalendar (.ics) byte payload for calendar integration."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SuchnaSetu AI//EN",
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


# =========================================================
# Multi-Notice Revision Ledger Schemas
# =========================================================

class RelationshipType(str, Enum):
    AMENDMENT = "AMENDMENT"
    EXTENSION = "EXTENSION"
    CANCELLATION = "CANCELLATION"
    REPLACEMENT = "REPLACEMENT"
    RELATED = "RELATED"
    UNRESOLVED = "UNRESOLVED"


class ChangeCategory(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"
    UNCERTAIN = "UNCERTAIN"


class NoticeRelationship(BaseModel):
    source_notice_id: str = Field(..., description="ID or title of the original/base notice")
    target_notice_id: str = Field(..., description="ID or title of the revised/amendment notice")
    relationship_type: RelationshipType = Field(default=RelationshipType.RELATED)
    confidence: str = Field(default="HIGH", description="'HIGH', 'MEDIUM', 'LOW'")
    is_explicit: bool = Field(default=False, description="True if source explicitly references target notice number")
    evidence_quote: str = Field(default="", description="Verbatim citation supporting the relationship")
    source_reference: Optional[str] = Field(default=None, description="Explicit reference circular number if found")
    explanation: str = Field(default="", description="Human-readable explanation of relationship")


class RevisionEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    field_name: str = Field(..., description="Machine-readable field key")
    display_name: str = Field(..., description="Human-readable field name")
    old_value: str = Field(..., description="Value in original notice")
    new_value: str = Field(..., description="Value in revised notice")
    change_category: ChangeCategory = Field(default=ChangeCategory.UNCHANGED)
    category: Optional[str] = None
    old_evidence_quote: Optional[str] = None
    new_evidence_quote: Optional[str] = None
    old_page: Optional[int] = None
    new_page: Optional[int] = None
    requires_review: bool = False
    explanation: str = ""

    @model_validator(mode="after")
    def sync_category(self) -> "RevisionEntry":
        if not self.category and self.change_category:
            val = self.change_category.value if hasattr(self.change_category, "value") else str(self.change_category)
            if val == "MODIFIED":
                if self.field_name == "deadline":
                    self.category = "DEADLINE_EXTENSION"
                elif self.field_name == "fee_or_cost":
                    self.category = "FEE_CHANGE"
                elif self.field_name == "eligibility":
                    self.category = "ELIGIBILITY_CHANGE"
                else:
                    self.category = "GENERAL_MODIFICATION"
            else:
                self.category = str(val)
        return self


class RevisionLedger(BaseModel):
    source_notice_id: str
    target_notice_id: str
    source_title: str = "Original Notice"
    target_title: str = "Revised Notice / Corrigendum"
    relationship: NoticeRelationship
    entries: List[RevisionEntry] = Field(default_factory=list)
    summary_of_changes: str = ""
    created_at: str = ""


class CompareNoticesRequest(BaseModel):
    source_session_id: Optional[str] = None
    target_session_id: Optional[str] = None
    source_text: Optional[str] = None
    target_text: Optional[str] = None


# =========================================================
# Explainable Applicant Eligibility Engine Schemas
# =========================================================

class CriterionType(str, Enum):
    AGE = "AGE"
    QUALIFICATION = "QUALIFICATION"
    PERCENTAGE = "PERCENTAGE"
    CATEGORY = "CATEGORY"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class EligibilityCriterion(BaseModel):
    id: str
    criterion_type: CriterionType
    description: str
    operator: str = ">="  # ">=", "<=", "==", "IN", "CONTAINS"
    threshold_value: str
    cutoff_date: Optional[str] = None
    category_relaxations: Dict[str, str] = Field(default_factory=dict)
    evidence_quote: str = ""
    page_number: Optional[int] = None


class ApplicantProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    date_of_birth: Optional[str] = None  # YYYY-MM-DD
    age_years: Optional[float] = None
    degree: Optional[str] = None
    academic_degree: Optional[str] = None
    course: Optional[str] = None  # e.g., B.Tech, MBA, B.Sc
    academic_year: Optional[Union[str, int]] = None  # e.g., 2nd Year, Final Year
    department: Optional[str] = None
    marks_percentage: Optional[float] = None
    academic_percentage: Optional[float] = None
    income_annual: Optional[float] = None
    annual_family_income: Optional[float] = None
    enrollment_status: Optional[str] = None
    category: Optional[str] = "General"  # General, OBC, SC, ST, EWS, PwD
    documents_available: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def sync_aliases(self) -> "ApplicantProfile":
        if not self.degree and self.academic_degree:
            self.degree = self.academic_degree
        if self.marks_percentage is None and self.academic_percentage is not None:
            self.marks_percentage = self.academic_percentage
        if self.income_annual is None and self.annual_family_income is not None:
            self.income_annual = self.annual_family_income
        if self.academic_year is not None:
            self.academic_year = str(self.academic_year)
        return self


class CriterionEvaluationResult(BaseModel):
    criterion_id: str
    criterion_type: CriterionType
    description: str
    status: EvaluationStatus
    applicant_value: str
    requirement_value: str
    evidence_quote: str
    page_number: Optional[int] = None
    explanation: str
    missing_info: Optional[str] = None


class EligibilityAssessment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    session_id: Optional[str] = None
    overall_status: str  # "ELIGIBLE", "NOT_ELIGIBLE", "INCONCLUSIVE"
    overall_verdict: Optional[str] = None
    results: List[CriterionEvaluationResult] = Field(default_factory=list)
    summary: str = ""
    disclaimer: str = (
        "This assessment is for informational assistance only and does not constitute "
        "an official government decision or guarantee of qualification. Always verify "
        "with official gazettes and recruiting authorities."
    )

    @model_validator(mode="after")
    def sync_verdict(self) -> "EligibilityAssessment":
        if not self.overall_verdict:
            self.overall_verdict = self.overall_status
        return self


class EvaluateEligibilityRequest(BaseModel):
    session_id: Optional[str] = None
    notice_text: Optional[str] = None
    applicant_profile: ApplicantProfile


# =========================================================
# Feature 1: Evidence-First Trust Engine Schemas
# =========================================================

class EvidenceVerificationStatus(str, Enum):
    VERIFIED_IN_SOURCE = "VERIFIED_IN_SOURCE"
    UNVERIFIED = "UNVERIFIED"
    UNCERTAIN_OCR = "UNCERTAIN_OCR"
    DERIVED_DETERMINISTIC = "DERIVED_DETERMINISTIC"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"


class TrustEvidence(BaseModel):
    evidence_id: str
    claim_id: Optional[str] = None
    claim_text: str = ""
    source_doc_id: Optional[str] = None
    source_doc_title: Optional[str] = None
    page_number: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    verbatim_excerpt: str = ""
    normalized_value: Optional[str] = None
    verification_status: EvidenceVerificationStatus = EvidenceVerificationStatus.UNVERIFIED
    confidence_rationale: str = ""
    is_inert_safe: bool = True


class VerifyEvidenceRequest(BaseModel):
    notice_text: str
    excerpt: str
    claim_text: Optional[str] = None
    source_doc_title: Optional[str] = "Active Notice"


class VerifyEvidenceResponse(BaseModel):
    is_valid: bool
    evidence: TrustEvidence
    suggested_match: Optional[str] = None


# =========================================================
# Feature 2: Personal Impact Change Tracker Schemas
# =========================================================

class ImpactType(str, Enum):
    BENEFICIAL = "BENEFICIAL"
    ADVERSE = "ADVERSE"
    NEUTRAL = "NEUTRAL"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    UNRESOLVED = "UNRESOLVED"


class PersonalImpactItem(BaseModel):
    id: str
    field_name: str
    change_category: ChangeCategory
    previous_value: str
    new_value: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    impact_type: ImpactType
    headline: str
    explanation: str
    evidence_old: Optional[str] = None
    evidence_new: Optional[str] = None
    required_user_action: Optional[str] = None


class PersonalImpactReport(BaseModel):
    overall_impact_summary: str
    impact_level: str  # "HIGH", "MODERATE", "LOW", "NEUTRAL"
    impact_items: List[PersonalImpactItem] = Field(default_factory=list)
    recalculated_eligibility: Optional[EligibilityAssessment] = None
    recommended_next_actions: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "This personal impact analysis is derived automatically by comparing notice revisions against "
        "your voluntarily provided profile. Always verify critical cutoff changes against the official issuing gazette."
    )


class EvaluatePersonalImpactRequest(BaseModel):
    revision_ledger: Optional[RevisionLedger] = None
    source_text: Optional[str] = None
    target_text: Optional[str] = None
    applicant_profile: Optional[ApplicantProfile] = None


# =========================================================
# Feature 3: Personalized Action Navigator Schemas
# =========================================================

class ActionCategory(str, Enum):
    ELIGIBILITY_CHECK = "ELIGIBILITY_CHECK"
    DOCUMENT_PREPARATION = "DOCUMENT_PREPARATION"
    FEE_PAYMENT = "FEE_PAYMENT"
    APPLICATION_SUBMISSION = "APPLICATION_SUBMISSION"
    HEARING_APPEARANCE = "HEARING_APPEARANCE"
    POST_SUBMISSION = "POST_SUBMISSION"
    CORRIGENDUM_REVIEW = "CORRIGENDUM_REVIEW"


class ActionItemStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class ActionItem(BaseModel):
    id: str
    title: str
    explanation: str
    category: ActionCategory
    status: ActionItemStatus = ActionItemStatus.PENDING
    deadline: Optional[str] = None
    deadline_evidence: Optional[str] = None
    deadline_status: Optional[str] = None  # Upcoming, Due soon, Due today, Past deadline, Date unclear, Superseded
    remaining_time: Optional[str] = None  # e.g., '3 days remaining', 'Expired 2 days ago'
    superseded_deadline: Optional[str] = None
    fee_amount: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    blocked_by: List[str] = Field(default_factory=list)
    official_portal_url: Optional[str] = None
    url_verified: bool = False
    evidence: Optional[TrustEvidence] = None
    is_user_custom: bool = False
    completed_at: Optional[str] = None
    user_notes: Optional[str] = None


class PersonalizedActionPlan(BaseModel):
    plan_id: str
    session_id: Optional[str] = None
    notice_title: str = "Administrative Notice Action Plan"
    overall_progress_percentage: float = 0.0
    completed_count: int = 0
    total_count: int = 0
    items: List[ActionItem] = Field(default_factory=list)
    next_recommended_action_id: Optional[str] = None
    last_updated: str = ""


class GenerateActionPlanRequest(BaseModel):
    session_id: Optional[str] = None
    notice_text: Optional[str] = None
    applicant_profile: Optional[ApplicantProfile] = None
    eligibility_assessment: Optional[EligibilityAssessment] = None
    revision_ledger: Optional[RevisionLedger] = None


class UpdateActionStatusRequest(BaseModel):
    plan_id: str
    action_id: str
    status: ActionItemStatus
    user_notes: Optional[str] = None


# =========================================================
# Feature 4: Cross-Notice Intelligence & Workspace Schemas
# =========================================================

class RelationshipConfidence(str, Enum):
    VERIFIED = "VERIFIED"
    STRONG_CANDIDATE = "STRONG_CANDIDATE"
    POSSIBLE = "POSSIBLE"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class NoticeMetadata(BaseModel):
    id: str
    title: str
    reference_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    notice_date: Optional[str] = None
    ingested_at: str = ""
    char_count: int = 0
    raw_text: str = ""
    fingerprint: str = ""
    document_type: str = "NOTICE"  # "ORIGINAL", "CORRIGENDUM", "ADDENDUM", "CIRCULAR", "CANCELLATION"


class CrossNoticeRelationship(BaseModel):
    id: str
    source_notice_id: str
    target_notice_id: str
    relationship_type: RelationshipType
    confidence_level: RelationshipConfidence
    evidence_quote: str = ""
    rationale: str = ""
    precedence_status: str = "INDEPENDENT"
    user_confirmed: bool = False


class TimelineEvent(BaseModel):
    id: str
    date: str
    notice_id: str
    notice_title: str
    event_type: str
    summary: str
    evidence_quote: str = ""
    is_active: bool = True


class CrossNoticeConflict(BaseModel):
    id: str
    notice_a_id: str
    notice_b_id: str
    field_name: str
    value_a: str
    value_b: str
    evidence_a: str = ""
    evidence_b: str = ""
    conflict_severity: str = "MODERATE"  # CRITICAL, MODERATE, INFORMATIONAL
    resolution_guidance: str = ""
    status: str = "UNRESOLVED"


class WorkspaceTimelineReport(BaseModel):
    workspace_id: str
    notices: List[NoticeMetadata] = Field(default_factory=list)
    relationships: List[CrossNoticeRelationship] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    conflicts: List[CrossNoticeConflict] = Field(default_factory=list)
    active_notice_id: Optional[str] = None

