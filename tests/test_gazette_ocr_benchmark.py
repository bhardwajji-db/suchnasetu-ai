"""
Ground-Truth Benchmark and Regression Suite for Multilingual OCR Accuracy Repair.
Evaluates the 28 April 2017 Gazette of India mixed Hindi-English corrigendum notice (S.O. 1364(E)),
measuring Character Error Rate (CER), Word Error Rate (WER), and Critical Field Exact Match.
Verifies deskewing, rotation recovery, confidence calibration, and downstream fact grounding.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import pytest
import pytesseract

from notice2action.config import config
from notice2action.ocr import (
    extract_text_from_image,
    detect_image_orientation,
    detect_and_correct_skew,
    preprocess_image_for_ocr,
    clean_and_repair_gazette_text,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
GAZETTE_IMG_PATH = FIXTURES_DIR / "gazette_corrigendum_2017.jpeg"
GROUND_TRUTH_JSON_PATH = FIXTURES_DIR / "gazette_corrigendum_2017_ground_truth.json"


def _levenshtein(s1: list | str, s2: list | str) -> int:
    """Computes exact Levenshtein edit distance between sequences."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def _normalize_eval_text(text: str) -> str:
    """Normalizes whitespace and Unicode NFC for deterministic scoring."""
    if not text:
        return ""
    nfc = unicodedata.normalize("NFC", text)
    return " ".join(nfc.split())


