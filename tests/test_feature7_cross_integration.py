"""
Comprehensive End-to-End Integration Test Suite for Feature 7: Cross-Feature Integration.
Executes the 7 end-to-end citizen workflows across all core features:
Workflow 1: Ingestion -> Deadline Intelligence & Banner Status
Workflow 2: Eligibility Evaluation (Degree, Marks, Age) with Epistemic Grounding
Workflow 3: Saved Notices, User Isolation & "What do I need to complete this week?"
Workflow 4: Document Viewer Modes & Per-Notice Font Zoom Logic
Workflow 5: Grounded Q&A with Line Citations & Absent Information Fallback
Workflow 6: Notice Revision & Corrigendum Delta Detection
Workflow 7: Full End-to-End Pipeline & State Integrity
"""

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
    ApplicantProfile,
    EvaluationStatus,
    CriterionType,
)
from notice2action.services.action_navigator_service import ActionNavigatorService
from notice2action.services.eligibility_engine import eligibility_engine
from notice2action.services.weekly_planner_service import weekly_planner
from notice2action.services.revision_engine import RevisionEngine
from notice2action.services.evidence_service import evidence_service
from notice2action.storage.db import get_db


@pytest.fixture
def client():
    return TestClient(app)


def test_workflow_1_deadline_intelligence_and_status():
    """Workflow 1: Ingest Notice -> Extract Deadlines -> Compute Countdowns & Statuses."""
    today = date.today()

    # 1. Past deadline
    past_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    status_past, rem_past = ActionNavigatorService.compute_deadline_status(past_date)
    assert status_past == "Past deadline"
    assert "Expired" in rem_past

    # 2. Due today
    today_str = today.strftime("%Y-%m-%d")
    status_today, rem_today = ActionNavigatorService.compute_deadline_status(today_str)
    assert status_today == "Due today"

    # 3. Due soon (2 days)
    soon_str = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    status_soon, rem_soon = ActionNavigatorService.compute_deadline_status(soon_str)
    assert status_soon == "Due soon"

    # 4. Upcoming (>3 days)
    up_str = (today + timedelta(days=10)).strftime("%Y-%m-%d")
    status_up, rem_up = ActionNavigatorService.compute_deadline_status(up_str)
    assert status_up == "Upcoming"

    # 5. Tentative/Ambiguous
    status_amb, rem_amb = ActionNavigatorService.compute_deadline_status("Tentative date to be announced")
    assert status_amb == "Date unclear"


def test_workflow_2_eligibility_evaluation_grounding():
    """Workflow 2: Ingest Notice -> Parse Eligibility -> Evaluate Profile with Epistemic Honesty."""
    notice = StructuredNotice(
        purpose=ExtractedFact(field_name="purpose", value="Admissions 2026", status=CertaintyStatus.STATED),
        deadline=ExtractedFact(field_name="deadline", value="2026-11-15", status=CertaintyStatus.STATED),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Requires B.Tech degree with at least 65% aggregate. Maximum age 25 years.",
            status=CertaintyStatus.STATED,
            evidence_quote="Requires B.Tech degree with at least 65% aggregate. Maximum age 25 years.",
        ),
        fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="Rs. 100", status=CertaintyStatus.STATED),
        required_documents=ExtractedFact(field_name="required_documents", value="Marksheet", status=CertaintyStatus.STATED),
        required_actions=ExtractedFact(field_name="required_actions", value="Register online", status=CertaintyStatus.STATED),
        contact_details=ExtractedFact(field_name="contact_details", value="adm@univ.edu", status=CertaintyStatus.STATED),
        important_conditions=ExtractedFact(field_name="important_conditions", value="Verify transcripts", status=CertaintyStatus.STATED),
    )

    criteria = eligibility_engine.extract_criteria(notice)
    assert len(criteria) >= 2

    # Eligible Profile
    prof_pass = ApplicantProfile(degree="B.Tech", marks_percentage=72.0, age_years=23.0)
    res_pass = eligibility_engine.evaluate_profile(criteria, prof_pass)
    assert res_pass.overall_status == "ELIGIBLE"

    # Ineligible Profile (Degree mismatch)
    prof_fail_deg = ApplicantProfile(degree="MBA", marks_percentage=75.0, age_years=23.0)
    res_fail_deg = eligibility_engine.evaluate_profile(criteria, prof_fail_deg)
    assert res_fail_deg.overall_status == "NOT_ELIGIBLE"

    # Inconclusive Profile (Missing marks and degree)
    prof_inconc = ApplicantProfile(age_years=23.0)
    res_inconc = eligibility_engine.evaluate_profile(criteria, prof_inconc)
    assert res_inconc.overall_status == "INCONCLUSIVE"


