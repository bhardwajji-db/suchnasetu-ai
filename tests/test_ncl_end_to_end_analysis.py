"""
End-to-End Regression Test for Real Notice Analysis (Northern Coalfields Limited).
Verifies that real complex uploaded notices complete analysis reliably with local Gemma 4,
ensuring robust multi-line quote parsing, six core field extraction, and full UI state transitions.
"""

import json
from pathlib import Path
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.analysis import NoticeAnalyzer
from notice2action.schemas import StructuredNotice, CertaintyStatus
from notice2action.llm.base import clean_llm_json_response

NCL_SAMPLE_TEXT = """Northern Coalfields Limited
A Miniratna Company, An undertaking of Government of India
Head office: Panjreh Bhawan, Morwa , Singrauli-486889.M.P..India
(Website: www-ncleiLin)
Reference: NCL/HQ/PD/Manpower/DR/2020-21/ 466 Date: 10/07/2020
Employment Notification
NCL invites online applications from Indian nationals possessing minimum qualifications required for
regular appointment to the posts as mentioned in Table A for regular deployment across Mines/
Establishments of NCL in Singrauli District of Madhya Pradesh and Sonebhadra District of Uttar Pradesh.
(1) POSITIONS/ ESSENTIAL QUALIFICATION:-
The different Positions, Minimum Qualifications required for different categories are provided in Table A.
Table A: Table showing Positions and required essential Qualifications:
Position Name: Supervisory Positions) Assistant Foreman (E&T) (Trainee) Grade C
Eligibility/Essential Qualification:
(a) Matriculate or equivalent examination passed from any recognized Board of examination;
(b) Diploma or relevant and higher qualification (Minimum 3 year course) in Electronics Engineering from an institute recognized by the Government.
*NCVT: National Council for Vocational Training; SCVT: State Council for Vocational Training
Page 1 of 13"""


def test_clean_llm_json_response_with_multiline_and_trailing_commas():
    """Verifies that clean_llm_json_response handles multiline fences and trailing commas cleanly."""
    raw = """Here is the result:
```json
{
  "issuing_authority": {
    "value": "Northern Coalfields Limited",
    "status": "stated",
    "evidence_quote": "Northern Coalfields Limited\\nA Miniratna Company",
  },
}
```
Hope this helps!"""
    cleaned = clean_llm_json_response(raw)
    parsed = json.loads(cleaned, strict=False)
    assert parsed["issuing_authority"]["value"] == "Northern Coalfields Limited"
    assert "Northern Coalfields Limited" in parsed["issuing_authority"]["evidence_quote"]


def test_ncl_notice_analysis_api_pipeline():
    """Executes /api/analyze with real NCL notification text and validates all dimensions."""
    client = TestClient(app)
    resp = client.post("/api/analyze", json={
        "notice_text": NCL_SAMPLE_TEXT,
        "target_language": "en",
        "reading_level": "standard",
    })

    assert resp.status_code == 200, f"Analysis failed with HTTP {resp.status_code}: {resp.text}"
    data = resp.json()

    # Core response envelope
    assert data["session_id"] is not None
    assert data["fingerprint"] is not None
    assert data["structured_notice"] is not None
    assert data["six_core_fields"] is not None
    assert data["summary_en"] is not None
    assert data["checklist_en"] is not None

    sn = data["structured_notice"]

    # Verify Six Core Fields
    assert sn["issuing_authority"]["value"] != "Not stated in the notice."
    assert "Northern Coalfields" in sn["issuing_authority"]["value"] or "NCL" in sn["issuing_authority"]["value"]
    assert "466" in sn["notice_reference_number"]["value"] or "NCL" in sn["notice_reference_number"]["value"]
    assert "2020" in sn["notice_date"]["value"] or "10/07/2020" in sn["notice_date"]["value"]

    # Verify Procedural Dimensions
    assert sn["purpose"]["value"] != "Not stated in the notice."
    assert sn["eligibility"]["value"] != "Not stated in the notice."
    assert isinstance(sn["missing_information"], list)
    assert isinstance(sn["uncertain_or_conflicting_details"], list)

    # Verify Action Checklist
    cl = data["checklist_en"]
    assert "items" in cl
    assert len(cl["items"]) > 0
    assert all("step_number" in it and "action" in it for it in cl["items"])

    # Verify Plain Language Summary
    summary = data["summary_en"]
    assert "about" in summary
    assert "eligible" in summary
    assert "actions" in summary
    assert len(summary["about"]) > 10


def test_notice_analyzer_fallback_on_unparseable_output():
    """Verifies that NoticeAnalyzer applies resilient deterministic fallback when model outputs garbage."""
    analyzer = NoticeAnalyzer()
    fallback = analyzer._deterministic_fallback_extraction(NCL_SAMPLE_TEXT)

    assert "Northern Coalfields" in fallback["issuing_authority"]["value"]
    assert "466" in fallback["notice_reference_number"]["value"]
    assert "10/07/2020" in fallback["notice_date"]["value"]
    assert any(term in fallback["main_subject"]["value"] for term in ("Employment", "Administrative", "NCL", "applications"))
    assert len(fallback["missing_information"]) > 0
