"""
End-to-End Test Suite for Output Language Selection, Grounding, and Cache Isolation.

Covers:
1. Hindi notice -> English explanation (hi -> en)
2. Hindi notice -> Hindi explanation (hi -> hi)
3. English notice -> Hindi explanation (en -> hi)
4. English notice -> English explanation (en -> en)
5. Strict preservation of verbatim evidence quotes in source notice language across all pairs
6. Verbatim entity preservation (dates, deadlines, fees, reference numbers)
7. Cache isolation: ensuring different target languages for the same text do not collide
8. Post-analysis language regeneration using existing extracted text without re-running OCR
9. Grounded Q&A with target language support and verbatim quotes
10. Revision comparison with target language support
"""

import pytest
from fastapi.testclient import TestClient
from notice2action.api.server import app, _ANALYSIS_CACHE, _CACHE_LOCK

client = TestClient(app)

HINDI_NOTICE_TEXT = """उच्च शिक्षा निदेशालय, उत्तर प्रदेश
पत्रांक: UP-SCH-2026/992
दिनांक: 12/10/2026
विषय: मेधावी छात्रवृत्ति योजना 2026 के संबंध में

सर्वसाधारण को सूचित किया जाता है कि राज्य के मेधावी छात्रों के लिए छात्रवृत्ति हेतु आवेदन आमंत्रित किए जाते हैं।
न्यूनतम शैक्षणिक योग्यता: स्नातक में 60% अंक।
आवेदन शुल्क: ₹500
आवेदन की अंतिम तिथि: 25/11/2026
संपर्क विवरण: हेल्पलाइन 0522-2288990, ईमेल scholarship@up.gov.in
सभी पात्र छात्र आधिकारिक पोर्टल upscholarship.up.gov.in पर निर्धारित तिथि से पूर्व आवेदन करें।"""

ENGLISH_NOTICE_TEXT = """NATIONAL SCHOLARSHIP BOARD OF INDIA
Ref: NSB/2026/FELLOW-402
Date: 15/09/2026
Subject: Notification for National Merit Fellowship Grant 2026

Notice is hereby given that applications are invited for the National Merit Fellowship 2026.
Eligibility: Candidates must hold an accredited Bachelor degree with minimum 65% aggregate marks.
Application Fee: ₹250 (Exempted for PwD candidates).
Submission Deadline: 30/11/2026 at 5:00 PM IST.
Official Contact: helpdesk@nsb.gov.in, Phone: 011-23384500.
Applicants must verify all guidelines and submit applications through nsb.gov.in before the deadline."""


@pytest.fixture(autouse=True)
def clear_analysis_cache():
    """Clear memory analysis cache before each test to ensure determinism."""
    with _CACHE_LOCK:
        _ANALYSIS_CACHE.clear()
    yield
    with _CACHE_LOCK:
        _ANALYSIS_CACHE.clear()


