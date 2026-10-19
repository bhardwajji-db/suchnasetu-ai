"""
Action Checklist Generator for Notice2Action AI.
Creates an ordered, grounded step-by-step checklist with uncertainty confirmation gates.
"""

from __future__ import annotations

from typing import List, Optional
from notice2action.schemas import (
    StructuredNotice,
    ActionChecklist,
    ChecklistItem,
    CertaintyStatus,
)


def generate_action_checklist(notice: StructuredNotice) -> ActionChecklist:
    """
    Constructs an ordered action checklist from verified structured notice facts.
    Enforces that actions depending on uncertain details require confirmation first.
    """
    items: List[ChecklistItem] = []
    step = 1

    # Step 1: Eligibility check
    if notice.eligibility.status == CertaintyStatus.STATED:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Verify Eligibility: Confirm you meet the criteria ({notice.eligibility.value}).",
                category="eligibility",
                is_mandatory=True,
                requires_confirmation=notice.eligibility.requires_confirmation,
                grounded_quote=notice.eligibility.evidence_quote,
                notes=notice.eligibility.explanation,
            )
        )
        step += 1
    elif notice.eligibility.status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Confirm Eligibility Criteria: The criteria appear ambiguous or contradictory ({notice.eligibility.value}). Verify with the official contact before proceeding.",
                category="eligibility",
                is_mandatory=True,
                requires_confirmation=True,
                grounded_quote=notice.eligibility.evidence_quote,
                notes="Uncertainty gate: must be verified prior to applying.",
            )
        )
        step += 1

    # Step 2: Document preparation
    if notice.required_documents.status == CertaintyStatus.STATED:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Gather Required Documents: Collect the required items ({notice.required_documents.value}).",
                category="documents",
                is_mandatory=True,
                requires_confirmation=notice.required_documents.requires_confirmation,
                grounded_quote=notice.required_documents.evidence_quote,
                notes=notice.required_documents.explanation,
            )
        )
        step += 1
    elif notice.required_documents.status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Clarify Document List: The notice mentions tentative documents ({notice.required_documents.value}). Confirm exact format and list.",
                category="documents",
                is_mandatory=True,
                requires_confirmation=True,
                grounded_quote=notice.required_documents.evidence_quote,
                notes="Requires verification before submission.",
            )
        )
        step += 1

    # Step 3: Application process / Actions
    if notice.required_actions.status == CertaintyStatus.STATED:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Complete Application: Follow the stated procedure ({notice.required_actions.value}).",
                category="application",
                is_mandatory=True,
                requires_confirmation=notice.required_actions.requires_confirmation,
                grounded_quote=notice.required_actions.evidence_quote,
            )
        )
        step += 1

    # Step 4: Submission & Deadline
    if notice.deadline.status == CertaintyStatus.STATED:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Submit Before Deadline: Complete submission by {notice.deadline.value}.",
                category="submission",
                is_mandatory=True,
                requires_confirmation=notice.deadline.requires_confirmation,
                grounded_quote=notice.deadline.evidence_quote,
            )
        )
        step += 1
    elif notice.deadline.status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Verify Submission Deadline: The deadline date is tentative or conflicting ({notice.deadline.value}). Confirm the exact closing date immediately.",
                category="submission",
                is_mandatory=True,
                requires_confirmation=True,
                grounded_quote=notice.deadline.evidence_quote,
                notes="Deadline uncertainty detected.",
            )
        )
        step += 1
    else:
        items.append(
            ChecklistItem(
                step_number=step,
                action="Clarify Deadline: The notice does not state a submission deadline. Contact the department to avoid missing out.",
                category="clarification",
                is_mandatory=True,
                requires_confirmation=False,
                notes="Missing critical deadline.",
            )
        )
        step += 1

    # Step 5: Fee payment (if any)
    if notice.fee_or_cost.status == CertaintyStatus.STATED:
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Pay Application / Registration Fee: {notice.fee_or_cost.value}.",
                category="application",
                is_mandatory=True,
                requires_confirmation=notice.fee_or_cost.requires_confirmation,
                grounded_quote=notice.fee_or_cost.evidence_quote,
            )
        )
        step += 1

    # Step 6: Missing information inquiries
    if notice.missing_information:
        missing_str = ", ".join(notice.missing_information)
        contact_str = (
            notice.contact_details.value
            if notice.contact_details.status == CertaintyStatus.STATED
            else "official college administration"
        )
        items.append(
            ChecklistItem(
                step_number=step,
                action=f"Contact Official Source: Inquire about missing details ({missing_str}) via {contact_str}.",
                category="clarification",
                is_mandatory=False,
                requires_confirmation=False,
                notes="Optional advisory step to resolve unstated information.",
            )
        )

    return ActionChecklist(items=items)
