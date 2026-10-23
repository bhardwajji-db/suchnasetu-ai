"""
Live Integration Test Suite for SuchnaSetu AI with Gemma 4.
Executes against local Ollama running 'gemma4:latest' and Tesseract OCR.
Marked with @pytest.mark.live.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from notice2action.config import config
from notice2action.llm.ollama_client import OllamaClient
from notice2action.analysis import NoticeAnalyzer
from notice2action.summary import generate_accessible_summary
from notice2action.checklist import generate_action_checklist
from notice2action.followup import FollowUpAssistant
from notice2action.schemas import CertaintyStatus
from notice2action.ocr import extract_text_from_image
from PIL import Image

pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def ollama_client():
    client = OllamaClient()
    try:
        health = client.check_health()
    except Exception as e:
        pytest.skip(f"Live Ollama server not reachable at {config.ollama_base_url}: {e}")
    if not health.get("has_target_model"):
        pytest.skip(f"Live target model '{config.ollama_model}' not found in Ollama.")
    return client


def test_live_01_ollama_health(ollama_client):
    """Verifies live Ollama connectivity and target model presence."""
    health = ollama_client.check_health()
    assert health["connected"] is True
    assert health["has_target_model"] is True
    assert config.ollama_model in health["target_model"]


def test_live_02_structured_analysis_scholarship_notice(ollama_client):
    """Tests end-to-end structured analysis of the synthetic scholarship notice using Gemma 4."""
    fixture_path = Path("tests/fixtures/sample_scholarship_notice.txt")
    assert fixture_path.is_file(), "Scholarship fixture missing"
    notice_text = fixture_path.read_text(encoding="utf-8")

    analyzer = NoticeAnalyzer(client=ollama_client)
    structured = analyzer.analyze_notice(notice_text)

    # Assert critical grounded facts
    assert structured.purpose.status == CertaintyStatus.STATED
    assert "scholarship" in structured.purpose.value.lower() or "financial" in structured.purpose.value.lower()
    assert structured.purpose.evidence_quote is not None

    assert structured.deadline.status == CertaintyStatus.STATED
    assert "15 november 2026" in structured.deadline.value.lower()
    assert "15 november 2026" in structured.deadline.evidence_quote.lower()

    assert structured.fee_or_cost.status == CertaintyStatus.STATED
    assert any(term in structured.fee_or_cost.value.lower() for term in ["no", "0", "free"])

    assert structured.contact_details.status == CertaintyStatus.STATED
    assert "dsw" in structured.contact_details.value.lower() or "0121" in structured.contact_details.value


def test_live_03_summary_and_checklist_generation(ollama_client):
    """Tests plain-language summary and grounded checklist generation."""
    fixture_path = Path("tests/fixtures/sample_scholarship_notice.txt")
    notice_text = fixture_path.read_text(encoding="utf-8")

    analyzer = NoticeAnalyzer(client=ollama_client)
    structured = analyzer.analyze_notice(notice_text)

    summary = generate_accessible_summary(structured, client=ollama_client)
    assert len(summary.about) > 0
    assert len(summary.deadline) > 0
    dl_lower = summary.deadline.lower()
    assert "15" in dl_lower and "november" in dl_lower and "2026" in dl_lower

    checklist = generate_action_checklist(structured)
    assert len(checklist.items) >= 4
    # All items should have clean actions
    actions_text = " ".join(item.action for item in checklist.items)
    assert "eligibility" in actions_text.lower() or "document" in actions_text.lower()


def test_live_04_followup_question_supported_and_unsupported(ollama_client):
    """Tests grounded Q&A: both supported queries and truthful reporting of absent info."""
    fixture_path = Path("tests/fixtures/sample_scholarship_notice.txt")
    notice_text = fixture_path.read_text(encoding="utf-8")
    assistant = FollowUpAssistant(client=ollama_client)

    # 1. Supported question
    q_supported = "What is the final deadline to submit?"
    ans_supported = assistant.answer_question(q_supported, notice_text)
    assert ans_supported.is_supported is True
    assert "15 november 2026" in ans_supported.answer.lower()
    assert ans_supported.evidence_quote is not None

    # 2. Deliberately unsupported question (late submission policy)
    q_unsupported = "Can I submit the application late?"
    ans_unsupported = assistant.answer_question(q_unsupported, notice_text)
    assert ans_unsupported.is_supported is False
    assert (
        "does not specify" in ans_unsupported.answer.lower()
        or "not stated" in ans_unsupported.answer.lower()
        or "official contact" in ans_unsupported.answer.lower()
    )


def test_live_05_image_ocr_pipeline():
    """Tests Tesseract OCR on the synthetic image fixture."""
    img_path = Path("tests/fixtures/synthetic_notice_ocr.png")
    assert img_path.is_file(), "OCR test image missing"
    img = Image.open(img_path)

    res = extract_text_from_image(img, target_lang="eng", apply_preprocessing=True)
    assert res.error is None
    assert res.confidence_score > 70.0
    assert "15 NOVEMBER 2026" in res.extracted_text.upper()
    assert "SCHOLARSHIP" in res.extracted_text.upper()
