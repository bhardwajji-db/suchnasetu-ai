"""
Tests for Personal Impact Change Tracker.
Verifies that notice amendments are evaluated against individual applicant
profiles, detecting deadline extensions, fee reductions, and qualification shifts.
"""

import pytest
from fastapi.testclient import TestClient
from notice2action.api.server import app
from notice2action.schemas import (
    ApplicantProfile,
    ChangeCategory,
    ImpactType,
)
from notice2action.services.impact_engine import PersonalImpactEngine

client = TestClient(app)

ORIGINAL_NOTICE = """CENTRAL SCHOLARSHIP NOTIFICATION 2026
Department of Higher Education
Advt. No. CMS/2026/04

1. Last date for submission: October 15, 2026.
2. Mandatory Qualification: Master's Degree with minimum 65% aggregate marks.
3. Maximum age limit: 30 years as on October 01, 2026.
4. Application fee: Rs. 500.
"""

CORRIGENDUM_NOTICE = """CORRIGENDUM TO ADVERTISEMENT NO. CMS/2026/04
Department of Higher Education

This corrigendum modifies Advertisement No. CMS/2026/04 as follows:
1. The last date for online submission is hereby extended to November 05, 2026.
2. Qualifying marks requirement in Master's Degree is relaxed to minimum 60% aggregate marks.
3. The application fee is reduced to Rs. 250 for all candidates.
All other terms remain unchanged.
"""


def test_personal_impact_deadline_extension_and_fee_reduction():
    profile = ApplicantProfile(
        marks_percentage=62.0,
        category="General",
    )
    report = PersonalImpactEngine.evaluate_impact(
        source_text=ORIGINAL_NOTICE,
        target_text=CORRIGENDUM_NOTICE,
        profile=profile,
    )

    assert report.impact_level in ["HIGH", "MODERATE"]
    assert len(report.impact_items) >= 3

    # Check deadline item
    deadline_items = [it for it in report.impact_items if "deadline" in it.field_name.lower()]
    assert len(deadline_items) == 1
    dl = deadline_items[0]
    assert dl.impact_type == ImpactType.BENEFICIAL
    assert "21 Days" in dl.headline

    # Check fee item
    fee_items = [it for it in report.impact_items if "fee" in it.field_name.lower()]
    assert len(fee_items) == 1
    fee = fee_items[0]
    assert fee.impact_type == ImpactType.BENEFICIAL
    assert "Rs. 250" in fee.headline

    # Check marks relaxation item
    marks_items = [it for it in report.impact_items if "eligibility" in it.field_name.lower() or "marks" in it.field_name.lower()]
    assert len(marks_items) == 1
    marks = marks_items[0]
    assert marks.previous_status == "FAIL"
    assert marks.new_status == "PASS"
    assert marks.impact_type == ImpactType.BENEFICIAL
    assert "You Are Now Eligible" in marks.headline


def test_personal_impact_unchanged_documents():
    report = PersonalImpactEngine.evaluate_impact(
        source_text=ORIGINAL_NOTICE,
        target_text=ORIGINAL_NOTICE,
    )
    assert report.impact_level == "NEUTRAL"
    assert len(report.impact_items) == 0


def test_api_evaluate_personal_impact_endpoint():
    resp = client.post(
        "/api/impact/evaluate",
        json={
            "source_text": ORIGINAL_NOTICE,
            "target_text": CORRIGENDUM_NOTICE,
            "applicant_profile": {
                "marks_percentage": 62.0,
                "category": "General",
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Positive Impact" in data["overall_impact_summary"]
    assert len(data["impact_items"]) >= 3
    assert len(data["recommended_next_actions"]) > 0
