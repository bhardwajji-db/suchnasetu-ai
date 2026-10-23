"""
Unit and Integration Tests for Multi-Notice Revision Ledger and Relationship Engine.
Verifies corrigendum linking, field diffing, date extensions, and quote preservation.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    RelationshipType,
    ChangeCategory,
    CertaintyStatus,
)
from notice2action.services.relationship_engine import relationship_engine
from notice2action.services.revision_engine import revision_engine


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def base_notice():
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="National Merit Scholarship Scheme 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="National Merit Scholarship Scheme for Higher Technical & Professional Education",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="15 February 2026, 5:00 PM",
            status=CertaintyStatus.STATED,
            evidence_quote="The last date for online submission of applications is 15 February 2026, 5:00 PM.",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Bachelor's Degree in Science or Engineering with 65% aggregate. Max 25 years.",
            status=CertaintyStatus.STATED,
            evidence_quote="Bachelor's Degree in Science or Engineering with a minimum 65% aggregate marks. Max 25 years.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="₹500 for General/OBC. SC/ST exempted.",
            status=CertaintyStatus.STATED,
            evidence_quote="Application fee is ₹500 for General and OBC category applicants.",
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Marksheets, Degree, Caste Certificate",
            status=CertaintyStatus.STATED,
            evidence_quote="Upload Self-Attested Marksheets, Degree Certificate, Valid Caste Certificate",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit online application via portal",
            status=CertaintyStatus.STATED,
            evidence_quote="Online application submission commences on 15 January 2026.",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="helpdesk@scholarships.gov.in",
            status=CertaintyStatus.STATED,
            evidence_quote="National Scholarship Portal Helpdesk: helpdesk@scholarships.gov.in",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Late submissions not accepted.",
            status=CertaintyStatus.STATED,
            evidence_quote="Late submissions will not be entertained under any circumstances.",
        ),
        issuing_authority=ExtractedFact(
            field_name="issuing_authority",
            value="Ministry of Education & National Scholarship Board",
            status=CertaintyStatus.STATED,
            evidence_quote="Ministry of Education & National Scholarship Board, New Delhi.",
        ),
        notice_reference_number=ExtractedFact(
            field_name="notice_reference_number",
            value="NMS/2026/01",
            status=CertaintyStatus.STATED,
            evidence_quote="Notice No. NMS/2026/01.",
        ),
    )


@pytest.fixture
def revised_notice():
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="National Merit Scholarship Scheme 2026 (Corrigendum)",
            status=CertaintyStatus.STATED,
            evidence_quote="Corrigendum to Notification No. NMS/2026/01 dated 10 Jan 2026.",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="28 February 2026, 11:59 PM",
            status=CertaintyStatus.STATED,
            evidence_quote="last date for online submission of applications is hereby extended to 28 February 2026, 11:59 PM.",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Revised: 60% for OBC candidates. General remains 65%. Max 25 years.",
            status=CertaintyStatus.STATED,
            evidence_quote="The minimum qualifying marks for OBC candidates is revised to 60% aggregate.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="₹500 for General/OBC. SC/ST exempted. UPI payment accepted.",
            status=CertaintyStatus.STATED,
            evidence_quote="Applicants can now also pay fees via UPI in addition to Net Banking",
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Marksheets, Degree, Caste Certificate",
            status=CertaintyStatus.STATED,
            evidence_quote="All other terms and conditions remain unchanged.",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit online application via portal",
            status=CertaintyStatus.STATED,
            evidence_quote="All other terms remain unchanged.",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="helpdesk@scholarships.gov.in",
            status=CertaintyStatus.STATED,
            evidence_quote="Helpdesk remains unchanged.",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Late submissions not accepted.",
            status=CertaintyStatus.STATED,
            evidence_quote="Late submissions will not be entertained under any circumstances.",
        ),
        issuing_authority=ExtractedFact(
            field_name="issuing_authority",
            value="Ministry of Education & National Scholarship Board",
            status=CertaintyStatus.STATED,
            evidence_quote="Ministry of Education & National Scholarship Board, New Delhi.",
        ),
        notice_reference_number=ExtractedFact(
            field_name="notice_reference_number",
            value="NMS/2026/01-CORR",
            status=CertaintyStatus.STATED,
            evidence_quote="Notice No. NMS/2026/01-CORR.",
        ),
    )


def test_relationship_detection_explicit_amendment():
    text_a = "NATIONAL MERIT SCHOLARSHIP. Notice No. NMS/2026/01."
    text_b = "CORRIGENDUM. In partial modification to Advertisement No. NMS/2026/01, the last date is extended."

    rel = relationship_engine.detect_relationship("notice_a", "notice_b", text_a, text_b)
    assert rel.relationship_type in (RelationshipType.AMENDMENT, RelationshipType.EXTENSION)
    assert rel.confidence == "HIGH"
    assert "partial modification" in rel.evidence_quote.lower() or "extended" in rel.evidence_quote.lower()


def test_relationship_detection_cancellation():
    text_a = "RECRUITMENT NOTICE. Advt No. 04/2026."
    text_b = "PUBLIC NOTICE. The advertisement Advt No. 04/2026 stands cancelled with immediate effect."

    rel = relationship_engine.detect_relationship("notice_a", "notice_b", text_a, text_b)
    assert rel.relationship_type == RelationshipType.CANCELLATION
    assert rel.confidence == "HIGH"
    assert "cancelled" in rel.evidence_quote.lower()


def test_relationship_detection_unrelated():
    text_a = "Scholarship application for engineering students."
    text_b = "Municipal Water Supply shutdown in Sector 4 on Monday."

    rel = relationship_engine.detect_relationship("notice_a", "notice_b", text_a, text_b)
    assert rel.relationship_type in (RelationshipType.RELATED, RelationshipType.UNRESOLVED)
    assert rel.confidence != "HIGH"


def test_revision_engine_detects_deadline_modification(base_notice, revised_notice):
    ledger = revision_engine.build_revision_ledger(
        source_id="notice_a",
        target_id="notice_b",
        source_notice=base_notice,
        target_notice=revised_notice,
        source_raw_text="Base notice text",
        target_raw_text="In partial modification to NMS/2026/01, last date is extended to 28 February 2026.",
    )

    # Find deadline entry
    dl_entry = next((e for e in ledger.entries if e.field_name == "deadline"), None)
    assert dl_entry is not None
    assert dl_entry.change_category == ChangeCategory.MODIFIED
    assert "15 February 2026" in dl_entry.old_value
    assert "28 February 2026" in dl_entry.new_value
    assert dl_entry.new_evidence_quote is not None
    assert "last date for online submission" in dl_entry.new_evidence_quote


def test_revision_engine_detects_unchanged_fields(base_notice, revised_notice):
    ledger = revision_engine.build_revision_ledger(
        source_id="notice_a",
        target_id="notice_b",
        source_notice=base_notice,
        target_notice=revised_notice,
    )

    auth_entry = next((e for e in ledger.entries if e.field_name == "issuing_authority"), None)
    assert auth_entry is not None
    assert auth_entry.change_category == ChangeCategory.UNCHANGED


def test_api_relationships_detect_endpoint(client):
    payload = {
        "source_text": "Notice No. 101/2026. Recruitment of Engineers.",
        "target_text": "Corrigendum to Notice No. 101/2026. The last date is hereby extended to 30th March.",
    }
    res = client.post("/api/relationships/detect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["relationship_type"] in ("AMENDMENT", "EXTENSION")
    assert data["confidence"] == "HIGH"


def test_api_revision_ledger_compare_endpoint(client, base_notice, revised_notice):
    with patch("notice2action.api.server.NoticeAnalyzer.analyze_notice", side_effect=[base_notice, revised_notice]):
        payload = {
            "source_text": "Notice No. 101/2026. Last date is 10 March 2026. Fee is ₹100.",
            "target_text": "Corrigendum to 101/2026. In partial modification, last date is extended to 25 March 2026. Fee is ₹100.",
        }
        res = client.post("/api/revision-ledger/compare", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "entries" in data
        assert len(data["entries"]) > 0
        assert "relationship" in data
