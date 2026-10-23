"""
Tests for Personalized Action Navigator Service.
Verifies roadmap synthesis, prerequisite dependency chains,
ineligibility blocking, and dynamic checklist updates.
"""

import pytest
from fastapi.testclient import TestClient
from notice2action.api.server import app
from notice2action.schemas import (
    ApplicantProfile,
    EligibilityAssessment,
    CriterionEvaluationResult,
    CriterionType,
    EvaluationStatus,
    ActionItemStatus,
    RevisionLedger,
    RevisionEntry,
    NoticeRelationship,
    RelationshipType,
    ChangeCategory,
)
from notice2action.services.action_navigator_service import ActionNavigatorService

client = TestClient(app)

SAMPLE_NOTICE = """CENTRAL SCHOLARSHIP NOTIFICATION 2026
Department of Higher Education
Advt. No. CMS/2026/04

Last date for online submission: October 15, 2026.
Fee: Rs. 500.
Official portal: https://scholarships.gov.in/apply
Mandatory Qualification: Master's Degree with minimum 60% aggregate marks.
"""


def test_action_navigator_plan_generation_eligible_candidate():
    profile = ApplicantProfile(category="OBC", degree="Master of Science", marks_percentage=65.0)
    eligibility = EligibilityAssessment(
        overall_status="ELIGIBLE",
        results=[
            CriterionEvaluationResult(
                criterion_id="c1",
                criterion_type=CriterionType.PERCENTAGE,
                description="Marks >= 60%",
                status=EvaluationStatus.PASS,
                applicant_value="65.0%",
                requirement_value="60.0%",
                evidence_quote="minimum 60% aggregate marks",
                explanation="Applicant marks satisfy requirement.",
            )
        ],
    )

    plan = ActionNavigatorService.generate_plan(
        notice_text=SAMPLE_NOTICE,
        profile=profile,
        eligibility=eligibility,
    )

    assert plan.total_count >= 5
    assert plan.completed_count >= 1  # Step 1 (Eligibility) is completed
    assert plan.overall_progress_percentage > 0.0

    # Verify OBC community certificate is advised in doc prep
    doc_step = next(it for it in plan.items if it.id == "ACT-03")
    assert "OBC" in doc_step.explanation

    # Verify official portal link is present and verified
    sub_step = next(it for it in plan.items if it.id == "ACT-05")
    assert sub_step.official_portal_url == "https://scholarships.gov.in/apply"
    assert sub_step.url_verified is True


def test_action_navigator_plan_generation_ineligible_candidate_blocks_actions():
    profile = ApplicantProfile(marks_percentage=55.0)
    eligibility = EligibilityAssessment(
        overall_status="NOT_ELIGIBLE",
        results=[
            CriterionEvaluationResult(
                criterion_id="c1",
                criterion_type=CriterionType.PERCENTAGE,
                description="Marks >= 60%",
                status=EvaluationStatus.FAIL,
                applicant_value="55.0%",
                requirement_value="60.0%",
                evidence_quote="minimum 60% aggregate marks",
                explanation="Marks (55.0%) do not meet cutoff (60.0%).",
            )
        ],
    )

    plan = ActionNavigatorService.generate_plan(
        notice_text=SAMPLE_NOTICE,
        profile=profile,
        eligibility=eligibility,
    )

    # Step 1 should be BLOCKED
    step1 = next(it for it in plan.items if it.id == "ACT-01")
    assert step1.status == ActionItemStatus.BLOCKED

    # Application submission should also be BLOCKED
    sub_step = next(it for it in plan.items if it.id == "ACT-05")
    assert sub_step.status == ActionItemStatus.BLOCKED
    assert len(sub_step.blocked_by) > 0


def test_action_navigator_status_update():
    plan = ActionNavigatorService.generate_plan(notice_text=SAMPLE_NOTICE)

    # Complete document prep
    updated_plan = ActionNavigatorService.update_item_status(
        plan=plan,
        action_id="ACT-03",
        new_status=ActionItemStatus.COMPLETED,
        user_notes="All degrees and caste certificate attested.",
    )

    updated_doc = next(it for it in updated_plan.items if it.id == "ACT-03")
    assert updated_doc.status == ActionItemStatus.COMPLETED
    assert updated_doc.completed_at is not None
    assert updated_doc.user_notes == "All degrees and caste certificate attested."


def test_api_action_navigator_endpoints():
    gen_resp = client.post(
        "/api/actions/generate",
        json={"notice_text": SAMPLE_NOTICE},
    )
    assert gen_resp.status_code == 200
    plan_data = gen_resp.json()
    assert len(plan_data["items"]) >= 4

    update_resp = client.post(
        "/api/actions/update-status",
        json={
            "plan": plan_data,
            "action_id": "ACT-01",
            "status": "COMPLETED",
        },
    )
    assert update_resp.status_code == 200
    up_data = update_resp.json()
    assert up_data["completed_count"] >= 1


def test_action_navigator_with_revision_ledger_corrigendum():
    """Regression test: ActionNavigatorService handles RevisionLedger without AttributeError."""
    ledger = RevisionLedger(
        source_notice_id="N1",
        target_notice_id="N2",
        relationship=NoticeRelationship(
            source_notice_id="N1",
            target_notice_id="N2",
            relationship_type=RelationshipType.AMENDMENT,
            confidence="HIGH",
            evidence_quote="This corrigendum modifies deadline",
        ),
        entries=[
            RevisionEntry(
                field_name="required_action_and_deadline",
                display_name="Deadline",
                old_value="October 15, 2026",
                new_value="November 05, 2026",
                change_category=ChangeCategory.MODIFIED,
                new_evidence_quote="extended to November 05, 2026",
            ),
            RevisionEntry(
                field_name="application_fee",
                display_name="Application Fee",
                old_value="Rs. 500",
                new_value="Rs. 250",
                change_category=ChangeCategory.MODIFIED,
                new_evidence_quote="fee reduced to Rs. 250",
            ),
        ],
    )

    plan = ActionNavigatorService.generate_plan(
        notice_text=SAMPLE_NOTICE,
        revision_ledger=ledger,
    )

    # Verify deadline step picked up the updated corrigendum deadline
    sub_step = next(it for it in plan.items if it.id == "ACT-05")
    assert "November 05, 2026" in sub_step.deadline
    assert "(Updated via Corrigendum)" in sub_step.deadline

    # Verify fee step picked up the updated corrigendum fee
    fee_step = next(it for it in plan.items if it.id == "ACT-04")
    assert "Rs. 250" in fee_step.fee_amount
    assert "(Updated via Corrigendum)" in fee_step.fee_amount