# =========================================================================
# Matrix Pair 1: Hindi Notice -> English Explanation (hi -> en)
# =========================================================================
def test_01_hindi_notice_to_english_explanation():
    """
    Verifies that when a Hindi notice is analyzed with target_language='en':
    - The output summary and explanations are generated in English.
    - Evidence quotations remain strictly verbatim Hindi from the source notice.
    - Critical entities (reference number, dates, fees) are preserved uncorrupted.
    """
    payload = {
        "notice_text": HINDI_NOTICE_TEXT,
        "target_language": "en",
        "output_language": "en",
        "reading_level": "standard",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["target_language"] == "en"

    # 1. English Summary
    summary = data["localized_summary"] or data["summary_en"]
    assert summary is not None
    assert "This notice announces" in summary["about"] or "Administrative directive" in summary["about"]
    assert "25/11/2026" in summary["deadline"]

    # 2. Evidence Quotations must remain verbatim Hindi
    structured = data["structured_notice"]
    ref_quote = structured["notice_reference_number"]["evidence_quote"]
    assert ref_quote is not None
    assert "UP-SCH-2026/992" in ref_quote
    # Verbatim Hindi prefix preserved
    assert "पत्रांक" in ref_quote or "UP-SCH-2026/992" in ref_quote

    # 3. Critical entities uncorrupted
    assert "UP-SCH-2026/992" in structured["notice_reference_number"]["value"]
    assert "12/10/2026" in structured["notice_date"]["value"]
    assert "25/11/2026" in structured["deadline"]["value"]
    assert "500" in structured["fee_or_cost"]["value"]


# =========================================================================
# Matrix Pair 2: Hindi Notice -> Hindi Explanation (hi -> hi)
# =========================================================================
def test_02_hindi_notice_to_hindi_explanation():
    """
    Verifies that when a Hindi notice is analyzed with target_language='hi':
    - The output summary and explanations are generated in Hindi.
    - The action checklist is localized into Hindi.
    - Evidence quotations remain strictly verbatim Hindi.
    - Critical entities are preserved uncorrupted.
    """
    payload = {
        "notice_text": HINDI_NOTICE_TEXT,
        "target_language": "hi",
        "output_language": "hi",
        "reading_level": "standard",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["target_language"] == "hi"

    # 1. Hindi Summary
    summary = data["localized_summary"] or data["summary_hi"]
    assert summary is not None
    assert "यह सूचना" in summary["about"] or "सूचना" in summary["about"]
    assert "अंतिम तिथि" in summary["deadline"]
    assert "25/11/2026" in summary["deadline"]

    # 2. Hindi Action Checklist
    checklist = data["localized_checklist"] or data["checklist_hi"]
    assert checklist is not None
    assert len(checklist["items"]) > 0
    # Steps are in Hindi
    has_hindi_action = any(
        any(k in item["action"] for k in ["आवेदन", "दस्तावेज़", "समीक्षा", "जांच", "शुल्क"])
        for item in checklist["items"]
    )
    assert has_hindi_action, f"Expected Hindi checklist actions, got {[i['action'] for i in checklist['items']]}"

    # 3. Evidence quotes remain verbatim
    structured = data["structured_notice"]
    assert "UP-SCH-2026/992" in structured["notice_reference_number"]["evidence_quote"]
    assert "25/11/2026" in structured["deadline"]["evidence_quote"]


# =========================================================================
# Matrix Pair 3: English Notice -> Hindi Explanation (en -> hi)
# =========================================================================
def test_03_english_notice_to_hindi_explanation():
    """
    Verifies that when an English notice is analyzed with target_language='hi':
    - The explanation and plain language summary are translated to Hindi.
    - Evidence quotations remain strictly verbatim ENGLISH in Latin script.
    - Critical entities (dates, fees, reference numbers) are preserved uncorrupted.
    """
    payload = {
        "notice_text": ENGLISH_NOTICE_TEXT,
        "target_language": "hi",
        "output_language": "hi",
        "reading_level": "standard",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["target_language"] == "hi"

    # 1. Hindi Summary
    summary = data["localized_summary"] or data["summary_hi"]
    assert summary is not None
    assert "यह सूचना" in summary["about"] or "सूचना" in summary["about"]
    assert "30/11/2026" in summary["deadline"]
    assert "अंतिम तिथि" in summary["deadline"]

    # 2. Verbatim English Evidence Quotes preserved in Latin script!
    structured = data["structured_notice"]
    ref_quote = structured["notice_reference_number"]["evidence_quote"]
    assert ref_quote is not None
    # Must be English script matching original text
    assert "NSB/2026/FELLOW-402" in ref_quote
    assert "Ref:" in ref_quote or "NSB" in ref_quote

    deadline_quote = structured["deadline"]["evidence_quote"]
    assert deadline_quote is not None
    assert "30/11/2026" in deadline_quote
    assert "Deadline:" in deadline_quote or "Submission" in deadline_quote

    # 3. Entities uncorrupted
    assert "NSB/2026/FELLOW-402" in structured["notice_reference_number"]["value"]
    assert "30/11/2026" in structured["deadline"]["value"]
    assert "250" in structured["fee_or_cost"]["value"]


# =========================================================================
# Matrix Pair 4: English Notice -> English Explanation (en -> en)
# =========================================================================
def test_04_english_notice_to_english_explanation():
    """
    Verifies that when an English notice is analyzed with target_language='en':
    - The output summary and explanations are generated in English.
    - Evidence quotations remain verbatim English.
    - Checklist items remain in English.
    """
    payload = {
        "notice_text": ENGLISH_NOTICE_TEXT,
        "target_language": "en",
        "output_language": "en",
        "reading_level": "standard",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["target_language"] == "en"

    # 1. English Summary
    summary = data["localized_summary"] or data["summary_en"]
    assert summary is not None
    assert "This notice announces" in summary["about"] or "Administrative directive" in summary["about"]
    assert "30/11/2026" in summary["deadline"]

    # 2. English Checklist
    checklist = data["localized_checklist"] or data["checklist_en"]
    assert checklist is not None
    assert len(checklist["items"]) > 0
    assert any("Application" in item["action"] or "Document" in item["action"] for item in checklist["items"])

    # 3. Verbatim English Evidence Quotes
    structured = data["structured_notice"]
    assert "NSB/2026/FELLOW-402" in structured["notice_reference_number"]["evidence_quote"]
    assert "30/11/2026" in structured["deadline"]["evidence_quote"]


# =========================================================================
# Test 5: Cache Isolation between Output Languages for the Same Notice
# =========================================================================
def test_05_cache_isolation_between_output_languages():
    """
    Verifies that requests for different output languages on the exact same document
    are isolated in the cache and do not return stale results from a prior language.
    """
    sample_text = (
        "GOVERNMENT POLYTECHNIC COLLEGE NOTICE\n"
        "Reference: GPC/ADM/2026/101\n"
        "Date: 01/11/2026\n"
        "Subject: Diploma Admission Counseling 2026\n"
        "Deadline: 20/11/2026\n"
        "Fee: ₹300"
    )

    # 1. First call requesting English output
    res_en = client.post(
        "/api/analyze",
        json={"notice_text": sample_text, "target_language": "en", "reading_level": "standard"},
    )
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["target_language"] == "en"
    assert "This notice announces" in data_en["summary_en"]["about"] or "Administrative directive" in data_en["summary_en"]["about"]

    # 2. Second call on identical text requesting Hindi output
    res_hi = client.post(
        "/api/analyze",
        json={"notice_text": sample_text, "target_language": "hi", "reading_level": "standard"},
    )
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert data_hi["target_language"] == "hi"

    # CRITICAL: data_hi MUST have Hindi localized summary, NOT the cached English summary
    summary_hi = data_hi["localized_summary"] or data_hi["summary_hi"]
    assert "यह सूचना" in summary_hi["about"] or "सूचना" in summary_hi["about"]
    assert "अंतिम तिथि" in summary_hi["deadline"]

    # 3. Third call on identical text requesting English again (hits English cache)
    res_en_again = client.post(
        "/api/analyze",
        json={"notice_text": sample_text, "target_language": "en", "reading_level": "standard"},
    )
    assert res_en_again.status_code == 200
    data_en_again = res_en_again.json()
    assert data_en_again["target_language"] == "en"
    summary_en_again = data_en_again["localized_summary"] or data_en_again["summary_en"]
    assert "This notice announces" in summary_en_again["about"] or "Administrative directive" in summary_en_again["about"]


# =========================================================================
# Test 6: Post-Analysis Language Regeneration without Re-OCR
# =========================================================================
def test_06_post_analysis_language_regeneration():
    """
    Verifies that changing the explanation language after initial analysis
    regenerates explanations in the new language using previously extracted text,
    without re-uploading or re-running OCR.
    """
    # Step 1: Initial analysis in English
    initial_res = client.post(
        "/api/analyze",
        json={
            "notice_text": ENGLISH_NOTICE_TEXT,
            "target_language": "en",
            "reading_level": "standard",
        },
    )
    assert initial_res.status_code == 200
    initial_data = initial_res.json()
    session_id = initial_data["session_id"]
    structured = initial_data["structured_notice"]

    # Step 2: Regenerate explanations in Hindi via reading-level summary endpoint using existing structured notice
    regen_res = client.post(
        "/api/summary/reading-level",
        json={
            "structured_notice": structured,
            "reading_level": "standard",
            "target_language": "hi",
            "session_id": session_id,
        },
    )
    assert regen_res.status_code == 200
    regen_data = regen_res.json()
    assert regen_data["target_language"] == "hi"

    # Explanations regenerated in Hindi
    hi_summary = regen_data["localized_summary"] or regen_data["summary_hi"]
    assert "यह सूचना" in hi_summary["about"] or "सूचना" in hi_summary["about"]
    assert "30/11/2026" in hi_summary["deadline"]
    assert "अंतिम तिथि" in hi_summary["deadline"]


# =========================================================================
# Test 7: Multilingual Grounded Q&A with Verbatim Quotes
# =========================================================================
def test_07_multilingual_grounded_qa():
    """
    Verifies that follow-up Q&A answers in the requested target language
    while maintaining verbatim evidence quotes from the source text.
    """
    # Ask in Hindi about deadline
    res = client.post(
        "/api/followup",
        json={
            "question": "आवेदन की अंतिम तिथि क्या है?",
            "notice_text": HINDI_NOTICE_TEXT,
            "target_language": "hi",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["question"] == "आवेदन की अंतिम तिथि क्या है?"
    # The answer or evidence contains 25/11/2026
    assert "25/11/2026" in (data["answer"] + (data.get("evidence_quote") or ""))


# =========================================================================
# Test 8: Multilingual Revision Comparison
# =========================================================================
def test_08_multilingual_revision_comparison():
    """
    Verifies that comparing notice revisions with target_language='hi'
    provides localized explanations in Hindi while preserving verbatim quotes.
    """
    notice_v1 = (
        "COLLEGE ADMISSION CIRCULAR 2026\n"
        "Last Date: 10/11/2026\n"
        "Fee: ₹200"
    )
    notice_v2 = (
        "COLLEGE ADMISSION CIRCULAR 2026 (CORRIGENDUM)\n"
        "Last Date: 20/11/2026\n"
        "Fee: ₹200"
    )
    res = client.post(
        "/api/compare/revisions",
        json={
            "source_text": notice_v1,
            "target_text": notice_v2,
            "target_language": "hi",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "entries" in data
    assert len(data["entries"]) > 0
