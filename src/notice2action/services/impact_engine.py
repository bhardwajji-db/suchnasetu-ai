"""
Personal Impact Change Tracker Engine.
Analyzes verified differences between notice revisions and computes
their specific, explainable personal impact on an individual applicant's
eligibility status, fees, deadlines, and required actions.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from notice2action.schemas import (
    RevisionLedger,
    RevisionEntry,
    ChangeCategory,
    ApplicantProfile,
    PersonalImpactItem,
    PersonalImpactReport,
    ImpactType,
    EligibilityAssessment,
)
from notice2action.services.revision_engine import RevisionEngine
from notice2action.services.eligibility_engine import eligibility_engine


class PersonalImpactEngine:
    """Evaluates how notice amendments impact an applicant's profile and plan."""

    @classmethod
    def _parse_date(cls, text: str) -> Optional[datetime]:
        """Attempts to parse common date formats found in Indian government circulars."""
        formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
            "%d.%m.%Y"
        ]
        text_clean = text.strip()
        for fmt in formats:
            try:
                return datetime.strptime(text_clean, fmt)
            except ValueError:
                continue
        # Try extracting pattern like YYYY-MM-DD or DD/MM/YYYY
        m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", text_clean)
        if m:
            d, month, y = m.groups()
            try:
                return datetime(int(y), int(month), int(d))
            except ValueError:
                pass
        return None

    @classmethod
    def evaluate_impact(
        cls,
        ledger: Optional[RevisionLedger] = None,
        source_text: Optional[str] = None,
        target_text: Optional[str] = None,
        profile: Optional[ApplicantProfile] = None,
    ) -> PersonalImpactReport:
        """
        Analyzes the ledger changes in relation to the applicant's profile.
        """
        # If ledger not provided, compute it from source and target texts
        if ledger is None:
            if source_text and target_text:
                ledger = RevisionEngine.compare(
                    source_text, target_text,
                    source_title="Original Notice",
                    target_title="Corrigendum / Revision",
                )
            else:
                return PersonalImpactReport(
                    overall_impact_summary="No revision ledger or document pair provided.",
                    impact_level="NEUTRAL",
                    impact_items=[],
                )

        impact_items: List[PersonalImpactItem] = []
        beneficial_count = 0
        adverse_count = 0
        action_count = 0

        # Run fresh eligibility evaluation on revised target notice if target_text exists
        recalculated_eligibility: Optional[EligibilityAssessment] = None
        if profile and target_text:
            target_notice = RevisionEngine._heuristic_extract_notice(target_text)
            criteria = eligibility_engine.extract_criteria(target_notice)
            recalculated_eligibility = eligibility_engine.evaluate_profile(criteria, profile)

        # Inspect each revision entry
        for entry in ledger.entries:
            if entry.change_category == ChangeCategory.UNCHANGED:
                continue

            field_lower = entry.field_name.lower()

            # 1. DEADLINE MODIFICATIONS
            if "deadline" in field_lower:
                old_dt = cls._parse_date(entry.old_value)
                new_dt = cls._parse_date(entry.new_value)

                days_diff = None
                if old_dt and new_dt:
                    days_diff = (new_dt - old_dt).days

                if days_diff is not None and days_diff > 0:
                    impact_type = ImpactType.BENEFICIAL
                    beneficial_count += 1
                    headline = f"Application Deadline Extended by {days_diff} Days"
                    explanation = (
                        f"The submission cutoff has been pushed back from {entry.old_value} to {entry.new_value}. "
                        f"You have {days_diff} additional days to submit your application and documents."
                    )
                    action = f"Update your personal schedule: final deadline is now {entry.new_value}."
                elif days_diff is not None and days_diff < 0:
                    impact_type = ImpactType.ADVERSE
                    adverse_count += 1
                    headline = f"Deadline Moved Earlier by {abs(days_diff)} Days"
                    explanation = (
                        f"Warning: The submission cutoff has been moved earlier from {entry.old_value} to {entry.new_value}."
                    )
                    action = f"Expedite your application before the expedited cutoff of {entry.new_value}."
                else:
                    impact_type = ImpactType.ACTION_REQUIRED
                    action_count += 1
                    headline = "Application Deadline Modified"
                    explanation = f"The deadline was updated from '{entry.old_value}' to '{entry.new_value}'."
                    action = f"Confirm submission cutoff date ({entry.new_value})."

                impact_items.append(
                    PersonalImpactItem(
                        id=str(uuid.uuid4())[:8],
                        field_name=entry.field_name,
                        change_category=entry.change_category,
                        previous_value=entry.old_value,
                        new_value=entry.new_value,
                        impact_type=impact_type,
                        headline=headline,
                        explanation=explanation,
                        evidence_old=entry.old_evidence_quote,
                        evidence_new=entry.new_evidence_quote,
                        required_user_action=action,
                    )
                )

            # 2. FEE MODIFICATIONS
            elif "fee" in field_lower:
                # Extract numeric amounts
                old_amt_match = re.search(r"(\d+)", entry.old_value.replace(",", ""))
                new_amt_match = re.search(r"(\d+)", entry.new_value.replace(",", ""))

                if old_amt_match and new_amt_match:
                    old_amt = int(old_amt_match.group(1))
                    new_amt = int(new_amt_match.group(1))
                    diff = old_amt - new_amt

                    if diff > 0:
                        impact_type = ImpactType.BENEFICIAL
                        beneficial_count += 1
                        headline = f"Application Fee Reduced by Rs. {diff}"
                        explanation = (
                            f"The payable application fee has been reduced from Rs. {old_amt} to Rs. {new_amt}."
                        )
                        action = f"Pay revised fee amount of Rs. {new_amt}."
                    elif diff < 0:
                        impact_type = ImpactType.ADVERSE
                        adverse_count += 1
                        headline = f"Application Fee Increased by Rs. {abs(diff)}"
                        explanation = (
                            f"The payable fee was revised upwards from Rs. {old_amt} to Rs. {new_amt}."
                        )
                        action = f"Budget for revised fee amount of Rs. {new_amt}."
                    else:
                        impact_type = ImpactType.NEUTRAL
                        headline = "Fee Conditions Clarified"
                        explanation = f"Fee structure updated from '{entry.old_value}' to '{entry.new_value}'."
                        action = "Verify payment gateway instructions."
                else:
                    impact_type = ImpactType.NEUTRAL
                    headline = "Fee Conditions Updated"
                    explanation = f"Fee structure updated from '{entry.old_value}' to '{entry.new_value}'."
                    action = "Verify payment gateway instructions."

                impact_items.append(
                    PersonalImpactItem(
                        id=str(uuid.uuid4())[:8],
                        field_name=entry.field_name,
                        change_category=entry.change_category,
                        previous_value=entry.old_value,
                        new_value=entry.new_value,
                        impact_type=impact_type,
                        headline=headline,
                        explanation=explanation,
                        evidence_old=entry.old_evidence_quote,
                        evidence_new=entry.new_evidence_quote,
                        required_user_action=action,
                    )
                )

            # 3. ELIGIBILITY & QUALIFICATION MODIFICATIONS
            elif "qualification" in field_lower or "marks" in field_lower or "age" in field_lower or "eligibility" in field_lower:
                old_m = re.search(r"(\d{1,2}(?:\.\d+)?)%", entry.old_value)
                new_m = re.search(r"(\d{1,2}(?:\.\d+)?)%", entry.new_value)

                prev_status = None
                new_status = None
                impact_type = ImpactType.ACTION_REQUIRED
                headline = "Eligibility Requirement Modified"
                explanation = f"Criterion changed from '{entry.old_value}' to '{entry.new_value}'."
                action = "Review your qualifications against the updated notice requirements."

                if old_m and new_m and profile and profile.marks_percentage is not None:
                    old_cutoff = float(old_m.group(1))
                    new_cutoff = float(new_m.group(1))
                    usr_marks = profile.marks_percentage

                    prev_status = "PASS" if usr_marks >= old_cutoff else "FAIL"
                    new_status = "PASS" if usr_marks >= new_cutoff else "FAIL"

                    if prev_status == "FAIL" and new_status == "PASS":
                        impact_type = ImpactType.BENEFICIAL
                        beneficial_count += 2
                        headline = f"You Are Now Eligible: Marks Cutoff Lowered from {old_cutoff}% to {new_cutoff}%"
                        explanation = (
                            f"The original notice required {old_cutoff}%, which your aggregate score ({usr_marks}%) "
                            f"did not meet. The corrigendum lowered the minimum requirement to {new_cutoff}%, "
                            f"making you fully eligible to apply."
                        )
                        action = "Proceed with application submission as your marks now satisfy the revised cutoff."
                    elif prev_status == "PASS" and new_status == "FAIL":
                        impact_type = ImpactType.ADVERSE
                        adverse_count += 2
                        headline = f"Eligibility Status Affected: Marks Cutoff Raised to {new_cutoff}%"
                        explanation = (
                            f"The required percentage was increased from {old_cutoff}% to {new_cutoff}%. "
                            f"Your score ({usr_marks}%) falls below the revised cutoff."
                        )
                        action = "Check if category relaxations or alternative qualifications apply to you."
                    else:
                        impact_type = ImpactType.NEUTRAL
                        headline = f"Marks Cutoff Revised to {new_cutoff}%"
                        explanation = f"Cutoff revised from {old_cutoff}% to {new_cutoff}%. Your status remains {new_status}."
                        action = "Keep copy of academic marksheet ready for verification."
                elif "age" in field_lower:
                    impact_type = ImpactType.ACTION_REQUIRED
                    headline = "Age Limit or Cutoff Date Revised"
                    explanation = f"Age conditions updated from '{entry.old_value}' to '{entry.new_value}'."
                    action = "Verify your age as of the revised cutoff date."

                impact_items.append(
                    PersonalImpactItem(
                        id=str(uuid.uuid4())[:8],
                        field_name=entry.field_name,
                        change_category=entry.change_category,
                        previous_value=entry.old_value,
                        new_value=entry.new_value,
                        previous_status=prev_status,
                        new_status=new_status,
                        impact_type=impact_type,
                        headline=headline,
                        explanation=explanation,
                        evidence_old=entry.old_evidence_quote,
                        evidence_new=entry.new_evidence_quote,
                        required_user_action=action,
                    )
                )

            # 4. REQUIRED DOCUMENTS / PROCEDURES
            elif "document" in field_lower or "certificate" in field_lower:
                impact_items.append(
                    PersonalImpactItem(
                        id=str(uuid.uuid4())[:8],
                        field_name=entry.field_name,
                        change_category=entry.change_category,
                        previous_value=entry.old_value,
                        new_value=entry.new_value,
                        impact_type=ImpactType.ACTION_REQUIRED,
                        headline="Mandatory Document Requirement Revised",
                        explanation=(
                            f"Required documents have been updated. Previous requirement: '{entry.old_value}'. "
                            f"New requirement: '{entry.new_value}'."
                        ),
                        evidence_old=entry.old_evidence_quote,
                        evidence_new=entry.new_evidence_quote,
                        required_user_action=f"Ensure you obtain and upload: {entry.new_value}",
                    )
                )
                action_count += 1

        # Determine overall summary & impact level
        if beneficial_count > adverse_count and beneficial_count > 0:
            impact_level = "HIGH" if beneficial_count >= 2 else "MODERATE"
            overall_summary = (
                f"Positive Impact: The corrigendum introduces {beneficial_count} beneficial revision(s) "
                f"for you (e.g. extended deadlines, lowered fees, or relaxed eligibility criteria)."
            )
        elif adverse_count > beneficial_count:
            impact_level = "HIGH"
            overall_summary = (
                f"Attention Required: The corrigendum introduces {adverse_count} restrictive change(s) "
                f"that require immediate review of your application status."
            )
        elif action_count > 0:
            impact_level = "MODERATE"
            overall_summary = (
                f"Action Required: {action_count} updated procedural or document requirement(s) "
                "were detected in the revision."
            )
        else:
            impact_level = "NEUTRAL"
            overall_summary = "Minor or procedural changes detected with neutral personal impact."

        recommended_actions = [item.required_user_action for item in impact_items if item.required_user_action]

        return PersonalImpactReport(
            overall_impact_summary=overall_summary,
            impact_level=impact_level,
            impact_items=impact_items,
            recalculated_eligibility=recalculated_eligibility,
            recommended_next_actions=recommended_actions,
        )
