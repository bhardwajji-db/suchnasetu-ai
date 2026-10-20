"""
Tests for EvidenceService, SessionStore, Six Core Fields, and OCR Engine Architecture.
Ensures session isolation, exact quotation grounding, and adherence to requirements.
"""

import pytest
import shutil
from pathlib import Path
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
    SixCoreFields,
    NOT_STATED_LABEL,
)
from notice2action.services.evidence_service import EvidenceService, evidence_service
from notice2action.services.session_store import SessionStore, SessionState
from notice2action.ocr import get_ocr_engine, TesseractOCREngine, RapidOCREngine
from notice2action.followup import FollowUpAssistant, NOT_FOUND_MESSAGE
from notice2action.config import config


SAMPLE_NOTICE_TEXT = """DIRECTORATE OF HIGHER EDUCATION
Ref No: DHE-2026-8812
Date: October 15, 2026

NOTICE TO SCHOLARSHIP APPLICANTS
Recipient: All Postgraduate Scholars

Subject: Merit-cum-Means Financial Aid Scheme 2026-27

1. ELIGIBILITY:
Candidates must have scored at least 80% marks in the qualifying degree.
Annual family income must not exceed INR 5,00,000.

2. DEADLINE:
Applications must be submitted by November 30, 2026.
Late applications will not be entertained.

3. CONTACT:
Email: helpdesk@dhe-fictional.gov.in
"""


# ---------------------------------------------------------------------------
# Evidence Service Tests
# ---------------------------------------------------------------------------

def test_evidence_service_indexing_and_search():
    """Tests indexing of notice segments and line-level relevance search."""
    svc = EvidenceService()
    store = svc.index_notice(SAMPLE_NOTICE_TEXT)

    assert store.total_lines > 10
    assert len(store.segments) > 0

    # Search for deadline
    citations = svc.search_evidence("What is the application deadline?", SAMPLE_NOTICE_TEXT)
    assert len(citations) > 0
    top = citations[0]
    assert "November 30, 2026" in top.quote or "DEADLINE" in top.quote
    assert top.line_number > 0


def test_evidence_service_quote_verification():
    """Tests verbatim quote verification in EvidenceService."""
    svc = EvidenceService()
    svc.index_notice(SAMPLE_NOTICE_TEXT)

    # Valid verbatim quote
    exists, line = svc.verify_quote("Annual family income must not exceed INR 5,00,000.", SAMPLE_NOTICE_TEXT)
    assert exists is True
    assert line is not None

    # Hallucinated quote
    fake_exists, _ = svc.verify_quote("There is a fee of INR 500 for application.", SAMPLE_NOTICE_TEXT)
    assert fake_exists is False


# ---------------------------------------------------------------------------
# Session Store Tests
# ---------------------------------------------------------------------------

def test_session_store_lifecycle(tmp_path):
    """Tests isolated session creation, retrieval, updates, and deletion."""
    store = SessionStore(storage_dir=tmp_path / ".sessions")

    # 1. Create session
    s1 = store.create_session({"filename": "notice_1.txt", "raw_notice_text": "Content 1"})
    s2 = store.create_session({"filename": "notice_2.txt", "raw_notice_text": "Content 2"})

    assert s1.session_id != s2.session_id

    # 2. Session isolation: updating s1 does not affect s2
    store.update_session(s1.session_id, {"reading_level": "simple"})
    s1_retrieved = store.get_session(s1.session_id)
    s2_retrieved = store.get_session(s2.session_id)

    assert s1_retrieved.reading_level == "simple"
    assert s2_retrieved.reading_level == "standard"

    # 3. List & delete
    sessions = store.list_sessions()
    assert len(sessions) >= 2

    assert store.delete_session(s1.session_id) is True
    assert store.get_session(s1.session_id) is None


# ---------------------------------------------------------------------------
# Six Core Fields Tests
# ---------------------------------------------------------------------------

