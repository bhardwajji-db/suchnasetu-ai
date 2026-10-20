"""
Tests for notice fingerprinting, stale-result detection, and buffer clearing in Notice2Action AI.
"""

import hashlib
from pathlib import Path
from streamlit.testing.v1 import AppTest
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
)


def _mock_structured_notice() -> StructuredNotice:
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="Merit Scholarship Application",
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
            value="Marksheet, College identity card, Bank account proof",
            status=CertaintyStatus.STATED,
            evidence_quote="Required documents: 1. Previous qualifying examination marksheet",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="Scholarship Office, Room 204; Email: scholarships@example.invalid",
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
        missing_information=[],
        uncertain_or_conflicting_details=[],
    )


def test_buffer_clear_resets_all_state():
    at = AppTest.from_file("../app.py", default_timeout=15)
    at.run()
    # Pre-populate state
    at.session_state.raw_notice_text = "Some temporary notice text"
    at.session_state.structured_notice = _mock_structured_notice()
    at.session_state.analyzed_fingerprint = hashlib.sha256("Some temporary notice text".encode()).hexdigest()
    at.session_state.summary_en = "Some summary"
    at.session_state.analysis_duration = 12.34
    at.run()

    # Click Clear Buffer button
    clear_btn = [b for b in at.button if "Clear Buffer" in b.label]
    assert len(clear_btn) > 0, "Clear buffer button should be present"
    clear_btn[0].click().run()

    assert at.session_state.raw_notice_text == ""
    assert at.session_state.structured_notice is None
    assert at.session_state.summary_en is None
    assert at.session_state.analyzed_fingerprint is None
    assert at.session_state.analysis_duration is None


def test_editing_buffer_detects_stale_fingerprint():
    at = AppTest.from_file("../app.py", default_timeout=15)
    at.run()
    initial_text = "Original notice content"
    at.session_state.raw_notice_text = initial_text
    at.session_state.structured_notice = _mock_structured_notice()
    at.session_state.analyzed_fingerprint = hashlib.sha256(initial_text.encode()).hexdigest()
    at.run()

    # Edit buffer text
    at.session_state.raw_notice_text = "Edited notice content with new deadline"
    at.run()

    # Verify stale warning appears in warning elements
    warnings = [w.value for w in at.warning]
    assert any("Notice Buffer Modified" in w or "Stale Results" in w for w in warnings), (
        f"Expected stale warning banner when buffer is edited, got: {warnings}"
    )


def test_empty_notice_validation():
    at = AppTest.from_file("../app.py", default_timeout=15)
    at.run()
    at.session_state.raw_notice_text = "   "
    at.run()

    analyze_btn = [b for b in at.button if "Analyze Notice with Gemma 4" in b.label]
    assert len(analyze_btn) > 0
    analyze_btn[0].click().run()

    errors = [e.value for e in at.error]
    assert any("Please supply notice text" in e for e in errors), (
        f"Expected empty notice error, got: {errors}"
    )
