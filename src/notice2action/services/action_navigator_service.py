"""
Personalized Action Navigator Service.
Transforms official notices into evidence-backed, dependency-aware,
personalized action plans tailored to an applicant's profile and eligibility.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from notice2action.schemas import (
    ActionCategory,
    ActionItemStatus,
    ActionItem,
    PersonalizedActionPlan,
    ApplicantProfile,
    EligibilityAssessment,
    RevisionLedger,
    TrustEvidence,
    EvidenceVerificationStatus,
)
from notice2action.services.trust_engine import TrustEngine


class ActionNavigatorService:
    """Builds personalized action plans with dependency tracking and evidence links."""

    @classmethod
    def compute_deadline_status(cls, deadline_str: Optional[str], is_superseded: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        Calculates countdown and deadline status:
        Statuses:
        - 'Superseded by a verified newer notice'
        - 'Due today'
        - 'Due soon' (1-3 days)
        - 'Upcoming' (>3 days)
        - 'Past deadline' (<0 days)
        - 'Date unclear'
        """
        if is_superseded:
            return "Superseded by a verified newer notice", "Superseded by corrigendum"
        if not deadline_str or not deadline_str.strip():
            return "Date unclear", None

        cleaned = deadline_str.strip()
        if any(w in cleaned.lower() for w in ["unclear", "not stated", "tbd", "to be announced", "within"]):
            return "Date unclear", None

        match = re.search(
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            cleaned,
        )
        if not match:
            return "Date unclear", None

        date_str = match.group(1).replace(",", "")
        target_date = None
        for fmt in ["%B %d %Y", "%d %B %Y", "%d %b %Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]:
            try:
                target_date = datetime.strptime(date_str, fmt).date()
                break
            except Exception:
                pass

        if not target_date:
            return "Date unclear", None

        today = datetime.now().date()
        diff = (target_date - today).days

        if diff < 0:
            return "Past deadline", f"Expired {abs(diff)} day{'s' if abs(diff) > 1 else ''} ago"
        elif diff == 0:
            return "Due today", "Due today by 11:59 PM"
        elif diff <= 3:
            return "Due soon", f"{diff} day{'s' if diff > 1 else ''} remaining"
        else:
            return "Upcoming", f"{diff} days remaining"

    @classmethod
    def generate_plan(
        cls,
        notice_text: str,
        session_id: Optional[str] = None,
        profile: Optional[ApplicantProfile] = None,
        eligibility: Optional[EligibilityAssessment] = None,
        revision_ledger: Optional[RevisionLedger] = None,
    ) -> PersonalizedActionPlan:
        """
        Synthesizes a structured, dependency-aware action roadmap based on notice facts,
        user profile, and eligibility assessment.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        items: List[ActionItem] = []

        # 1. Extract deadline and evidence
        deadline_str = None
        raw_deadline = None
        deadline_evidence = None
        superseded_deadline = None
        is_superseded = False

        deadline_match = re.search(
            r"(?:deadline|last date|closing date|cutoff|submit by)[^\n\.;]*?(?:[:=]|\b(?:is|shall be)\b)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|[^\n\.;]+)|(?:on or before|submit by|before|deadline|last date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{4})",
            notice_text,
            re.IGNORECASE,
        )
        if deadline_match:
            raw_deadline = (deadline_match.group(1) or deadline_match.group(2) or "").strip()
            deadline_str = raw_deadline
            deadline_evidence = deadline_match.group(0).strip()

        # Check if revision ledger updated the deadline
        if revision_ledger:
            for entry in revision_ledger.entries:
                if "deadline" in entry.field_name.lower():
                    superseded_deadline = raw_deadline or entry.old_value
                    deadline_str = f"{entry.new_value} (Updated via Corrigendum)"
                    deadline_evidence = entry.new_evidence_quote
                    is_superseded = True
                    break

        dl_status, remaining_time = cls.compute_deadline_status(deadline_str, is_superseded=is_superseded)

        # 2. Extract fee amount
        fee_str = None
        fee_match = re.search(r"(?:fee|charges|amount)[:\s]+(?:Rs\.?|INR)?\s*(\d+)", notice_text, re.IGNORECASE)
        if fee_match:
            fee_str = f"Rs. {fee_match.group(1)}"

        # Check if revision ledger updated the fee
        if revision_ledger:
            for entry in revision_ledger.entries:
                if "fee" in entry.field_name.lower():
                    fee_str = f"{entry.new_value} (Updated via Corrigendum)"
                    break

        # Check candidate category fee exemption
        if profile and profile.category in ["SC", "ST", "PwD"]:
            fee_str = f"Exempted / Concessional for {profile.category} category"

        # 3. Extract official portal link (only if valid in text)
        portal_url = None
        url_match = re.search(r"https?://[a-zA-Z0-9\.\-_/]+", notice_text)
        if url_match:
            portal_url = url_match.group(0)

        # -----------------------------------------------------------------
        # STEP 1: ELIGIBILITY VERIFICATION (Prerequisite)
        # -----------------------------------------------------------------
        is_ineligible = False
        ineligible_reasons = []

        if eligibility:
            if eligibility.overall_status == "NOT_ELIGIBLE":
                is_ineligible = True
                for r in eligibility.results:
                    if r.status.value == "FAIL":
                        ineligible_reasons.append(r.explanation)

        eligibility_status = ActionItemStatus.COMPLETED if (eligibility and eligibility.overall_status == "ELIGIBLE") else (
            ActionItemStatus.BLOCKED if is_ineligible else ActionItemStatus.PENDING
        )

        step1_ev = TrustEngine.verify_excerpt(
            notice_text,
            deadline_evidence or "Eligibility criteria outlined in notice",
            claim_text="Verify basic applicant eligibility criteria",
        ).evidence

        step1 = ActionItem(
            id="ACT-01",
            title="Verify Criteria & Eligibility Requirements",
            explanation=(
                "Confirm that your age, academic degrees, and qualifying marks strictly meet the official criteria."
                if not is_ineligible
                else f"Eligibility Check Failed: {'; '.join(ineligible_reasons)}"
            ),
            category=ActionCategory.ELIGIBILITY_CHECK,
            status=eligibility_status,
            evidence=step1_ev,
            dependencies=[],
            blocked_by=ineligible_reasons if is_ineligible else [],
        )
        items.append(step1)

        # -----------------------------------------------------------------
        # STEP 2: CORRIGENDUM REVIEW (If revision ledger exists)
        # -----------------------------------------------------------------
        if revision_ledger and revision_ledger.entries:
            corrigendum_ev = TrustEngine.verify_excerpt(
                notice_text,
                revision_ledger.relationship.evidence_quote or "Corrigendum modifies previous notice clauses",
                claim_text="Review Corrigendum Amendments",
            ).evidence

            items.append(
                ActionItem(
                    id="ACT-02",
                    title="Review Corrigendum & Amendment Additions",
                    explanation=f"Review {len(revision_ledger.entries)} revised clause(s) affecting deadlines, fees, or requirements.",
                    category=ActionCategory.CORRIGENDUM_REVIEW,
                    status=ActionItemStatus.COMPLETED,
                    evidence=corrigendum_ev,
                    dependencies=["ACT-01"],
                )
            )

        # -----------------------------------------------------------------
        # STEP 3: DOCUMENT PREPARATION
        # -----------------------------------------------------------------
        doc_dependencies = ["ACT-01"]
        doc_blocked = ["Prerequisite step ACT-01 (Eligibility) is blocked"] if is_ineligible else []
        doc_status = ActionItemStatus.BLOCKED if is_ineligible else ActionItemStatus.PENDING

        doc_explanation = "Gather attested copies of marksheet, degree certificate, and identity proof."
        if profile and profile.category in ["OBC", "SC", "ST", "EWS"]:
            doc_explanation += f" Ensure your valid {profile.category} Community Certificate (NCL where applicable) is ready."

        items.append(
            ActionItem(
                id="ACT-03",
                title="Prepare Mandatory Supporting Documents",
                explanation=doc_explanation,
                category=ActionCategory.DOCUMENT_PREPARATION,
                status=doc_status,
                dependencies=doc_dependencies,
                blocked_by=doc_blocked,
            )
        )

        # -----------------------------------------------------------------
        # STEP 4: FEE PAYMENT (If applicable)
        # -----------------------------------------------------------------
        if fee_str:
            items.append(
                ActionItem(
                    id="ACT-04",
                    title="Pay Prescribed Application Fee",
                    explanation=f"Submit fee payment of {fee_str} via designated banking or online portal channel.",
                    category=ActionCategory.FEE_PAYMENT,
                    status=ActionItemStatus.BLOCKED if is_ineligible else ActionItemStatus.PENDING,
                    fee_amount=fee_str,
                    dependencies=["ACT-01", "ACT-03"],
                    blocked_by=doc_blocked,
                )
            )

        # -----------------------------------------------------------------
        # STEP 5: APPLICATION SUBMISSION (Core action)
        # -----------------------------------------------------------------
        sub_dependencies = ["ACT-01", "ACT-03"]
        if fee_str:
            sub_dependencies.append("ACT-04")

        items.append(
            ActionItem(
                id="ACT-05",
                title="Submit Formal Application & Upload Credentials",
                explanation=f"Complete final online submission on or before the statutory deadline: {deadline_str or 'Stated cutoff'}.",
                category=ActionCategory.APPLICATION_SUBMISSION,
                status=ActionItemStatus.BLOCKED if is_ineligible else ActionItemStatus.PENDING,
                deadline=deadline_str,
                deadline_evidence=deadline_evidence,
                deadline_status=dl_status,
                remaining_time=remaining_time,
                superseded_deadline=superseded_deadline,
                official_portal_url=portal_url,
                url_verified=bool(portal_url),
                dependencies=sub_dependencies,
                blocked_by=doc_blocked,
            )
        )

        # -----------------------------------------------------------------
        # STEP 6: POST-SUBMISSION CONFIRMATION
        # -----------------------------------------------------------------
        items.append(
            ActionItem(
                id="ACT-06",
                title="Download Acknowledgment & Retain Confirmation Slip",
                explanation="Securely save your submitted application PDF, transaction reference, and registration number for verification.",
                category=ActionCategory.POST_SUBMISSION,
                status=ActionItemStatus.BLOCKED if is_ineligible else ActionItemStatus.PENDING,
                dependencies=["ACT-05"],
                blocked_by=doc_blocked,
            )
        )

        # Calculate progress
        completed_count = sum(1 for item in items if item.status == ActionItemStatus.COMPLETED)
        total_count = len(items)
        progress = round((completed_count / total_count) * 100, 1) if total_count > 0 else 0.0

        # Find next recommended action
        next_action_id = None
        for item in items:
            if item.status == ActionItemStatus.PENDING:
                next_action_id = item.id
                break

        return PersonalizedActionPlan(
            plan_id=plan_id,
            session_id=session_id,
            notice_title="Notice-to-Action Implementation Plan",
            overall_progress_percentage=progress,
            completed_count=completed_count,
            total_count=total_count,
            items=items,
            next_recommended_action_id=next_action_id,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    @classmethod
    def update_item_status(
        cls,
        plan: PersonalizedActionPlan,
        action_id: str,
        new_status: ActionItemStatus,
        user_notes: Optional[str] = None,
    ) -> PersonalizedActionPlan:
        """
        Updates the status of a specific item, adjusting dependent items and progress score.
        """
        target_item = None
        for item in plan.items:
            if item.id == action_id:
                target_item = item
                item.status = new_status
                if new_status == ActionItemStatus.COMPLETED:
                    item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    item.completed_at = None
                if user_notes is not None:
                    item.user_notes = user_notes
                break

        # Recompute dependencies and unblock items if prerequisites completed
        completed_ids = {i.id for i in plan.items if i.status == ActionItemStatus.COMPLETED}

        for item in plan.items:
            if item.status == ActionItemStatus.BLOCKED:
                # Check if all dependencies are satisfied
                if all(dep in completed_ids for dep in item.dependencies):
                    # Unblock if no fundamental ineligibility
                    if not any("ineligibility" in b.lower() for b in item.blocked_by):
                        item.status = ActionItemStatus.PENDING
                        item.blocked_by = []

        completed_count = sum(1 for item in plan.items if item.status == ActionItemStatus.COMPLETED)
        total_count = len(plan.items)
        plan.completed_count = completed_count
        plan.overall_progress_percentage = round((completed_count / total_count) * 100, 1) if total_count > 0 else 0.0

        # Find next recommended action
        plan.next_recommended_action_id = None
        for item in plan.items:
            if item.status == ActionItemStatus.PENDING:
                plan.next_recommended_action_id = item.id
                break

        plan.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return plan
