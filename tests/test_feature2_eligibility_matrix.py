"""
Comprehensive Test Suite for Feature 2: Eligibility and Personal Impact Matrix.
Tests the 5 mandatory evaluation scenarios with deterministic verification:
1. Eligible student (B.Tech, 82.5%, age 22 -> ELIGIBLE)
2. Ineligible student (MBA vs B.Tech, and 58% < 60% -> NOT_ELIGIBLE)
3. Student with missing profile info (missing degree/marks -> UNKNOWN / INSUFFICIENT INFORMATION)
4. Notice with ambiguous criteria (qualitative/vague rules -> INCONCLUSIVE / UNCERTAIN)
5. Notice unmentioned condition (no eligibility stated -> default general criterion with explanation)
"""

import pytest
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
def btech_notice():
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="Graduate Engineer Trainee Recruitment 2026",
            status=CertaintyStatus.STATED,
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="2026-11-30",
            status=CertaintyStatus.STATED,
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Candidates must possess a B.Tech degree with minimum 60% aggregate marks. Maximum age 25 years as of 01-08-2026.",
            status=CertaintyStatus.STATED,
            evidence_quote="Candidates must possess a B.Tech degree with minimum 60% aggregate marks. Maximum age 25 years as of 01-08-2026.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="Rs. 250",
            status=CertaintyStatus.STATED,
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="B.Tech Degree Certificate, Marksheets",
            status=CertaintyStatus.STATED,
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit online application before deadline",
            status=CertaintyStatus.STATED,
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="recruitment@eng.gov.in",
            status=CertaintyStatus.STATED,
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Strict verification of degree at interview",
            status=CertaintyStatus.STATED,
        ),
    )


def test_case_1_eligible_student(btech_notice):
    """Case 1: Eligible student (B.Tech, 82.5%, age 22 -> ELIGIBLE)."""
    criteria = eligibility_engine.extract_criteria(btech_notice)
    profile = ApplicantProfile(
        degree="B.Tech",
        marks_percentage=82.5,
        age_years=22.0,
        category="General",
    )
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    assert assessment.overall_status == "ELIGIBLE"
    assert all(r.status == EvaluationStatus.PASS for r in assessment.results)
    for r in assessment.results:
        assert len(r.evidence_quote) > 0


def test_case_2a_ineligible_degree_mismatch(btech_notice):
    """Case 2A: Ineligible student (MBA applying for B.Tech position -> NOT_ELIGIBLE)."""
    criteria = eligibility_engine.extract_criteria(btech_notice)
    profile = ApplicantProfile(
        degree="MBA",  # Incompatible degree
        marks_percentage=85.0,
        age_years=23.0,
        category="General",
    )
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    assert assessment.overall_status == "NOT_ELIGIBLE"
    qual_result = next((r for r in assessment.results if r.criterion_type == CriterionType.QUALIFICATION), None)
    assert qual_result is not None
    assert qual_result.status == EvaluationStatus.FAIL
    assert "does not match required qualification" in qual_result.explanation


def test_case_2b_ineligible_marks_below_threshold(btech_notice):
    """Case 2B: Ineligible student (58.0% when 60.0% required -> NOT_ELIGIBLE)."""
    criteria = eligibility_engine.extract_criteria(btech_notice)
    profile = ApplicantProfile(
        degree="B.Tech",
        marks_percentage=58.0,  # Below 60% requirement
        age_years=22.0,
        category="General",
    )
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    assert assessment.overall_status == "NOT_ELIGIBLE"
    marks_result = next((r for r in assessment.results if r.criterion_type == CriterionType.PERCENTAGE), None)
    assert marks_result is not None
    assert marks_result.status == EvaluationStatus.FAIL
    assert "does not meet the minimum required threshold" in marks_result.explanation


def test_case_3_missing_profile_information(btech_notice):
    """Case 3: Student with missing profile info -> UNKNOWN / INSUFFICIENT INFORMATION."""
    criteria = eligibility_engine.extract_criteria(btech_notice)
    # Profile has age only, missing degree and marks
    profile = ApplicantProfile(
        age_years=22.0,
        category="General",
    )
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    assert assessment.overall_status == "INCONCLUSIVE"
    unknown_results = [r for r in assessment.results if r.status == EvaluationStatus.UNKNOWN]
    assert len(unknown_results) >= 2  # Degree and marks are unknown
    for u in unknown_results:
        assert u.missing_info is not None
        assert len(u.missing_info) > 0


def test_case_4_notice_with_ambiguous_criteria():
    """Case 4: Notice with ambiguous / qualitative criteria -> UNCERTAIN / INCONCLUSIVE."""
    ambiguous_notice = StructuredNotice(
        purpose=ExtractedFact(field_name="purpose", value="Special Fellowship 2026", status=CertaintyStatus.STATED),
        deadline=ExtractedFact(field_name="deadline", value="2026-12-15", status=CertaintyStatus.STATED),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Applicants should demonstrate strong community leadership and relevant practical exposure as per governing norms.",
            status=CertaintyStatus.STATED,
            evidence_quote="Applicants should demonstrate strong community leadership and relevant practical exposure as per governing norms.",
        ),
        fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="Nil", status=CertaintyStatus.STATED),
        required_documents=ExtractedFact(field_name="required_documents", value="Portfolio", status=CertaintyStatus.STATED),
        required_actions=ExtractedFact(field_name="required_actions", value="Apply online", status=CertaintyStatus.STATED),
        contact_details=ExtractedFact(field_name="contact_details", value="fellowship@gov.in", status=CertaintyStatus.STATED),
        important_conditions=ExtractedFact(field_name="important_conditions", value="Subject to interview", status=CertaintyStatus.STATED),
    )

    criteria = eligibility_engine.extract_criteria(ambiguous_notice)
    profile = ApplicantProfile(degree="B.A", marks_percentage=75.0, age_years=24.0)
    assessment = eligibility_engine.evaluate_profile(criteria, profile)

    assert assessment.overall_status == "INCONCLUSIVE"
    assert any("Manual verification" in r.explanation for r in assessment.results)


def test_case_5_notice_unmentioned_condition():
    """Case 5: Notice unmentioned condition (no eligibility criteria stated in notice)."""
    unstated_notice = StructuredNotice(
        purpose=ExtractedFact(field_name="purpose", value="General Public Advisory", status=CertaintyStatus.STATED),
        deadline=ExtractedFact(field_name="deadline", value="2026-11-20", status=CertaintyStatus.STATED),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Not stated in this notice",
            status=CertaintyStatus.NOT_STATED,
            evidence_quote="No specific eligibility rules stated in notice.",
        ),
        fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="Nil", status=CertaintyStatus.STATED),
        required_documents=ExtractedFact(field_name="required_documents", value="None", status=CertaintyStatus.STATED),
        required_actions=ExtractedFact(field_name="required_actions", value="Read circular", status=CertaintyStatus.STATED),
        contact_details=ExtractedFact(field_name="contact_details", value="advisory@gov.in", status=CertaintyStatus.STATED),
        important_conditions=ExtractedFact(field_name="important_conditions", value="For public info", status=CertaintyStatus.STATED),
    )

    criteria = eligibility_engine.extract_criteria(unstated_notice)
    assert len(criteria) == 1
    assert criteria[0].threshold_value == "Not stated in this notice"

    profile = ApplicantProfile(degree="B.Com", marks_percentage=70.0, age_years=21.0)
    assessment = eligibility_engine.evaluate_profile(criteria, profile)
    assert assessment.overall_status == "INCONCLUSIVE"
    assert "No specific eligibility rules stated in notice." in assessment.results[0].evidence_quote
