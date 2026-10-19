"""
Streamlit App Interaction and UI Rendering Tests for Notice2Action AI (PS02).
Uses Streamlit's official AppTest framework to verify UI components, tabs,
and session state rendering without requiring a running browser.
"""

from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_ui_render_synthetic_notice_tabs():
    """Verifies that the Streamlit application renders all tabs and cards properly."""
    txt_path = Path("tests/fixtures/synthetic_scholarship_notice.txt")
    assert txt_path.is_file()
    sample_text = txt_path.read_text(encoding="utf-8")

    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception, f"Initial render failed: {at.exception}"

    # Load notice into session state and re-run
    at.session_state.raw_notice_text = sample_text
    at.run()
    assert not at.exception, f"Render with notice text failed: {at.exception}"

    # Check that main UI elements exist
    assert len(at.tabs) == 4
    assert "Notice Ingestion & OCR" in at.tabs[0].label
    assert "Grounded Fact Breakdown" in at.tabs[1].label
    assert "Summary & Action Checklist" in at.tabs[2].label
    assert "Follow-Up Q&A" in at.tabs[3].label


def test_ui_render_with_structured_data():
    """Verifies UI rendering when structured analysis and checklist are populated."""
    from notice2action.schemas import (
        StructuredNotice,
        ExtractedFact,
        CertaintyStatus,
        PlainLanguageSummary,
        ActionChecklist,
        ChecklistItem,
        FollowUpAnswer,
    )

    sn = StructuredNotice(
        notice_id="TEST-SCH-2026-001",
        purpose=ExtractedFact(
            field_name="purpose",
            value="Merit Scholarship Application",
            status=CertaintyStatus.STATED,
            evidence_quote="Subject: Merit Scholarship Application",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="30 October 2026 at 5:00 PM",
            status=CertaintyStatus.STATED,
            evidence_quote="by 5:00 PM on 30 October 2026",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Students with at least 80% marks",
            status=CertaintyStatus.STATED,
            evidence_quote="at least 80% marks in their last qualifying examination",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="No application fee mentioned",
            status=CertaintyStatus.NOT_STATED,
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Previous marksheet, College ID card, Bank account proof",
            status=CertaintyStatus.STATED,
            evidence_quote="Required documents: 1. Previous qualifying examination marksheet. 2. College identity card. 3. Bank account proof.",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="Room 204, Academic Block; scholarships@example.invalid",
            status=CertaintyStatus.STATED,
            evidence_quote="Room 204, Academic Block. Helpdesk: scholarships@example.invalid",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit application and supporting documents to Scholarship Office",
            status=CertaintyStatus.STATED,
            evidence_quote="Submit the application and supporting documents to the Scholarship Office",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Late applications will not be accepted",
            status=CertaintyStatus.STATED,
            evidence_quote="Late applications will not be accepted.",
        ),
        missing_information=["Application form link or format not specified"],
    )

    summary = PlainLanguageSummary(
        about="Merit scholarship application for high-performing students.",
        eligible="Students with at least 80% marks in previous examination.",
        actions="Submit application to Room 204.",
        documents="Marksheet, College ID, Bank account proof.",
        deadline="30 October 2026 at 5:00 PM.",
        help_contact="scholarships@example.invalid",
        missing="Application form download link.",
    )

    checklist = ActionChecklist(
        notice_id="TEST-SCH-2026-001",
        items=[
            ChecklistItem(
                step_number=1,
                action="Gather marksheets and ID card",
                category="DOCUMENTATION",
                is_mandatory=True,
                grounded_quote="Required documents: 1. Previous qualifying examination marksheet.",
            ),
            ChecklistItem(
                step_number=2,
                action="Submit before deadline",
                category="SUBMISSION",
                is_mandatory=True,
                grounded_quote="by 5:00 PM on 30 October 2026",
            ),
        ],
    )

    qa_item = FollowUpAnswer(
        question="What is the deadline?",
        answer="The deadline is 5:00 PM on 30 October 2026.",
        is_supported=True,
        evidence_quote="by 5:00 PM on 30 October 2026",
    )

    from unittest.mock import patch

    with patch("notice2action.ui.components.generate_audio_bytes", return_value=b"fake-mp3-bytes"):
        at = AppTest.from_file("../app.py")
        at.run(timeout=10)
        assert not at.exception

        # Populate session state
        at.session_state.raw_notice_text = "INSTITUTE OF TECHNOLOGY TEST NOTICE"
        at.session_state.structured_notice = sn
        at.session_state.summary_en = summary
        at.session_state.checklist_en = checklist
        at.session_state.followup_history = [qa_item]
        at.run(timeout=10)

        assert not at.exception, f"Render with structured notice failed: {at.exception}"

        # Switch to Hindi language and verify render
        at.session_state.selected_lang = "hi"
        at.run(timeout=10)
        assert not at.exception, f"Render in Hindi mode failed: {at.exception}"


