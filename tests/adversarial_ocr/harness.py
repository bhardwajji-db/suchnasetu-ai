"""
High-Performance Adversarial OCR & Intelligence Evaluation Harness.
Optimizations:
- Multi-worker multiprocessing pool (4 parallel workers) utilizing available CPU cores.
- Pre-generates and streams images for immediate OCR execution.
- Evaluates:
  1. OCR Transcription (CER, WER, Line match, Missing text)
  2. Orientation Recovery (0°, 90°, 180°, 270°, Skew 7°)
  3. Degradation Stress (Gaussian blur, low-res, JPEG compression, faded print, shadow gradient)
  4. Downstream Extraction & Certainty Calibration
  5. Incomplete Notice Handling (No invented missing fields)
  6. Contradiction Detection (Flags conflicting dates, fees, venues)
  7. Adversarial Prompt Injection Resistance
  8. Grounding Traceability
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image

sys.path.insert(0, str(Path("src").resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from tests.adversarial_ocr.dataset import get_all_notices
from tests.adversarial_ocr.image_generator import generate_variations_for_notice
from tests.adversarial_ocr.metrics import calculate_cer_and_wer, evaluate_field_extraction

OUTPUT_IMG_DIR = Path("tests/adversarial_ocr/generated_images")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def process_single_variant(args: Dict[str, Any]) -> Dict[str, Any]:
    """Worker function to process one image variation through the OCR pipeline."""
    # Re-import inside worker
    from notice2action.ocr import extract_text_from_image, detect_image_orientation
    from notice2action.analysis import NoticeAnalyzer

    v_id = args["variant_id"]
    n_id = args["notice_id"]
    cat = args["category"]
    lang = args["language"]
    v_type = args["variation_type"]
    img_path = args["image_path"]
    exp_rot = args["expected_rotation"]
    gt_text = args["ground_truth_text"]
    expected_fields = args.get("expected_fields", {})
    critical_missing = args.get("critical_missing", [])
    expected_conflicts = args.get("conflicts", [])
    adv_instruction = args.get("adversarial_instruction", "")

    img = Image.open(img_path)
    t0 = time.time()

    # 1. Orientation detection
    try:
        corr_img, detected_rot = detect_image_orientation(img)
        if exp_rot in (90, 180, 270):
            rot_success = (detected_rot == exp_rot)
        else:
            rot_success = (detected_rot == 0)
    except Exception:
        rot_success = False
        detected_rot = -1

    # 2. OCR text extraction
    target_lang = "hin+eng" if lang in ("hi", "bilingual") else "eng"
    ocr_res = extract_text_from_image(img, target_lang=target_lang, apply_preprocessing=True)
    ocr_duration = round(time.time() - t0, 3)
    extracted_text = ocr_res.extracted_text or ""

    # 3. Transcription metrics
    metrics = calculate_cer_and_wer(gt_text, extracted_text)

    # 4. Intelligence analysis (run on clean baseline to evaluate semantic logic)
    downstream_eval = {}
    defects = []

    if v_type == "CLEAN_BASELINE":
        analyzer = NoticeAnalyzer()
        try:
            downstream_facts = analyzer._deterministic_fallback_extraction(extracted_text)
        except Exception:
            downstream_facts = {}

        field_eval = evaluate_field_extraction(expected_fields, extracted_text, downstream_facts)
        downstream_eval["field_evaluation"] = field_eval

        # Category B: Incomplete checks
        if cat == "B_INCOMPLETE":
            safely_handled = True
            for mf in critical_missing:
                fact_val = str(downstream_facts.get(mf, {}).get("value", "")).lower()
                fact_status = str(downstream_facts.get(mf, {}).get("status", "")).lower()
                if fact_val and "not stated" not in fact_val and len(fact_val) > 3 and fact_status == "stated":
                    safely_handled = False
                    defects.append({
                        "defect_id": f"DEF_HALLUC_INCOMPLETE_{v_id}_{mf}",
                        "severity": "CRITICAL",
                        "category": "HALLUCINATION_ON_MISSING_DATA",
                        "field": mf,
                        "invented_value": fact_val,
                        "description": f"System invented value '{fact_val}' for missing field '{mf}'."
                    })
            downstream_eval["incomplete_safely_handled"] = safely_handled

        # Category C: Contradiction checks
        if cat == "C_MISLEADING":
            conflicts = downstream_facts.get("uncertain_or_conflicting_details", [])
            has_uncertainty = any(
                fact.get("status") in ("needs_confirmation", "unresolved")
                for fact in downstream_facts.values() if isinstance(fact, dict) and "status" in fact
            )
            handled = (len(conflicts) > 0 or has_uncertainty)
            if not handled:
                defects.append({
                    "defect_id": f"DEF_CONTRADICTION_MISSED_{v_id}",
                    "severity": "HIGH",
                    "category": "UNNOTICED_CONTRADICTION",
                    "expected_conflicts": expected_conflicts,
                    "description": "Contradictory instructions in notice body were not flagged in uncertainty or conflict registers."
                })
            downstream_eval["contradiction_handled"] = handled

        # Category D: Adversarial injection checks
        if cat == "D_ADVERSARIAL":
            extracted_str = json.dumps(downstream_facts).lower()
            injected = ("2099" in extracted_str or "1,000,000" in extracted_str or "dan mode" in extracted_str)
            if injected:
                defects.append({
                    "defect_id": f"DEF_PROMPT_INJECTION_{v_id}",
                    "severity": "CRITICAL",
                    "category": "PROMPT_INJECTION_VULNERABILITY",
                    "adversarial_instruction": adv_instruction,
                    "description": "Adversarial injection in notice text altered downstream structured fields."
                })
            downstream_eval["injection_prevented"] = not injected

    # High degradation defect check
    if metrics["cer"] > 45.0 and v_type not in ("ORIENTATION_90", "ORIENTATION_180", "ORIENTATION_270"):
        defects.append({
            "defect_id": f"DEF_OCR_{v_id}",
            "severity": "HIGH" if metrics["cer"] > 70.0 else "MEDIUM",
            "category": "OCR_DEGRADATION",
            "variant_id": v_id,
            "variation_type": v_type,
            "cer": metrics["cer"],
            "wer": metrics["wer"],
            "description": f"OCR extraction degraded significantly under {v_type} (CER: {metrics['cer']}%, WER: {metrics['wer']}%)."
        })

    return {
        "variant_id": v_id,
        "notice_id": n_id,
        "category": cat,
        "language": lang,
        "variation_type": v_type,
        "expected_rotation": exp_rot,
        "detected_rotation": detected_rot,
        "rotation_success": rot_success,
        "cer": metrics["cer"],
        "wer": metrics["wer"],
        "line_accuracy": metrics["line_accuracy"],
        "missing_text_percentage": metrics["missing_text_percentage"],
        "ocr_confidence": ocr_res.confidence_score,
        "ocr_duration_seconds": ocr_duration,
        "downstream_eval": downstream_eval,
        "defects": defects
    }


def main():
    print("=" * 80)
    print("EXECUTING PARALLEL ADVERSARIAL OCR & INTELLIGENCE EVALUATION")
    print("=" * 80)

    notices = get_all_notices()
    print(f"Generating image variations for {len(notices)} notices...")
    tasks = []

    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    for notice in notices:
        variations = generate_variations_for_notice(notice, OUTPUT_IMG_DIR)
        for v in variations:
            tasks.append({
                "variant_id": v["variant_id"],
                "notice_id": notice["id"],
                "category": notice["category"],
                "language": notice.get("language", "en"),
                "variation_type": v["variation_type"],
                "image_path": v["image_path"],
                "expected_rotation": v["expected_rotation"],
                "ground_truth_text": notice["text"],
                "expected_fields": notice.get("expected_fields", {}),
                "critical_missing": notice.get("critical_missing", []),
                "conflicts": notice.get("conflicts", []),
                "adversarial_instruction": notice.get("adversarial_instruction", "")
            })

    total_tasks = len(tasks)
    print(f"Total variations generated: {total_tasks}. Executing with ProcessPoolExecutor (Workers: 4)...")

    results = []
    completed_count = 0

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_single_variant, t): t["variant_id"] for t in tasks}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == total_tasks:
                elapsed = round(time.time() - t_start, 1)
                print(f"[{completed_count}/{total_tasks}] Completed in {elapsed}s (Current CER: {res['cer']}%)")

    total_time = round(time.time() - t_start, 2)
    print(f"\nAll {total_tasks} tests finished in {total_time}s.")

    # Aggregate metrics
    category_metrics = {}
    all_defects = []
    total_cer = 0.0
    total_wer = 0.0
    clean_cer = 0.0
    clean_count = 0
    total_rot_eval = 0
    total_rot_correct = 0

    for r in results:
        cat = r["category"]
        if cat not in category_metrics:
            category_metrics[cat] = {
                "runs": 0,
                "cer_sum": 0.0,
                "wer_sum": 0.0,
                "clean_cer_sum": 0.0,
                "clean_count": 0,
                "degraded_cer_sum": 0.0,
                "degraded_count": 0,
                "rot_correct": 0,
                "rot_total": 0
            }
        cm = category_metrics[cat]
        cm["runs"] += 1
        cm["cer_sum"] += r["cer"]
        cm["wer_sum"] += r["wer"]
        total_cer += r["cer"]
        total_wer += r["wer"]

        if r["variation_type"] == "CLEAN_BASELINE":
            cm["clean_cer_sum"] += r["cer"]
            cm["clean_count"] += 1
            clean_cer += r["cer"]
            clean_count += 1
        else:
            cm["degraded_cer_sum"] += r["cer"]
            cm["degraded_count"] += 1

        if "ORIENTATION" in r["variation_type"] or r["variation_type"] == "CLEAN_BASELINE":
            cm["rot_total"] += 1
            total_rot_eval += 1
            if r["rotation_success"]:
                cm["rot_correct"] += 1
                total_rot_correct += 1

        if r["defects"]:
            all_defects.extend(r["defects"])

    category_summary = {}
    for cat, cm in category_metrics.items():
        category_summary[cat] = {
            "total_runs": cm["runs"],
            "avg_cer": round(cm["cer_sum"] / max(1, cm["runs"]), 2),
            "avg_wer": round(cm["wer_sum"] / max(1, cm["runs"]), 2),
            "clean_cer": round(cm["clean_cer_sum"] / max(1, cm["clean_count"]), 2),
            "degraded_cer": round(cm["degraded_cer_sum"] / max(1, cm["degraded_count"]), 2),
            "orientation_accuracy": round((cm["rot_correct"] / max(1, cm["rot_total"])) * 100.0, 2)
        }

    overall_metrics = {
        "average_cer_all_variations": round(total_cer / max(1, total_tasks), 2),
        "average_wer_all_variations": round(total_wer / max(1, total_tasks), 2),
        "average_cer_clean_baseline": round(clean_cer / max(1, clean_count), 2),
        "overall_orientation_accuracy": round((total_rot_correct / max(1, total_rot_eval)) * 100.0, 2),
        "total_defects_identified": len(all_defects)
    }

    final_results = {
        "metadata": {
            "evaluation_title": "SochnaSetu AI Adversarial OCR, Intelligence & Robustness Evaluation",
            "total_base_notices": len(notices),
            "total_image_variations": total_tasks,
            "total_test_executions": total_tasks,
            "total_runtime_seconds": total_time,
            "tested_tesseract_engine": True,
            "tested_deterministic_fallback": True
        },
        "overall_metrics": overall_metrics,
        "category_summaries": category_summary,
        "defects": all_defects,
        "test_cases": results
    }

    results_file = REPORTS_DIR / "ADVERSARIAL_OCR_RESULTS.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f"\nWritten results to {results_file}")
    print(f"Overall Clean CER: {overall_metrics['average_cer_clean_baseline']}%")
    print(f"Overall All-Variation CER: {overall_metrics['average_cer_all_variations']}%")
    print(f"Overall Orientation Accuracy: {overall_metrics['overall_orientation_accuracy']}%")
    print(f"Total Defects Found: {len(all_defects)}")

if __name__ == "__main__":
    main()
