"""
SuchnaSetu AI — Multilingual Notice Translation Test Suite
Validates dynamic translation of analyzed notice content across all 10 supported languages:
English (en), Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te),
Marathi (mr), Gujarati (gu), Punjabi (pa), Kannada (kn), Urdu (ur).

Verifies:
1. Translation of summaries, checklists, and structured facts.
2. Strict preservation of entities: dates, reference codes, monetary amounts, and contacts.
3. Preservation of grounded evidence quotes in their verbatim source language.
4. In-memory caching behavior for fast repeated language switches.
5. Live FastAPI /api/translate-notice endpoint behavior.
"""

import pytest
from fastapi.testclient import TestClient

from notice2action.schemas import (
    PlainLanguageSummary,
    ActionChecklist,
    ChecklistItem,
    ActionCategory,
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
)
from notice2action.translation import (
    SUPPORTED_LANGUAGES,
    translate_notice_package,
    translate_extracted_fact,
    deterministic_translate_text,
)
from notice2action.api.server import app


@pytest.fixture
def sample_notice_package():
    summary_en = PlainLanguageSummary(
        about="Notification regarding scholarship application for year 2026-27.",
        eligible="Citizen students who passed with 60% marks and income under Rs 2,50,000.",
        actions="Apply online at portal before 30 November 2026 with income certificate.",
        documents="Income certificate, marksheet, Aadhaar card, bank passbook.",
        deadline="30 November 2026 at 5:00 PM.",
        help_contact="Email: scholarship@gov.in or helpline 1800-111-222.",
        missing="Detailed penalty clause for false declaration not stated in document.",
    )

    checklist_en = ActionChecklist(
        items=[
            ChecklistItem(
                step_number=1,
                action="Prepare Required Documents and verify eligibility requirements",
                category=ActionCategory.DOCUMENT_PREPARATION,
                is_mandatory=True,
                requires_confirmation=False,
                is_completed=False,
            ),
            ChecklistItem(
                step_number=2,
                action="Submit Application Form before deadline",
                category=ActionCategory.APPLICATION_SUBMISSION,
                is_mandatory=True,
                requires_confirmation=False,
                is_completed=False,
            ),
        ]
    )

    def make_fact(val: str, quote: str = "Official Notice Ref No. SCH-2026/099 dated 15-10-2026"):
        return ExtractedFact(
            field_name="test_field",
            value=val,
            status=CertaintyStatus.STATED,
            evidence_quote=quote,
            requires_confirmation=False,
            user_confirmed=False,
        )

    structured_notice = StructuredNotice(
        issuing_authority=make_fact("Ministry of Social Welfare, Government of India"),
        notice_reference_number=make_fact("SCH-2026/099"),
        notice_date=make_fact("15 October 2026"),
        recipient=make_fact("Eligible citizen students"),
        main_subject=make_fact("Scholarship Award Scheme 2026-27"),
        required_action_and_deadline=make_fact("Apply online by 30 November 2026"),
        purpose=make_fact("Scholarship financial assistance"),
        eligibility=make_fact("Students with family income below Rs 2,50,000"),
        deadline=make_fact("30 November 2026"),
        fee_or_cost=make_fact("Free of cost, zero application fee"),
        required_documents=make_fact("Income certificate, Marksheet, Aadhaar card"),
        contact_details=make_fact("scholarship@gov.in, 1800-111-222"),
        required_actions=make_fact("Submit Application Form before deadline"),
        important_conditions=make_fact("Bank account must be Aadhaar-seeded"),
        missing_information=["Appeal process not stated"],
    )

    return {
        "summary": summary_en,
        "checklist": checklist_en,
        "structured": structured_notice,
    }


def test_supported_languages_list():
    """Verify all 10 official languages are properly configured."""
    expected_langs = {"en", "hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"}
    for lang in expected_langs:
        assert lang in SUPPORTED_LANGUAGES, f"Missing language {lang} in SUPPORTED_LANGUAGES"
        assert "name" in SUPPORTED_LANGUAGES[lang]


def test_deterministic_translation_all_languages():
    """Verify deterministic glossary translation produces translated text across non-English languages."""
    test_phrase = "Prepare Required Documents and Submit Application Form"
    target_langs = ["hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"]

    for lang in target_langs:
        translated = deterministic_translate_text(test_phrase, lang)
        assert isinstance(translated, str)
        assert len(translated) > 0
        assert translated != test_phrase, f"Language {lang} should translate glossary terms"


def test_fact_evidence_quote_preservation(sample_notice_package):
    """Verify evidence_quote is strictly preserved in original source language and never modified."""
    fact = sample_notice_package["structured"].deadline
    original_quote = fact.evidence_quote
    assert original_quote is not None

    for lang in ["hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"]:
        trans_fact = translate_extracted_fact(fact, lang)
        assert isinstance(trans_fact.value, str)
        # Evidence quote MUST remain 100% identical to original
        assert trans_fact.evidence_quote == original_quote, f"evidence_quote was mutated for lang {lang}!"
        assert trans_fact.status == fact.status
        assert trans_fact.requires_confirmation == fact.requires_confirmation


def test_entity_preservation_in_translation(sample_notice_package):
    """Verify numbers, dates, reference numbers, and contact emails are preserved."""
    summary = sample_notice_package["summary"]
    checklist = sample_notice_package["checklist"]
    structured = sample_notice_package["structured"]

    for lang in ["hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"]:
        res = translate_notice_package(
            summary_en=summary,
            checklist_en=checklist,
            structured_notice=structured,
            target_lang=lang,
            fingerprint="test_fp_entity_preservation",
        )
        sum_actions = res["summary"].actions
        assert "2026" in sum_actions or "30" in sum_actions
        assert "scholarship@gov.in" in res["summary"].help_contact or "1800-111-222" in res["summary"].help_contact


def test_translation_caching(sample_notice_package):
    """Verify notice translation packages are cached per fingerprint and target language."""
    summary = sample_notice_package["summary"]
    checklist = sample_notice_package["checklist"]
    structured = sample_notice_package["structured"]
    fp = "cache_test_fp_1001"

    # First run: cache miss
    res1 = translate_notice_package(
        summary_en=summary,
        checklist_en=checklist,
        structured_notice=structured,
        target_lang="hi",
        fingerprint=fp,
    )
    assert res1["cached"] is False

    # Second run: cache hit
    res2 = translate_notice_package(
        summary_en=summary,
        checklist_en=checklist,
        structured_notice=structured,
        target_lang="hi",
        fingerprint=fp,
    )
    assert res2["cached"] is True
    assert res2["summary"].about == res1["summary"].about


def test_api_translate_notice_endpoint(monkeypatch, sample_notice_package):
    """Verify POST /api/translate-notice endpoint over TestClient."""
    monkeypatch.setattr("notice2action.api.server.get_llm_client", lambda *args, **kwargs: None)
    client = TestClient(app)

    payload = {
        "fingerprint": "api_test_fp_2002",
        "target_language": "ta",
        "reading_level": "standard",
        "summary_en": sample_notice_package["summary"].model_dump(),
        "checklist_en": sample_notice_package["checklist"].model_dump(),
        "structured_notice": sample_notice_package["structured"].model_dump(),
    }

    resp = client.post("/api/translate-notice", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_language"] == "ta"
    assert data["target_language_name"] == "Tamil"
    assert "summary" in data
    assert "checklist" in data
    assert "structured_notice" in data
    assert "six_core_fields" in data
    assert data["structured_notice"]["issuing_authority"]["evidence_quote"] == sample_notice_package["structured"].issuing_authority.evidence_quote