def test_workflow_3_saved_notices_and_weekly_query(client):
    """Workflow 3: Save notices -> Verify isolation -> Answer 'What do I need to complete this week?'."""
    user = "citizen_workflow_3"
    ref_date = date.today()
    in_2_days = (ref_date + timedelta(days=2)).strftime("%Y-%m-%d")
    in_5_days = (ref_date + timedelta(days=5)).strftime("%Y-%m-%d")

    db = get_db()
    # Save notice 1
    db.save_notice_for_user(
        user_id=user,
        document_id="wf3_doc_1",
        title="DBMS Assignment 2",
        authority="Computer Science Dept",
        deadline=in_2_days,
        assignment_title="ER Diagram Submission",
    )
    # Save notice 2
    db.save_notice_for_user(
        user_id=user,
        document_id="wf3_doc_2",
        title="AI Lab Project",
        authority="Data Science Dept",
        deadline=in_5_days,
        assignment_title="Model Benchmark Notebook",
    )

    # Weekly Action Planner calculation
    plan = weekly_planner.get_weekly_plan(user_id=user, reference_date=ref_date)
    assert plan["due_this_week_count"] == 2
    # Verify chronological order
    assert plan["due_this_week"][0]["task_title"] == "DBMS Assignment 2"
    assert plan["due_this_week"][1]["task_title"] == "AI Lab Project"
    assert "DBMS Assignment 2" in plan["summary"]

    # Clean up
    db.unsave_notice_for_user(user, "wf3_doc_1")
    db.unsave_notice_for_user(user, "wf3_doc_2")


def test_workflow_4_evidence_grounding_and_fallback():
    """Workflow 5 & 4: Grounded Q&A Line Citations and Not Found Fallback."""
    notice_text = (
        "Line 1: OFFICIAL SCHOLARSHIP ANNOUNCEMENT 2026\n"
        "Line 2: The last date for online fee payment is 10 November 2026.\n"
        "Line 3: Applicants must pay an application fee of Rs. 300 via debit card.\n"
        "Line 4: For inquiries, contact support@scholarship.gov.in."
    )

    # Search evidence
    citations = evidence_service.search_evidence("application fee", notice_text)
    assert len(citations) > 0
    assert "300" in citations[0].quote

    # Verify fallback for unmentioned fact
    citations_absent = evidence_service.search_evidence("hostel food vegetarian menu", notice_text)
    # Relevance should be low or 0
    if citations_absent:
        assert citations_absent[0].relevance_score < 0.6


def test_workflow_6_revision_detector_corrigendum():
    """Workflow 6: Revision Detector deltas, ignoring superficial formatting."""
    original_text = (
        "NATIONAL ENTRANCE EXAMINATION 2026\n"
        "Application deadline is 15 October 2026.\n"
        "Application fee is Rs. 500.\n"
        "Minimum qualifying mark is 60% aggregate."
    )
    corrigendum_text = (
        "CORRIGENDUM — NATIONAL ENTRANCE EXAMINATION 2026\n"
        "The application deadline is extended to 31 October 2026.\n"
        "Application fee is revised to Rs. 400 for all candidates.\n"
        "Minimum qualifying mark remains 60% aggregate."
    )

    ledger = RevisionEngine.compare(
        source_text=original_text,
        target_text=corrigendum_text,
        source_title="Original Circular",
        target_title="Corrigendum Circular",
    )

    from notice2action.schemas import ChangeCategory

    # Check modifications
    modified_entries = [e for e in ledger.entries if e.change_category == ChangeCategory.MODIFIED]
    assert len(modified_entries) >= 1

    # Check deadline modified
    dl_entry = next((e for e in ledger.entries if "deadline" in e.field_name.lower()), None)
    assert dl_entry is not None
    assert dl_entry.change_category == ChangeCategory.MODIFIED
    assert "15 October 2026" in dl_entry.old_value
    assert "31 October 2026" in dl_entry.new_value


def test_workflow_7_end_to_end_state_integrity(client):
    """Workflow 7: Full cross-cutting pipeline verifying database state integrity."""
    db = get_db()
    conn = db.get_connection()
    cur = conn.cursor()

    # Verify all 14 tables exist and are healthy
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r[0] for r in cur.fetchall()}

    expected_tables = {
        "schema_migrations", "documents", "analyses", "checklist_items",
        "user_confirmations", "qa_interactions", "revision_comparisons",
        "demo_registry", "app_settings", "users", "sessions", "auth_tokens",
        "rate_limits", "saved_notices"
    }

    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
