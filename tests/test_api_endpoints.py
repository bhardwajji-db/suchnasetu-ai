"""
Comprehensive Integration Tests for Notice2Action AI FastAPI Endpoints.
Verifies REST contract, schemas, error handling, security, and exports.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
    FollowUpAnswer,
    PlainLanguageSummary,
    ActionChecklist,
    ChecklistItem,
)


@pytest.fixture
def client():
    return TestClient(app)


def _mock_structured_notice() -> StructuredNotice:
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="Merit Scholarship Application 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="Notice ID: TEST-SCH-2026-001",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="5:00 PM on 30 October 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="All applications must be submitted by 5:00 PM on 30 October 2026.",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Minimum 75% marks in qualifying examination",
            status=CertaintyStatus.STATED,
            evidence_quote="Students securing minimum 75% marks in their previous qualifying examination are eligible.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="Not stated in the notice.",
            status=CertaintyStatus.NOT_STATED,
            evidence_quote=None,
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Marksheet, College ID card, Bank passbook copy",
            status=CertaintyStatus.STATED,
            evidence_quote="Required documents: 1. Previous qualifying examination marksheet",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="Scholarship Office, Room 204",
            status=CertaintyStatus.STATED,
            evidence_quote="For queries contact: Scholarship Office, Room 204",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit application form with documents before deadline",
            status=CertaintyStatus.STATED,
            evidence_quote="Eligible candidates should submit their completed application form",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Late submissions not accepted",
            status=CertaintyStatus.STATED,
            evidence_quote="Late applications will not be accepted under any circumstances.",
        ),
        missing_information=["Selection criteria"],
        uncertain_or_conflicting_details=[],
        raw_notice_text="Mock raw notice text content.",
    )


def test_api_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "overall_status" in data
    assert "model_name" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 3


def test_api_samples_list(client):
    response = client.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert isinstance(samples, list)
    assert len(samples) >= 4
    sample_ids = [s["id"] for s in samples]
    assert "synthetic_scholarship_notice.txt" in sample_ids


def test_api_samples_get_content(client):
    response = client.get("/api/samples/synthetic_scholarship_notice.txt")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "synthetic_scholarship_notice.txt"
    assert "TEST-SCH-2026-001" in data["content"]
    assert "fingerprint" in data
    assert len(data["fingerprint"]) == 64


def test_api_samples_path_traversal_protection(client):
    response = client.get("/api/samples/../../etc/passwd")
    assert response.status_code in [404, 400]


def test_api_ingest_text_valid(client):
    notice_text = "Notice: College annual scholarship deadline is 30 Oct 2026."
    response = client.post("/api/ingest/text", json={"text": notice_text})
    assert response.status_code == 200
    data = response.json()
    assert data["raw_text"] == notice_text
    assert data["char_count"] == len(notice_text)
    assert len(data["fingerprint"]) == 64


def test_api_ingest_text_empty(client):
    response = client.post("/api/ingest/text", json={"text": "   "})
    assert response.status_code == 422


def test_api_ingest_upload_text_file(client):
    content = b"Official Circular: Examination fees waived."
    files = {"file": ("test_circular.txt", content, "text/plain")}
    response = client.post("/api/ingest/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "text"
    assert "Examination fees waived." in data["raw_text"]


def test_api_ocr_endpoint(client):
    png_path = Path("tests/fixtures/synthetic_notice_ocr.png")
    if not png_path.is_file():
        pytest.skip("synthetic_notice_ocr.png not found")

    with open(png_path, "rb") as f:
        files = {"file": ("synthetic_notice_ocr.png", f.read(), "image/png")}

    data = {"target_lang": "eng", "enhance_contrast": "true"}
    response = client.post("/api/ocr", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert "extracted_text" in res
    assert res["is_preprocessed"] is True
    assert "fingerprint" in res


def test_api_analyze_endpoint(client):
    mock_notice = _mock_structured_notice()
    with patch("notice2action.api.server.NoticeAnalyzer.analyze_notice", return_value=mock_notice):
        payload = {
            "notice_text": "Sample notice text for testing",
            "target_language": "en",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "structured_notice" in data
        assert data["structured_notice"]["purpose"]["value"] == "Merit Scholarship Application 2026"
        assert "summary_en" in data
        assert "summary_hi" in data
        assert "checklist_en" in data
        assert "checklist_hi" in data
        assert data["duration_seconds"] >= 0
        assert len(data["fingerprint"]) == 64


def test_api_followup_endpoint(client):
    mock_answer = FollowUpAnswer(
        question="What documents are needed?",
        answer="You must submit your qualifying examination marksheet and identity card.",
        is_supported=True,
        evidence_quote="Required documents: 1. Previous qualifying examination marksheet",
        unsupported_message=None,
    )
    with patch("notice2action.api.server.FollowUpAssistant.answer_question", return_value=mock_answer):
        payload = {
            "question": "What documents are needed?",
            "notice_text": "Required documents: 1. Previous qualifying examination marksheet",
        }
        response = client.post("/api/followup", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "What documents are needed?"
        assert data["is_supported"] is True
        assert "marksheet" in data["answer"]


def test_api_export_markdown(client):
    mock_notice = _mock_structured_notice()
    summary = PlainLanguageSummary(
        about="Scholarship application",
        eligible="Min 75% marks",
        actions="Apply online",
        documents="Marksheet",
        deadline="30 Oct 2026",
        help_contact="Room 204",
        missing="None",
    )
    checklist = ActionChecklist(
        items=[
            ChecklistItem(
                step_number=1,
                action="Verify marks",
                category="eligibility",
                is_mandatory=True,
                requires_confirmation=False,
                is_completed=False,
            )
        ]
    )
    payload = {
        "structured_notice": mock_notice.model_dump(),
        "summary": summary.model_dump(),
        "checklist": checklist.model_dump(),
    }
    response = client.post("/api/export/markdown", json=payload)
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "Notice2Action AI" in response.text
    assert "Merit Scholarship Application 2026" in response.text


def test_api_export_ics(client):
    checklist = ActionChecklist(
        items=[
            ChecklistItem(
                step_number=1,
                action="Submit Scholarship Form",
                category="submission",
                is_mandatory=True,
                requires_confirmation=False,
                is_completed=False,
            )
        ]
    )
    payload = {
        "checklist": checklist.model_dump(),
        "title": "Scholarship Deadline",
    }
    response = client.post("/api/export/ics", json=payload)
    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert "BEGIN:VCALENDAR" in response.text
    assert "Submit Scholarship Form" in response.text
