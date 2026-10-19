"""
Executable Ground-Truth Evaluation Script for Notice2Action AI (PS02).
Executes end-to-end evaluation with live Gemma 4 and Tesseract OCR,
comparing results against independent ground truth JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from notice2action.config import config
from notice2action.analysis import NoticeAnalyzer
from notice2action.ocr import extract_text_from_image
from notice2action.summary import generate_accessible_summary
from notice2action.checklist import generate_action_checklist
from notice2action.evaluator import evaluate_against_ground_truth


def main():
    print("=" * 65)
    print(" Notice2Action AI — Ground-Truth Evaluation Runner (PS02)")
    print(f" LLM: {config.ollama_model} | Ollama: {config.ollama_base_url}")
    print("=" * 65)

    fixtures_dir = PROJECT_ROOT / "tests" / "fixtures"
    txt_path = fixtures_dir / "synthetic_scholarship_notice.txt"
    json_path = fixtures_dir / "synthetic_scholarship_ground_truth.json"
    png_path = fixtures_dir / "synthetic_scholarship_notice.png"

    if not txt_path.is_file() or not json_path.is_file():
        print(f"[ERROR] Fixtures missing in {fixtures_dir}")
        sys.exit(1)

    notice_text = txt_path.read_text(encoding="utf-8")
    with open(json_path, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # 1. Image OCR Evaluation (if image present)
    ocr_text = None
    if png_path.is_file():
        print("\n[1/3] Running Tesseract OCR on synthetic notice image...")
        img = Image.open(png_path)
        ocr_res = extract_text_from_image(img, target_lang="eng")
        ocr_text = ocr_res.extracted_text
        print(f"  OCR Status: {'OK' if not ocr_res.error else 'ERROR'}")
        print(f"  Confidence: {ocr_res.confidence_score}% | Characters: {ocr_res.char_count}")

    # 2. Live Gemma 4 Analysis
    print("\n[2/3] Running live Gemma 4 extraction on synthetic notice text...")
    analyzer = NoticeAnalyzer()
    structured = analyzer.analyze_notice(notice_text)
    summary = generate_accessible_summary(structured, client=analyzer.client)
    checklist = generate_action_checklist(structured)

    print("  Extracted Purpose: ", structured.purpose.value)
    print("  Extracted Deadline:", structured.deadline.value)
    print("  Extracted Documents:", structured.required_documents.value)
    print("  Extracted Contact: ", structured.contact_details.value)
    print("  Extracted Fee:     ", structured.fee_or_cost.value)

    # 3. Independent Evaluation
    print("\n[3/3] Evaluating extracted facts against independent ground truth...")
    report = evaluate_against_ground_truth(
        notice=structured,
        ground_truth=ground_truth,
        ocr_text=ocr_text,
        original_notice_text=notice_text,
    )

    print("\n" + "-" * 65)
    print(f"{'FIELD':<26} | {'STATUS':<7} | {'CRITICAL':<8} | {'NOTES'}")
    print("-" * 65)
    for ev in report.evaluations:
        notes_str = ev.notes if ev.notes else "Matches ground truth"
        crit_str = "YES" if ev.is_critical else "NO"
        print(f"{ev.field_name:<26} | {ev.status:<7} | {crit_str:<8} | {notes_str}")
    print("-" * 65)

    print(f"\nCritical Field Accuracy: {report.critical_field_accuracy_pct}% ({report.critical_field_passed}/{report.critical_field_count})")
    print(f"Field Coverage:          {report.field_coverage_pct}%")
    print(f"Unsupported Claims:      {report.unsupported_facts_count}")
    if report.ocr_word_recall_pct is not None:
        print(f"OCR Word Recall:         {report.ocr_word_recall_pct}%")
    print(f"OVERALL EVALUATION:      {report.overall_status}")
    print("=" * 65)

    # Save machine-readable report
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    out_json = reports_dir / "ps02_evaluation_results.json"

    export_data = {
        "report": report.to_dict(),
        "extracted_structured": structured.model_dump(),
        "summary": summary.model_dump(),
        "checklist": checklist.model_dump(),
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"\nMachine-readable results saved to: {out_json}")

    return report


if __name__ == "__main__":
    main()
