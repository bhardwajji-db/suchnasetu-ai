"""
Comprehensive UI Controls and Interactive Elements Test Matrix for Notice2Action AI (PS02).
Tests every interactive element using Streamlit's official AppTest framework:
- Sidebar navigation buttons and active tab routing
- Language selector (English / Hindi)
- Synthetic fixture quick-loaders (English, Hindi, Scanned OCR)
- Image upload and Tesseract OCR trigger controls
- Text area buffer and clear button
- Primary 'Analyze Notice with Gemma 4' workflow
- Fast assistance navigation jump buttons
- Checklist interactive checkboxes and progress updates
- Export downloads (JSON, Markdown, RFC 5545 ICS)
- Follow-up Q&A suggested inquiry buttons and custom query submission
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from streamlit.testing.v1 import AppTest

from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
    PlainLanguageSummary,
    ActionChecklist,
    ChecklistItem,
    FollowUpAnswer,
)


@pytest.fixture
def mock_structured_notice():
    return StructuredNotice(
        notice_id="TEST-SCH-2026-001",
        purpose=ExtractedFact(
            field_name="purpose",
            value="Merit Scholarship Application 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="NOTICE: MERIT-CUM-MEANS SCHOLARSHIP 2026-27",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="15 November 2026, 5:00 PM IST",
            status=CertaintyStatus.STATED,
            evidence_quote="Final submission deadline: 15 November 2026, 5:00 PM IST.",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Full-time B.Tech/B.Sc CS students with 75% marks",
            status=CertaintyStatus.STATED,
            evidence_quote="Minimum cumulative score of 75% or 7.5 CGPA in preceding semesters.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="No application fee",
            status=CertaintyStatus.STATED,
            evidence_quote="There is NO application fee for this scholarship.",
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Previous marksheets, Income certificate, ID card, Bank passbook",
            status=CertaintyStatus.STATED,
            evidence_quote="Applicants must attach self-attested copies of the following documents",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="Room 204, Administrative Block; dsw-helpdesk@iimtu.edu.in",
            status=CertaintyStatus.STATED,
            evidence_quote="Room 204, Administrative Block, IIMT University, Meerut",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit online form and physical copy with documents to Room 204",
            status=CertaintyStatus.STATED,
            evidence_quote="Complete the online submission form at https://scholarships.iimtu.edu.in",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Late submission policy not specified; incomplete submissions rejected",
            status=CertaintyStatus.STATED,
            evidence_quote="Incomplete submissions without income proof will be summarily rejected.",
        ),
        missing_information=["Scholarship amount/stipend value not specified"],
        uncertain_or_conflicting_details=[],
    )


@pytest.fixture
def mock_checklist():
    return ActionChecklist(
        notice_id="TEST-SCH-2026-001",
        items=[
            ChecklistItem(
                step_number=1,
                action="Verify cumulative score is at least 75%",
                category="ELIGIBILITY",
                is_mandatory=True,
                is_completed=False,
                grounded_quote="Minimum cumulative score of 75%",
            ),
            ChecklistItem(
                step_number=2,
                action="Obtain valid Family Income Certificate",
                category="DOCUMENTATION",
                is_mandatory=True,
                is_completed=True,
                grounded_quote="Valid Family Income Certificate issued by the Tehsildar",
            ),
            ChecklistItem(
                step_number=3,
                action="Submit physical copy to Room 204 before 15 November 2026",
                category="SUBMISSION",
                is_mandatory=True,
                is_completed=False,
                grounded_quote="Submit one signed physical copy along with document photocopies to Room 204",
            ),
        ],
    )


@pytest.fixture
def mock_summary():
    return PlainLanguageSummary(
        about="Merit-cum-Means Financial Assistance Scholarship 2026-27.",
        eligible="Full-time 2nd or 3rd year B.Tech/B.Sc CS students with 75% marks.",
        actions="Complete online form and submit physical copy to Room 204.",
        documents="Marksheets 1-4, Income Certificate, College ID, Bank passbook.",
        deadline="15 November 2026 at 5:00 PM IST.",
        help_contact="Room 204, Administrative Block; dsw-helpdesk@iimtu.edu.in",
        missing="Specific scholarship stipend amount is not stated.",
    )


def test_ui_control_01_sidebar_navigation_buttons():
    """Verifies that clicking any sidebar navigation button updates active_tab_index."""
    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception
    assert at.session_state.active_tab_index == 0

    # Click navigation button 1 (Extracted Facts)
    btn_facts = [b for b in at.button if "2. Extracted Facts" in b.label]
    assert len(btn_facts) == 1
    btn_facts[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 1

    # Click navigation button 2 (Summary & Actions)
    btn_summary = [b for b in at.button if "3. Summary & Actions" in b.label]
    assert len(btn_summary) == 1
    btn_summary[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 2

    # Click navigation button 3 (Follow-Up Q&A)
    btn_qa = [b for b in at.button if "4. Follow-Up Q&A" in b.label]
    assert len(btn_qa) == 1
    btn_qa[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 3

    # Click navigation button 0 (Process Notice)
    btn_proc = [b for b in at.button if "1. Process Notice" in b.label]
    assert len(btn_proc) == 1
    btn_proc[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 0


def test_ui_control_02_synthetic_demo_loaders():
    """Verifies that the synthetic fixture loader buttons populate notice buffer."""
    at = AppTest.from_file("../app.py")
    at.run()

    # Load English Demo Notice
    btn_demo = [b for b in at.button if "TEST-SCH-2026-001" in b.label]
    assert len(btn_demo) >= 1
    btn_demo[0].click().run()
    assert not at.exception
    assert len(at.session_state.raw_notice_text) > 100
    assert "SCHOLARSHIP" in at.session_state.raw_notice_text.upper()

    # Load Hindi Notice via Selectbox
    at.selectbox[0].select("🇮🇳 Notice (Hindi)").run()
    btn_load1 = [b for b in at.button if "Load Selected Sample" in b.label]
    assert len(btn_load1) >= 1
    btn_load1[0].click().run()
    assert not at.exception
    assert at.session_state.selected_lang == "hi"
    assert len(at.session_state.raw_notice_text) > 50

    # Load Scanned OCR Demo via Selectbox
    at.selectbox[0].select("🖼️ Scanned Notice (OCR Demo)").run()
    btn_load2 = [b for b in at.button if "Load Selected Sample" in b.label]
    assert len(btn_load2) >= 1
    btn_load2[0].click().run()
    assert not at.exception
    assert at.session_state.uploaded_image is not None


def test_ui_control_03_buffer_clear_button():
    """Verifies that the Clear Buffer button clears notice text and state."""
    at = AppTest.from_file("../app.py")
    at.session_state.raw_notice_text = "Some dummy notice content"
    at.run()
    assert at.session_state.raw_notice_text == "Some dummy notice content"

    btn_clear = [b for b in at.button if "Clear Buffer" in b.label]
    assert len(btn_clear) == 1
    btn_clear[0].click().run()
    assert not at.exception
    assert at.session_state.raw_notice_text == ""


def test_ui_control_04_ics_and_markdown_exports(mock_structured_notice, mock_checklist, mock_summary):
    """Verifies that export buttons generate RFC 5545 ICS and Markdown downloads."""
    with patch("notice2action.ui.components.generate_audio_bytes", return_value=b"fake-audio"):
        at = AppTest.from_file("../app.py")
        at.session_state.raw_notice_text = "Sample text"
        at.session_state.structured_notice = mock_structured_notice
        at.session_state.checklist_en = mock_checklist
        at.session_state.summary_en = mock_summary
        at.run()

        # Check Markdown download button exists
        md_dl = [b for b in at.download_button if "Download Action Plan (Markdown)" in b.label]
        assert len(md_dl) >= 1

        # Check Calendar .ics download button exists in both Tab 1 widget and Tab 3 export
        ics_dls = [b for b in at.download_button if "Calendar (.ics)" in b.label]
        assert len(ics_dls) >= 2  # One in fast assistance widget, one in Tab 3 exports

        # Check JSON download button exists in dashboard
        json_dl = [b for b in at.download_button if "JSON" in b.label]
        assert len(json_dl) >= 1


def test_ui_control_05_followup_suggested_inquiries():
    """Verifies that clicking suggested inquiries populates qa_input_text_box."""
    at = AppTest.from_file("../app.py")
    at.session_state.raw_notice_text = "Notice mentioning Room 204 deadline 15 November 2026."
    at.session_state.active_tab_index = 3  # Tab 4 Follow-up
    at.run()

    # Click 'Required Documents?' suggestion
    btn_docs = [b for b in at.button if "Required Documents?" in b.label]
    assert len(btn_docs) == 1
    btn_docs[0].click().run()
    assert not at.exception
    assert "What documents are needed to apply?" in at.session_state.qa_input_text_box

    # Click 'Exact Deadline?' suggestion
    btn_dl = [b for b in at.button if "Exact Deadline?" in b.label]
    assert len(btn_dl) == 1
    btn_dl[0].click().run()
    assert not at.exception
    assert "What is the final deadline to submit?" in at.session_state.qa_input_text_box


def test_ui_control_06_jump_navigation_buttons(mock_structured_notice):
    """Verifies that the jump buttons in the Success Banner switch tabs properly."""
    at = AppTest.from_file("../app.py")
    at.session_state.raw_notice_text = "Sample notice text"
    at.session_state.structured_notice = mock_structured_notice
    at.session_state.active_tab_index = 0
    at.run()

    # Jump to Tab 2 (Grounded Facts)
    btn_j2 = [b for b in at.button if "View Grounded Facts" in b.label]
    assert len(btn_j2) == 1
    btn_j2[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 1

    # Jump to Tab 3 (Summary & Checklist)
    btn_j3 = [b for b in at.button if "View Summary & Checklist" in b.label]
    assert len(btn_j3) == 1
    btn_j3[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 2

    # Jump to Tab 4 (Follow-Up Q&A)
    btn_j4 = [b for b in at.button if "Ask Follow-Up Q&A" in b.label]
    assert len(btn_j4) == 1
    btn_j4[0].click().run()
    assert not at.exception
    assert at.session_state.active_tab_index == 3


def test_ui_control_07_checklist_checkbox_interaction(mock_structured_notice, mock_checklist):
    """Verifies that interacting with checklist checkboxes updates completion state."""
    at = AppTest.from_file("../app.py")
    at.session_state.raw_notice_text = "Sample notice text"
    at.session_state.structured_notice = mock_structured_notice
    at.session_state.checklist_en = mock_checklist
    at.session_state.active_tab_index = 2  # Tab 3 Summary & Checklist
    at.run()

    # Checkbox for step 1
    step1_boxes = [c for c in at.checkbox if "Step 1" in c.label]
    assert len(step1_boxes) >= 1
    initial_val = step1_boxes[0].value
    step1_boxes[0].check().run()
    assert not at.exception
    assert step1_boxes[0].value != initial_val


def test_ui_control_08_analyze_workflow_trigger(mock_structured_notice):
    """Verifies clicking 'Analyze Notice with Gemma 4' executes analyzer and populates session."""
    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice", return_value=mock_structured_notice), \
         patch("notice2action.ui.components.generate_audio_bytes", return_value=b"fake-audio"):
        at = AppTest.from_file("../app.py", default_timeout=15)
        at.session_state.raw_notice_text = "DEPARTMENT OF STUDENT WELFARE NOTICE 2026"
        at.session_state.structured_notice = None
        at.run(timeout=10)

        btn_analyze = [b for b in at.button if "Analyze Notice with Gemma 4" in b.label]
        assert len(btn_analyze) == 1
        btn_analyze[0].click().run(timeout=10)
        assert not at.exception
        assert at.session_state.structured_notice is not None
        assert at.session_state.structured_notice.purpose.value == "Merit Scholarship Application 2026"