def test_six_core_fields_schema():
    """Tests explicit extraction and modeling of the Six Core Fields."""
    issuing = ExtractedFact(field_name="issuing_authority", value="Directorate of Higher Education", status=CertaintyStatus.STATED)
    ref_num = ExtractedFact(field_name="notice_reference_number", value="DHE-2026-8812", status=CertaintyStatus.STATED)
    date = ExtractedFact(field_name="notice_date", value="October 15, 2026", status=CertaintyStatus.STATED)
    recipient = ExtractedFact(field_name="recipient", value="All Postgraduate Scholars", status=CertaintyStatus.STATED)
    subject = ExtractedFact(field_name="main_subject", value="Merit-cum-Means Financial Aid Scheme", status=CertaintyStatus.STATED)
    action_dl = ExtractedFact(field_name="required_action_and_deadline", value="Submit before November 30, 2026", status=CertaintyStatus.STATED)

    core = SixCoreFields(
        issuing_authority=issuing,
        notice_reference_number=ref_num,
        notice_date=date,
        recipient=recipient,
        main_subject=subject,
        required_action_and_deadline=action_dl,
    )

    assert core.issuing_authority.value == "Directorate of Higher Education"
    assert core.notice_reference_number.value == "DHE-2026-8812"
    assert core.notice_date.value == "October 15, 2026"
    assert core.recipient.value == "All Postgraduate Scholars"
    assert core.main_subject.value == "Merit-cum-Means Financial Aid Scheme"
    assert core.required_action_and_deadline.value == "Submit before November 30, 2026"


def test_structured_notice_six_fields_backward_compatibility():
    """Tests that StructuredNotice exposes the Six Core Fields and syncs defaults."""
    dummy_fact = ExtractedFact(field_name="test", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED)
    sn = StructuredNotice(
        purpose=ExtractedFact(field_name="purpose", value="Financial Aid Scheme", status=CertaintyStatus.STATED),
        eligibility=dummy_fact,
        deadline=ExtractedFact(field_name="deadline", value="Nov 30, 2026", status=CertaintyStatus.STATED),
        fee_or_cost=dummy_fact,
        required_documents=dummy_fact,
        contact_details=dummy_fact,
        required_actions=ExtractedFact(field_name="required_actions", value="Submit Online", status=CertaintyStatus.STATED),
        important_conditions=dummy_fact,
    )

    six = sn.to_six_core_fields()
    # Main subject automatically synchronized from purpose
    assert six.main_subject.value == "Financial Aid Scheme"
    # Action and deadline synchronized from deadline & required_actions
    assert "Nov 30, 2026" in six.required_action_and_deadline.value


# ---------------------------------------------------------------------------
# OCR Engine Architecture Tests
# ---------------------------------------------------------------------------

def test_ocr_engine_factory():
    """Verifies that OCR engine factory returns Tesseract by default and RapidOCR adapter on request."""
    tess_engine = get_ocr_engine("tesseract")
    assert isinstance(tess_engine, TesseractOCREngine)
    assert tess_engine.engine_name == "tesseract"

    rapid_engine = get_ocr_engine("rapidocr")
    assert isinstance(rapid_engine, RapidOCREngine)
    assert rapid_engine.engine_name == "rapidocr"


# ---------------------------------------------------------------------------
# Fictional Demo Notices Existence & Quality Check
# ---------------------------------------------------------------------------

def test_three_fictional_demos_exist():
    """Verifies that all 3 dedicated fictional demos exist, are labeled, and non-empty."""
    fixtures_dir = config.synthetic_fixtures_dir

    demo1 = fixtures_dir / "demo_missing_compliance.txt"
    demo2 = fixtures_dir / "demo_outstanding_dues.txt"
    demo3 = fixtures_dir / "demo_response_hearing.txt"

    for p in [demo1, demo2, demo3]:
        assert p.is_file(), f"Missing demo fixture: {p.name}"
        content = p.read_text(encoding="utf-8")
        assert len(content) > 300
        assert "FICTIONAL" in content.upper()


# ---------------------------------------------------------------------------
# Grounded Q&A Absent Info Phrasing
# ---------------------------------------------------------------------------

def test_followup_absent_info_phrase():
    """Verifies that absent notice information returns the exact specified phrase."""
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.generate_structured_json.return_value = {
        "answer": "This information was not found in the provided notice. The notice does not specify this detail.",
        "is_supported": False,
        "evidence_quote": None,
        "unsupported_message": "Penalty fee is absent from notice.",
    }
    assistant = FollowUpAssistant(client=mock_client)
    ans = assistant.answer_question("What is the penalty fee for late submission?", SAMPLE_NOTICE_TEXT)
    assert NOT_FOUND_MESSAGE in ans.answer
    assert ans.is_supported is False