def compute_cer(reference: str, hypothesis: str) -> float:
    """Calculates Character Error Rate (CER)."""
    ref = _normalize_eval_text(reference)
    hyp = _normalize_eval_text(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    dist = _levenshtein(ref, hyp)
    return dist / len(ref)


def compute_wer(reference: str, hypothesis: str) -> float:
    """Calculates Word Error Rate (WER)."""
    ref_words = _normalize_eval_text(reference).split()
    hyp_words = _normalize_eval_text(hypothesis).split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dist = _levenshtein(ref_words, hyp_words)
    return dist / len(ref_words)


def run_baseline_ocr(image: Image.Image) -> str:
    """
    Executes the legacy/unimproved OCR pipeline:
    - 1.5x lanczos rescaling
    - Standard autocontrast and 3x3 sharpen
    - Single pass hin+eng without spatial fusion or domain repair
    """
    gray = image.convert("L")
    w, h = gray.size
    if w < 1200:
        gray = gray.resize((int(w * 1.5), int(h * 1.5)), Image.Resampling.LANCZOS)
    stretched = ImageOps.autocontrast(gray, cutoff=1)
    sharpened = stretched.filter(ImageFilter.SHARPEN)

    pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
    return pytesseract.image_to_string(
        sharpened, lang="hin+eng", config=r"--oem 3 --psm 3"
    ).strip()


@pytest.fixture(scope="module")
def gazette_benchmark_data():
    if not GAZETTE_IMG_PATH.is_file():
        pytest.skip(f"Benchmark test image not found at {GAZETTE_IMG_PATH}")
    if not GROUND_TRUTH_JSON_PATH.is_file():
        pytest.skip(f"Ground truth JSON not found at {GROUND_TRUTH_JSON_PATH}")

    with open(GROUND_TRUTH_JSON_PATH, "r", encoding="utf-8") as f:
        gt = json.load(f)

    img = Image.open(GAZETTE_IMG_PATH)
    return img, gt


def test_gazette_2017_baseline_vs_improved_accuracy(gazette_benchmark_data):
    """
    Compares the baseline OCR pipeline against the improved pipeline on the
    actual 28 April 2017 mixed Hindi-English Gazette of India corrigendum.
    Verifies dramatic reduction in CER and WER and high critical-field exact match.
    """
    img, gt = gazette_benchmark_data
    ref_text = gt["ground_truth_full_text"]
    critical_fields = gt["critical_fields"]

    # 1. Run Baseline
    baseline_text = run_baseline_ocr(img)
    baseline_cer = compute_cer(ref_text, baseline_text)
    baseline_wer = compute_wer(ref_text, baseline_text)

    # 2. Run Improved Pipeline
    improved_res = extract_text_from_image(img, target_lang="hin+eng", apply_preprocessing=True)
    improved_text = improved_res.extracted_text
    improved_cer = compute_cer(ref_text, improved_text)
    improved_wer = compute_wer(ref_text, improved_text)

    # 3. Critical Field Accuracy
    baseline_matches = sum(1 for val in critical_fields.values() if val in baseline_text)
    improved_matches = sum(1 for val in critical_fields.values() if val in improved_text)

    total_fields = len(critical_fields)
    baseline_field_acc = (baseline_matches / total_fields) * 100.0
    improved_field_acc = (improved_matches / total_fields) * 100.0

    print("\n" + "=" * 60)
    print("GAZETTE CORRIGENDUM OCR ACCURACY BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Baseline CER:       {baseline_cer * 100:.2f}%  --> Improved CER: {improved_cer * 100:.2f}%")
    print(f"Baseline WER:       {baseline_wer * 100:.2f}%  --> Improved WER: {improved_wer * 100:.2f}%")
    print(f"Baseline Field Acc: {baseline_field_acc:.1f}% ({baseline_matches}/{total_fields}) --> Improved: {improved_field_acc:.1f}% ({improved_matches}/{total_fields})")
    print("=" * 60)

    # Assert significant improvement
    assert improved_cer < baseline_cer, "Improved pipeline must achieve lower Character Error Rate"
    assert improved_wer < baseline_wer, "Improved pipeline must achieve lower Word Error Rate"
    assert improved_field_acc > baseline_field_acc, "Improved pipeline must extract more critical fields"
    assert improved_field_acc >= 85.0, f"Critical field exact match must be >= 85%, got {improved_field_acc:.1f}%"

    # Specific essential fields must be correctly present
    assert "The Gazette of India" in improved_text
    assert "भारत का राजपत्र" in improved_text
    assert "1204" in improved_text
    assert "28 अप्रैल, 2017" in improved_text
    assert "का.आ. 1364(अ)" in improved_text
    assert "का.आ. 19(अ)" in improved_text
    assert "4 जनवरी, 2017" in improved_text
    assert "31 मार्च, 2017" in improved_text
    assert "30 सितंबर, 2017" in improved_text
    assert "अपराजिता सारंगी" in improved_text
    assert "संयुक्त सचिव" in improved_text


def test_synthetic_skew_and_rotation_recovery(gazette_benchmark_data):
    """
    Tests automated skew angle detection and 90-degree orientation correction.
    """
    img, _ = gazette_benchmark_data

    # Test skew detection on tilted image (+3.5 degrees)
    tilted = img.rotate(3.5, expand=False, fillcolor="white")
    deskewed, detected_angle = detect_and_correct_skew(tilted)
    # The counter-rotation should be near -3.5 (within 1.0 degree tolerance)
    assert abs(detected_angle - (-3.5)) <= 1.0, f"Expected skew detection near -3.5 deg, got {detected_angle}"

    # Test 90-degree orientation correction
    rot90 = img.rotate(90, expand=True)
    upright, applied_rot = detect_image_orientation(rot90)
    assert applied_rot == 90, f"Expected 90 degree orientation detection, got {applied_rot}"


def test_confidence_and_document_quality_calibration(gazette_benchmark_data):
    """
    Verifies calibrated document quality scoring, raw text preservation,
    and low-confidence span reporting.
    """
    img, _ = gazette_benchmark_data
    res = extract_text_from_image(img, target_lang="hin+eng", apply_preprocessing=True)

    assert res.confidence_score > 0.0
    assert res.document_quality_score is not None
    assert 0.0 <= res.document_quality_score <= 100.0
    assert res.raw_ocr_text is not None
    assert len(res.raw_ocr_text) > 0
    # Cleaned text distinguishes raw OCR from repaired text
    assert res.extracted_text != res.raw_ocr_text or len(res.extracted_text) > 100
    assert isinstance(res.uncertain_spans, list)


def test_downstream_fact_preservation_and_anti_hallucination(gazette_benchmark_data):
    """
    Verifies that the repaired OCR text contains verified dates and deadlines
    so that downstream grounding and evidence citation cannot hallucinate dates.
    """
    img, _ = gazette_benchmark_data
    res = extract_text_from_image(img, target_lang="hin+eng", apply_preprocessing=True)
    text = res.extracted_text

    # Verify deadlines and dates are strictly present for grounding
    assert "31 मार्च, 2017" in text
    assert "30 सितंबर, 2017" in text
    assert "1 अप्रैल, 2017" in text
    assert "का.आ. 1364(अ)" in text

    # Verify impossible dates do NOT appear in the cleaned text
    assert "34 मार्च" not in text
    assert "30 सितंबर, 2077" not in text
    assert "2047" not in text

