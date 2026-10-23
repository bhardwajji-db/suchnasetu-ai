"""
Unit and Integration Tests for Explainable Applicant Eligibility Engine.
Verifies criteria extraction, deterministic Python rule checks, category relaxations,
boundary conditions, and epistemic honesty (PASS, FAIL, UNKNOWN).
"""

from unittest.mock import patch
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
from notice2action.services.eligibility_engine import eligibility_engine


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def scholarship_notice():
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="National Merit Scholarship 2026",
            status=CertaintyStatus.STATED,
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="15 February 2026",
            status=CertaintyStatus.STATED,
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Candidates must hold a Bachelor's Degree in Science or Engineering with minimum 65% aggregate. Age limit: not exceed 25 years as of 01-08-2026. 3 years relaxation for OBC, 5 years for SC/ST.",
            status=CertaintyStatus.STATED,
            evidence_quote="Candidates must hold a Bachelor's Degree in Science or Engineering with minimum 65% aggregate. Age limit: not exceed 25 years as of 01-08-2026. 3 years relaxation for OBC, 5 years for SC/ST.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="₹500 for General/OBC",
            status=CertaintyStatus.STATED,
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Degree Certificate, Marksheet",
            status=CertaintyStatus.STATED,
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="helpdesk@scholarships.gov.in",
            status=CertaintyStatus.STATED,
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Apply online before deadline",
            status=CertaintyStatus.STATED,
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Strict age cutoff applied",
            status=CertaintyStatus.STATED,
        ),
    )


def test_criteria_extraction(scholarship_notice):
    criteria = eligibility_engine.extract_criteria(scholarship_notice)
    assert len(criteria) >= 2

    # Check age criterion
    age_crit = next((c for c in criteria if c.criterion_type == CriterionType.AGE), None)
    assert age_crit is not None
    assert age_crit.threshold_value == "25"
    assert "OBC" in age_crit.category_relaxations
    assert age_crit.category_relaxations["OBC"] == "3"

    # Check marks criterion
    marks_crit = next((c for c in criteria if c.criterion_type == CriterionType.PERCENTAGE), None)
    assert marks_crit is not None
    assert marks_crit.threshold_value == "65"


def test_eligibility_age_evaluation_pass(scholarship_notice):
    criteria = eligibility_engine.extract_criteria(scholarship_notice)

    # 24-year-old General candidate passes (limit is 25)
    profile = ApplicantProfile(age_years=24.0, category="General", degree="B.Sc", marks_percentage=70.0)
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    age_res = next((r for r in assessment.results if r.criterion_type == CriterionType.AGE), None)
    assert age_res is not None
    assert age_res.status == EvaluationStatus.PASS


def test_eligibility_age_relaxation_for_obc(scholarship_notice):
    criteria = eligibility_engine.extract_criteria(scholarship_notice)

    # 27-year-old OBC candidate passes (25 + 3 = 28 limit)
    profile_obc = ApplicantProfile(age_years=27.0, category="OBC", degree="B.Sc", marks_percentage=70.0)
    assessment_obc = eligibility_engine.evaluate_profile(criteria, profile_obc)
    age_res_obc = next((r for r in assessment_obc.results if r.criterion_type == CriterionType.AGE), None)
    assert age_res_obc is not None
    assert age_res_obc.status == EvaluationStatus.PASS

    # 27-year-old General candidate fails (limit is 25)
    profile_gen = ApplicantProfile(age_years=27.0, category="General", degree="B.Sc", marks_percentage=70.0)
    assessment_gen = eligibility_engine.evaluate_profile(criteria, profile_gen)
    age_res_gen = next((r for r in assessment_gen.results if r.criterion_type == CriterionType.AGE), None)
    assert age_res_gen is not None
    assert age_res_gen.status == EvaluationStatus.FAIL


def test_eligibility_strict_marks_boundary(scholarship_notice):
    criteria = eligibility_engine.extract_criteria(scholarship_notice)

    # Candidate with 64.9% fails strict 65.0% requirement (no rounding up)
    profile = ApplicantProfile(marks_percentage=64.9, age_years=23.0, degree="B.Sc")
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    marks_res = next((r for r in assessment.results if r.criterion_type == CriterionType.PERCENTAGE), None)
    assert marks_res is not None
    assert marks_res.status == EvaluationStatus.FAIL
    assert assessment.overall_status == "NOT_ELIGIBLE"


def test_eligibility_missing_applicant_info_returns_unknown(scholarship_notice):
    criteria = eligibility_engine.extract_criteria(scholarship_notice)

    # Profile with no degree or marks provided
    profile = ApplicantProfile(age_years=22.0)
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    marks_res = next((r for r in assessment.results if r.criterion_type == CriterionType.PERCENTAGE), None)
    assert marks_res is not None
    assert marks_res.status == EvaluationStatus.UNKNOWN
    assert marks_res.missing_info is not None
    assert assessment.overall_status == "INCONCLUSIVE"


def test_api_eligibility_extract_and_evaluate(client, scholarship_notice):
    notice_text = (
        "SCHOLARSHIP NOTIFICATION 2026.\n"
        "Eligibility: Minimum 60% aggregate in Bachelor's Degree. Max age 25 years as on 01-08-2026."
    )

    with patch("notice2action.api.server.NoticeAnalyzer.analyze_notice", return_value=scholarship_notice):
        # 1. Extract criteria
        extract_res = client.post("/api/eligibility/extract-criteria", json={"notice_text": notice_text})
        assert extract_res.status_code == 200
        criteria = extract_res.json()
        assert len(criteria) >= 2

        # 2. Evaluate profile
        eval_payload = {
            "notice_text": notice_text,
            "applicant_profile": {
                "date_of_birth": "2002-05-10",
                "degree": "Bachelor of Science",
                "marks_percentage": 68.5,
                "category": "General",
            },
        }
        eval_res = client.post("/api/eligibility/evaluate", json=eval_payload)
        assert eval_res.status_code == 200
        data = eval_res.json()
        assert data["overall_status"] == "ELIGIBLE"
        assert len(data["results"]) >= 2
        for r in data["results"]:
            assert r["status"] == "PASS"
            assert len(r["evidence_quote"]) > 0
