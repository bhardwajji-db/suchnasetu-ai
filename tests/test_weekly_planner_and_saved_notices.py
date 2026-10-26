"""
Unit and Integration Tests for Saved Notices & Weekly Action Planner.
Verifies cross-user isolation, weekly deadline computation (today + 7 days),
ambiguous/tentative date tagging, and natural language query answers.
"""

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.storage.db import get_db
from notice2action.services.weekly_planner_service import weekly_planner


@pytest.fixture
def client():
    return TestClient(app)


def test_cross_user_isolation(client):
    db = get_db()
    user_a = "user_alpha_101"
    user_b = "user_beta_202"

    # User A saves a notice
    saved_a = db.save_notice_for_user(
        user_id=user_a,
        document_id="doc_a1",
        title="Scholarship Application Form",
        authority="Higher Education Dept",
        deadline="2026-10-31",
        assignment_title="Submit Income Certificate",
    )
    assert saved_a["user_id"] == user_a

    # User B saves a different notice
    saved_b = db.save_notice_for_user(
        user_id=user_b,
        document_id="doc_b1",
        title="Hostel Allotment Notice",
        authority="Campus Administration",
        deadline="2026-11-15",
        assignment_title="Hostel Room Deposit",
    )
    assert saved_b["user_id"] == user_b

    # Verify isolation
    list_a = db.list_saved_notices_for_user(user_a)
    list_b = db.list_saved_notices_for_user(user_b)

    assert any(n["document_id"] == "doc_a1" for n in list_a)
    assert not any(n["document_id"] == "doc_b1" for n in list_a)

    assert any(n["document_id"] == "doc_b1" for n in list_b)
    assert not any(n["document_id"] == "doc_a1" for n in list_b)

    # Clean up
    db.unsave_notice_for_user(user_a, "doc_a1")
    db.unsave_notice_for_user(user_b, "doc_b1")


def test_saved_notice_search():
    db = get_db()
    user = "user_search_test"

    db.save_notice_for_user(
        user_id=user,
        document_id="doc_s1",
        title="B.Tech Final Semester Exam Schedule",
        authority="Examination Board",
        deadline="2026-11-05",
    )
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_s2",
        title="Library Book Return and Fine Exemption",
        authority="Central Library",
        deadline="2026-11-02",
    )

    # Search for "Exam"
    results_exam = db.list_saved_notices_for_user(user, search_query="exam")
    assert len(results_exam) == 1
    assert results_exam[0]["document_id"] == "doc_s1"

    # Search for "Library"
    results_lib = db.list_saved_notices_for_user(user, search_query="library")
    assert len(results_lib) == 1
    assert results_lib[0]["document_id"] == "doc_s2"

    # Search for non-matching
    assert len(db.list_saved_notices_for_user(user, search_query="astronaut")) == 0

    # Clean up
    db.unsave_notice_for_user(user, "doc_s1")
    db.unsave_notice_for_user(user, "doc_s2")


def test_weekly_action_planner_chronological_ordering():
    db = get_db()
    user = "user_weekly_plan_test"
    ref_date = date(2026, 10, 25)

    # Notice 1: Due in 2 days (Oct 27) -> Due this week
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_w1",
        title="Physics Assignment 1",
        deadline="2026-10-27",
    )
    # Notice 2: Due in 5 days (Oct 30) -> Due this week
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_w2",
        title="Math Project Report",
        deadline="2026-10-30",
    )
    # Notice 3: Due in 12 days (Nov 06) -> Upcoming later
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_w3",
        title="Chemistry Lab Viva",
        deadline="2026-11-06",
    )
    # Notice 4: Expired 3 days ago (Oct 22) -> Past due
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_w4",
        title="Late Registration Fee",
        deadline="2026-10-22",
    )
    # Notice 5: Tentative date
    db.save_notice_for_user(
        user_id=user,
        document_id="doc_w5",
        title="Campus Placement Drive",
        deadline="Tentative by First Week of November 2026",
    )

    plan = weekly_planner.get_weekly_plan(user_id=user, reference_date=ref_date)

    assert plan["due_this_week_count"] == 2
    assert len(plan["due_this_week"]) == 2
    # Verify chronological ordering: earliest (Oct 27) before later (Oct 30)
    assert plan["due_this_week"][0]["task_title"] == "Physics Assignment 1"
    assert plan["due_this_week"][1]["task_title"] == "Math Project Report"

    # Verify upcoming later
    assert any(t["task_title"] == "Chemistry Lab Viva" for t in plan["upcoming_later"])

    # Verify past due
    assert any(t["task_title"] == "Late Registration Fee" for t in plan["past_due"])

    # Verify ambiguous tasks
    assert any("Campus Placement Drive" in t["task_title"] for t in plan["ambiguous_tasks"])

    # Clean up
    for doc in ["doc_w1", "doc_w2", "doc_w3", "doc_w4", "doc_w5"]:
        db.unsave_notice_for_user(user, doc)


def test_what_do_i_need_to_complete_this_week_query(client):
    ref_date = date.today()
    in_3_days = (ref_date + timedelta(days=3)).strftime("%Y-%m-%d")

    # Save a notice via API
    save_res = client.post(
        "/api/user/saved-notices/doc_query_test",
        json={
            "title": "Computer Networks Assignment 3",
            "authority": "Dept of Computer Science",
            "deadline": in_3_days,
            "assignment_title": "Packet Tracing Submission",
        },
    )
    assert save_res.status_code == 200

    # Query: What do I need to complete this week?
    query_res = client.post(
        "/api/user/weekly-tasks/query",
        json={"query": "What do I need to complete this week?"},
    )
    assert query_res.status_code == 200
    data = query_res.json()
    assert data["due_this_week_count"] >= 1
    assert "Computer Networks Assignment 3" in data["summary"]
    assert in_3_days in data["summary"]

    # Delete saved notice
    del_res = client.delete("/api/user/saved-notices/doc_query_test")
    assert del_res.status_code == 200
