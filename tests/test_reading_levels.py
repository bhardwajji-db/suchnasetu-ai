"""
Regression Test Suite for Plain Language Summary Reading Levels.
Verifies that Simple, Standard, and Detailed reading levels produce
meaningfully differentiated, grounded content for the same source notice.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
    NOT_STATED_LABEL,
)
from notice2action.summary import generate_deterministic_summary
from notice2action.api.server import app
from notice2action.services.session_store import session_store


def _create_comprehensive_synthetic_notice() -> StructuredNotice:
    """Creates a realistic synthetic notice covering all 6 core and procedural fields."""
    return StructuredNotice(
        issuing_authority=ExtractedFact(
            field_name="issuing_authority",
            value="Department of Higher Education & Technical Training",
            status=CertaintyStatus.STATED,
            evidence_quote="Government of India - Department of Higher Education & Technical Training",
        ),
        notice_reference_number=ExtractedFact(
            field_name="notice_reference_number",
            value="DHETT/SCH/2026/089",
            status=CertaintyStatus.STATED,
            evidence_quote="Ref No: DHETT/SCH/2026/089",
        ),
        notice_date=ExtractedFact(
            field_name="notice_date",
            value="15 October 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="Dated: 15 October 2026",
        ),
        recipient=ExtractedFact(
            field_name="recipient",
            value="All Engineering and Polytechnic Students in Uttar Pradesh",
            status=CertaintyStatus.STATED,
            evidence_quote="To: All Engineering and Polytechnic Students in Uttar Pradesh",
        ),
        main_subject=ExtractedFact(
            field_name="main_subject",
            value="Post-Matric Technical Merit Scholarship Scheme 2026-27",
            status=CertaintyStatus.STATED,
            evidence_quote="Sub: Post-Matric Technical Merit Scholarship Scheme 2026-27",
        ),
        required_action_and_deadline=ExtractedFact(
            field_name="required_action_and_deadline",
            value="Complete online registration and submit physical copy by 30 November 2026, 5:00 PM",
            status=CertaintyStatus.STATED,
            evidence_quote="Action required: Complete online registration and submit physical copy by 30 November 2026, 5:00 PM",
        ),
        purpose=ExtractedFact(
            field_name="purpose",
            value="Provide financial assistance of Rs 50,000 per annum to meritorious STEM students",
            status=CertaintyStatus.STATED,
            evidence_quote="Financial grant of Rs 50,000 per annum for meritorious technical students",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Enrolled B.Tech or Diploma students with minimum 75% marks and family annual income below Rs 4.5 Lakh",
            status=CertaintyStatus.STATED,
            evidence_quote="Eligibility: Minimum 75% aggregate marks and family income under 4.5 LPA",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="Rs. 500 registration fee (exempted for SC/ST and female candidates)",
            status=CertaintyStatus.STATED,
            evidence_quote="Application fee: Rs. 500 (SC/ST and female applicants exempt)",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Step 1: Fill online application form at scholarships.gov.in. Step 2: Pay Rs. 500 fee or upload waiver. Step 3: Submit counter-signed physical dossier to Dean Office Room 102",
            status=CertaintyStatus.STATED,
            evidence_quote="Steps: Fill online form, pay fee or upload waiver, submit hardcopy to Dean Office Room 102",
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Aadhaar card, 10th and 12th marksheets, college bonafide certificate, current semester grade report, and revenue authority income certificate",
            status=CertaintyStatus.STATED,
            evidence_quote="Enclose: Aadhaar card, marksheets, bonafide certificate, and revenue income certificate",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="30 November 2026, 5:00 PM",
            status=CertaintyStatus.STATED,
            evidence_quote="Last date for online submission is 30 November 2026 at 5:00 PM",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="scholarship-helpdesk@dhett.gov.in | Toll-free: 1800-112-233",
            status=CertaintyStatus.STATED,
            evidence_quote="Helpline: scholarship-helpdesk@dhett.gov.in or call 1800-112-233",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Fee Exemption Exception: SC/ST and female candidates are 100% exempt from the Rs. 500 fee. Disqualification Rule: Students availing any other government scholarship are not eligible. Self-attested photocopies must accompany original certificates during verification.",
            status=CertaintyStatus.STATED,
            evidence_quote="Conditions: Fee waiver for SC/ST and female students. No dual scholarship allowed. Self-attested copies mandatory.",
        ),
        missing_information=[
            "Grievance appeal timeline if application is rejected",
            "Minimum attendance threshold required to maintain grant",
        ],
        uncertain_or_conflicting_details=[
            "Whether physical submission is permitted after 5:00 PM if online form was completed on time",
        ],
    )


class TestReadingLevelDifferentiation:
    """Verifies that Simple, Standard, and Detailed produce meaningfully different summaries."""

    def test_all_three_levels_produce_different_content(self):
        notice = _create_comprehensive_synthetic_notice()

        simple = generate_deterministic_summary(notice, reading_level="simple")
        standard = generate_deterministic_summary(notice, reading_level="standard")
        detailed = generate_deterministic_summary(notice, reading_level="detailed")

        # Confirm every field is non-empty
        for field in ("about", "eligible", "actions", "documents", "deadline", "help_contact", "missing"):
            assert getattr(simple, field), f"Simple.{field} must not be empty"
            assert getattr(standard, field), f"Standard.{field} must not be empty"
            assert getattr(detailed, field), f"Detailed.{field} must not be empty"

            # Must NOT be identical across levels
            assert getattr(simple, field) != getattr(standard, field), (
                f"Field '{field}' should differ between Simple and Standard"
            )
            assert getattr(standard, field) != getattr(detailed, field), (
                f"Field '{field}' should differ between Standard and Detailed"
            )
            assert getattr(simple, field) != getattr(detailed, field), (
                f"Field '{field}' should differ between Simple and Detailed"
            )

    def test_detailed_includes_more_relevant_supported_information_than_standard(self):
        """
        Detailed must include specific supported dimensions not present in Standard:
        - Official reference number & date of notice
        - Specific target audience / recipient scope
        - Complete fee / financial cost breakdown
        - Step-by-step submission location & process details
        - Document verification standard (originals + self-attested photocopies)
        - Late submission policy warning
        - Public helpdesk working hours notice
        - Evidence quotes from the source notice
        - Itemized missing information with citizen advisory
        """
        notice = _create_comprehensive_synthetic_notice()
        standard = generate_deterministic_summary(notice, reading_level="standard")
        detailed = generate_deterministic_summary(notice, reading_level="detailed")

        # 1. About: Detailed includes Reference Number, Notice Date, Target Audience, and Evidence Quote
        assert "DHETT/SCH/2026/089" in detailed.about
        assert "15 October 2026" in detailed.about
        assert "Target Recipients" in detailed.about
        assert "[Evidence Quote:" in detailed.about

        # 2. Eligible: Detailed includes mandatory conditions, fee terms, and evidence quote
        assert "Financial Requirements / Application Fee" in detailed.eligible
        assert "Rs. 500" in detailed.eligible
        assert "Mandatory Conditions, Exceptions & Waivers" in detailed.eligible
        assert "Fee Exemption Exception" in detailed.eligible or "exempt" in detailed.eligible.lower()
        assert "No dual scholarship" in detailed.eligible or "dual government scholarship" in detailed.eligible or "not eligible" in detailed.eligible

        # 3. Actions: Detailed includes submission location and procedural directives
        assert "Room 102" in detailed.actions
        assert "Procedural & Submission Directive" in detailed.actions

        # 4. Documents: Detailed includes verification format (originals & self-attested copies)
        assert "self-attested" in detailed.documents.lower()
        assert "originals" in detailed.documents.lower()

        # 5. Deadline: Detailed includes late submission warning and evidence quote
        assert "Late Submission Policy" in detailed.deadline
        assert "30 November 2026" in detailed.deadline

        # 6. Contact: Detailed includes office hours notice and administrative office
        assert "Helpdesk Working Hours" in detailed.help_contact
        assert "Administrative Office" in detailed.help_contact

        # 7. Missing: Detailed includes itemized gap breakdown and actionable citizen advisory
        assert "Omitted Administrative Details" in detailed.missing
        assert "Actionable Citizen Advisory" in detailed.missing
        assert "Grievance appeal timeline" in detailed.missing

        # Detailed should contain substantially more explanatory text overall
        total_std_len = sum(len(getattr(standard, f)) for f in ("about", "eligible", "actions", "documents", "deadline", "help_contact", "missing"))
        total_det_len = sum(len(getattr(detailed, f)) for f in ("about", "eligible", "actions", "documents", "deadline", "help_contact", "missing"))
        assert total_det_len > total_std_len * 1.5, "Detailed summary must provide substantially more comprehensive context"

    def test_standard_includes_more_explanatory_content_than_simple(self):
        """
        Standard provides clear everyday language with moderate detail,
        surpassing Simple's terse bullet-like syntax.
        """
        notice = _create_comprehensive_synthetic_notice()
        simple = generate_deterministic_summary(notice, reading_level="simple")
        standard = generate_deterministic_summary(notice, reading_level="standard")

        # Simple uses beginner-friendly short sentence structures
        assert simple.about.startswith("Topic:")
        assert simple.eligible.startswith("Who can apply:")
        assert simple.actions.startswith("Steps:")
        assert simple.documents.startswith("Bring:")
        assert simple.deadline.startswith("Due date:")
        assert simple.help_contact.startswith("Contact:")

        # Standard uses complete explanatory sentences
        assert "This notice announces" in standard.about
        assert "Eligibility is open to:" in standard.eligible
        assert "Required actions:" in standard.actions
        assert "Required documents:" in standard.documents
        assert "Submission deadline:" in standard.deadline
        assert "Official contact:" in standard.help_contact

        total_smp_len = sum(len(getattr(simple, f)) for f in ("about", "eligible", "actions", "documents", "deadline", "help_contact", "missing"))
        total_std_len = sum(len(getattr(standard, f)) for f in ("about", "eligible", "actions", "documents", "deadline", "help_contact", "missing"))
        assert total_std_len > total_smp_len * 1.25, "Standard summary must provide more explanatory narrative than Simple"

    def test_unstated_fields_handling_across_all_three_levels(self):
        """Verifies that missing/unstated fields are handled gracefully without hallucination."""
        empty_notice = StructuredNotice(
            purpose=ExtractedFact(field_name="purpose", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            eligibility=ExtractedFact(field_name="eligibility", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            deadline=ExtractedFact(field_name="deadline", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            fee_or_cost=ExtractedFact(field_name="fee_or_cost", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            required_documents=ExtractedFact(field_name="required_documents", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            contact_details=ExtractedFact(field_name="contact_details", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            required_actions=ExtractedFact(field_name="required_actions", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            important_conditions=ExtractedFact(field_name="important_conditions", value=NOT_STATED_LABEL, status=CertaintyStatus.NOT_STATED),
            missing_information=[],
            uncertain_or_conflicting_details=[],
        )

        simple = generate_deterministic_summary(empty_notice, reading_level="simple")
        standard = generate_deterministic_summary(empty_notice, reading_level="standard")
        detailed = generate_deterministic_summary(empty_notice, reading_level="detailed")

        # Simple
        assert "Not stated" in simple.about
        assert "No rules stated" in simple.eligible
        assert "No deadline given" in simple.deadline
        assert "No documents needed" in simple.documents

        # Standard
        assert "not explicitly stated" in standard.about
        assert "No specific eligibility requirements" in standard.eligible
        assert "No deadline is mentioned" in standard.deadline

        # Detailed
        assert "Not explicitly stated" in detailed.about
        assert "No participant qualification criteria" in detailed.eligible
        assert "No deadline or closing date is specified" in detailed.deadline
        assert "No specific documents, certificates" in detailed.documents

    def test_confirmed_fact_value_is_reflected_in_all_levels(self):
        """Verifies that user-confirmed corrections are propagated to all reading levels."""
        notice = _create_comprehensive_synthetic_notice()
        # Simulate user confirming a corrected deadline
        notice.deadline.user_confirmed = True
        notice.deadline.confirmed_value = "10 December 2026, 11:59 PM"

        simple = generate_deterministic_summary(notice, reading_level="simple")
        standard = generate_deterministic_summary(notice, reading_level="standard")
        detailed = generate_deterministic_summary(notice, reading_level="detailed")

        assert "10 December 2026" in simple.deadline
        assert "10 December 2026" in standard.deadline
        assert "10 December 2026" in detailed.deadline


    def test_notice_with_exception_is_differentiated_across_levels(self):
        """
        Mandatory regression test: A synthetic notice containing eligibility rules,
        a deadline, a fee, required documents, an application procedure, and an exception
        must produce calibrated outputs where:
        - Simple presents essential facts with easy words and short sentences.
        - Standard covers all important supported information in a clear format (including fee and exception).
        - Detailed explains additional supported conditions, exceptions, and procedural steps.
        """
        notice = _create_comprehensive_synthetic_notice()
        simple = generate_deterministic_summary(notice, reading_level="simple")
        standard = generate_deterministic_summary(notice, reading_level="standard")
        detailed = generate_deterministic_summary(notice, reading_level="detailed")

        # 1. Simple: Essential facts only, short sentences
        assert "Cost: Rs. 500" in simple.eligible
        assert "Who can apply:" in simple.eligible
        assert "Due date: 30 November 2026" in simple.deadline
        assert "Steps:" in simple.actions
        assert len(simple.eligible.split(". ")) <= 4, "Simple should use concise sentence structures"

        # 2. Standard: Complete coverage including fee, exception, and application procedure
        assert "Rs. 500" in standard.eligible
        assert "Fee Exemption Exception" in standard.eligible or "exempt" in standard.eligible.lower()
        assert "Eligibility is open to:" in standard.eligible
        assert "Required actions:" in standard.actions
        assert "Room 102" in standard.actions
        assert "Submission deadline:" in standard.deadline

        # 3. Detailed: Deep explanation of supported conditions, exceptions, steps, and citations
        assert "Comprehensive Eligibility Criteria:" in detailed.eligible
        assert "Mandatory Conditions, Exceptions & Waivers:" in detailed.eligible
        assert "Fee Exemption Exception: SC/ST and female candidates are 100% exempt" in detailed.eligible
        assert "Step-by-Step Action Procedure:" in detailed.actions
        assert "Procedural & Submission Directive:" in detailed.actions
        assert "Submission Format: Ensure originals and valid self-attested photocopies" in detailed.documents
        assert "Late Submission Policy:" in detailed.deadline
        assert "Helpdesk Working Hours:" in detailed.help_contact
        assert "Actionable Citizen Advisory:" in detailed.missing
        assert "[Evidence Quote:" in detailed.about
        assert "[Evidence Quote:" in detailed.eligible
        assert "[Evidence Quote:" in detailed.deadline


class TestReadingLevelAPIEndpoint:
    """Verifies the /api/summary/reading-level endpoint and session cache synchronization."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_api_endpoint_all_three_levels(self, client):
        notice = _create_comprehensive_synthetic_notice()

        for lvl in ("simple", "standard", "detailed"):
            resp = client.post(
                "/api/summary/reading-level",
                json={
                    "structured_notice": notice.model_dump(),
                    "reading_level": lvl,
                    "target_language": "en",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["reading_level"] == lvl
            assert "summary_en" in data
            assert "summary_hi" in data
            assert data["summary_en"]["about"]

    def test_api_endpoint_session_store_synchronization(self, client):
        notice = _create_comprehensive_synthetic_notice()
        session_id = "test_reading_level_session_123"

        # Initialize session in store
        session_store.update_session(session_id, {
            "raw_notice_text": "Sample text",
            "reading_level": "standard",
            "structured_notice": notice.model_dump(),
        })

        # Request detailed summary with session_id
        resp = client.post(
            "/api/summary/reading-level",
            json={
                "structured_notice": notice.model_dump(),
                "reading_level": "detailed",
                "session_id": session_id,
            },
        )
        assert resp.status_code == 200

        # Verify session store was updated
        sess = session_store.get_session(session_id)
        assert sess is not None
        assert sess.reading_level == "detailed"
        assert "Notice Purpose & Directive:" in sess.summary_en["about"]

    def test_api_endpoint_invalid_level_falls_back_to_standard(self, client):
        notice = _create_comprehensive_synthetic_notice()
        resp = client.post(
            "/api/summary/reading-level",
            json={
                "structured_notice": notice.model_dump(),
                "reading_level": "ultra_complex_invalid_level",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["reading_level"] == "standard"

    def test_switching_levels_and_switching_back_preserves_content(self, client):
        """
        Verifies that switching between reading levels and switching back to a previous level
        returns identical and correct content without cache pollution.
        """
        notice = _create_comprehensive_synthetic_notice()
        session_id = "test_level_switch_cycle_session"

        # 1. Fetch Simple
        resp_simple_1 = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "simple", "session_id": session_id},
        )
        assert resp_simple_1.status_code == 200
        data_s1 = resp_simple_1.json()
        simple_about_1 = data_s1["summary_en"]["about"]
        assert simple_about_1.startswith("Topic:")

        # 2. Switch to Detailed
        resp_detailed = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "detailed", "session_id": session_id},
        )
        assert resp_detailed.status_code == 200
        data_d = resp_detailed.json()
        detailed_about = data_d["summary_en"]["about"]
        assert "Notice Purpose & Directive:" in detailed_about
        assert detailed_about != simple_about_1

        # 3. Switch to Standard
        resp_standard = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "standard", "session_id": session_id},
        )
        assert resp_standard.status_code == 200
        data_std = resp_standard.json()
        standard_about = data_std["summary_en"]["about"]
        assert "This notice announces" in standard_about
        assert standard_about != detailed_about
        assert standard_about != simple_about_1

        # 4. Switch back to Simple
        resp_simple_2 = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "simple", "session_id": session_id},
        )
        assert resp_simple_2.status_code == 200
        data_s2 = resp_simple_2.json()
        simple_about_2 = data_s2["summary_en"]["about"]

        # Confirm switching back faithfully restored the original Simple content
        assert simple_about_2 == simple_about_1

    def test_multilingual_translation_preserves_reading_level_differentiation(self, client):
        """
        Verifies that requesting Hindi or regional translations reflects
        the distinct reading levels in the translated output.
        """
        notice = _create_comprehensive_synthetic_notice()

        resp_simple = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "simple", "target_language": "hi"},
        )
        assert resp_simple.status_code == 200
        data_s = resp_simple.json()

        resp_detailed = client.post(
            "/api/summary/reading-level",
            json={"structured_notice": notice.model_dump(), "reading_level": "detailed", "target_language": "hi"},
        )
        assert resp_detailed.status_code == 200
        data_d = resp_detailed.json()

        # Both English and Hindi summaries must differ between Simple and Detailed
        assert data_s["summary_en"]["eligible"] != data_d["summary_en"]["eligible"]
        assert data_s["summary_hi"]["eligible"] != data_d["summary_hi"]["eligible"]
        assert data_s["localized_summary"]["eligible"] != data_d["localized_summary"]["eligible"]
        assert "DHETT/SCH/2026/089" in data_d["summary_hi"]["about"]
        assert "[Evidence Quote:" in data_d["summary_hi"]["about"]
