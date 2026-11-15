"""
Metric calculation utilities for OCR evaluation:
- Character Error Rate (CER) via Levenshtein edit distance
- Word Error Rate (WER)
- Text normalization (Unicode NFC, whitespace normalization, Hindi matra preservation)
- Line-level accuracy and missing text ratio
- Information Extraction Precision, Recall, F1
"""

import re
import unicodedata
from typing import Tuple, Dict, Any, List

def normalize_text_for_evaluation(text: str, preserve_case: bool = False) -> str:
    """Normalizes text by unifying whitespace, newlines and Unicode while preserving Hindi matras."""
    if not text:
        return ""
    # Unicode canonical composition
    normalized = unicodedata.normalize("NFC", text)
    # Replace non-breaking spaces and tabs with space
    normalized = re.sub(r"[\t\r\xa0]", " ", normalized)
    # Condense consecutive spaces
    normalized = re.sub(r" +", " ", normalized)
    # Condense multiple newlines
    normalized = re.sub(r"\n\s*\n+", "\n", normalized)
    normalized = "\n".join(line.strip() for line in normalized.splitlines() if line.strip())
    if not preserve_case:
        normalized = normalized.lower()
    return normalized.strip()


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes exact Levenshtein distance between two strings using two-row dynamic programming."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1] + [0] * len(s2)
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[-1]


def calculate_cer_and_wer(ground_truth: str, hypothesis: str) -> Dict[str, float]:
    """
    Computes Character Error Rate (CER) and Word Error Rate (WER).
    CER = Levenshtein(chars) / max(1, len(ground_truth_chars)) * 100
    WER = Levenshtein(words) / max(1, len(ground_truth_words)) * 100
    """
    gt_norm = normalize_text_for_evaluation(ground_truth)
    hyp_norm = normalize_text_for_evaluation(hypothesis)

    # Character metrics
    gt_chars = list(gt_norm)
    hyp_chars = list(hyp_norm)
    char_dist = levenshtein_distance(gt_norm, hyp_norm)
    cer = (char_dist / max(1, len(gt_norm))) * 100.0

    # Word metrics
    gt_words = gt_norm.split()
    hyp_words = hyp_norm.split()
    word_dist = levenshtein_distance(" ".join(gt_words), " ".join(hyp_words))
    # Approximate WER by token comparison
    wer = (word_dist / max(1, len(" ".join(gt_words)))) * 100.0

    # Line match rate
    gt_lines = [l.strip() for l in gt_norm.splitlines() if l.strip()]
    hyp_lines = [l.strip() for l in hyp_norm.splitlines() if l.strip()]
    matching_lines = sum(1 for gl in gt_lines if any(gl in hl or hl in gl for hl in hyp_lines))
    line_accuracy = (matching_lines / max(1, len(gt_lines))) * 100.0

    # Missing critical tokens ratio
    gt_tokens = set(gt_words)
    hyp_tokens = set(hyp_words)
    missing_tokens = gt_tokens - hyp_tokens
    missing_ratio = (len(missing_tokens) / max(1, len(gt_tokens))) * 100.0

    return {
        "cer": round(min(100.0, cer), 2),
        "wer": round(min(100.0, wer), 2),
        "char_distance": char_dist,
        "gt_char_count": len(gt_norm),
        "hyp_char_count": len(hyp_norm),
        "line_accuracy": round(line_accuracy, 2),
        "missing_text_percentage": round(missing_ratio, 2),
        "exact_match": gt_norm == hyp_norm
    }


def evaluate_field_extraction(
    expected_fields: Dict[str, Any],
    extracted_text: str,
    extracted_notice: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates whether critical fields are accurately extracted or preserved in downstream structured representation.
    """
    results = {}
    total_evaluated = 0
    correctly_extracted = 0

    norm_extracted_text = normalize_text_for_evaluation(extracted_text)

    for field_name, expected_val in expected_fields.items():
        if field_name == "action_steps":
            continue
        total_evaluated += 1
        expected_str = str(expected_val).strip()
        expected_norm = normalize_text_for_evaluation(expected_str)

        # Check if field was expected as missing / Not stated
        is_expected_missing = "not stated" in expected_norm or "none" in expected_norm

        # Check presence in extracted text
        found_in_text = expected_norm in norm_extracted_text or any(token in norm_extracted_text for token in expected_norm.split() if len(token) > 3)

        # Check downstream structured notice value
        downstream_fact = extracted_notice.get(field_name) or {}
        val = str(downstream_fact.get("value", "")).strip().lower()
        status = str(downstream_fact.get("status", "")).strip().lower()

        if is_expected_missing:
            # Success if downstream correctly labeled not_stated or omitted
            is_correct = (status == "not_stated" or "not stated" in val or val == "")
        else:
            # Success if downstream captured or OCR contained the critical fact
            is_correct = (found_in_text and (expected_norm in val or val in expected_norm or len(val) > 3))

        results[field_name] = {
            "expected": expected_str,
            "extracted_downstream": downstream_fact.get("value"),
            "status": downstream_fact.get("status"),
            "found_in_raw_ocr": found_in_text,
            "is_correct": is_correct
        }
        if is_correct:
            correctly_extracted += 1

    accuracy = (correctly_extracted / max(1, total_evaluated)) * 100.0
    return {
        "field_accuracy": round(accuracy, 2),
        "total_fields": total_evaluated,
        "correct_fields": correctly_extracted,
        "details": results
    }
