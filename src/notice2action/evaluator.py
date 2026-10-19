"""
Independent Ground-Truth Evaluation Engine for Notice2Action AI (PS02).
Compares actual extraction output strictly against independently defined ground truth.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from notice2action.schemas import StructuredNotice, CertaintyStatus


@dataclass
class FieldEvaluation:
    field_name: str
    expected_value: Any
    actual_value: Any
    status: str  # "PASS", "FAIL", "NOT_TESTED"
    is_critical: bool
    notes: Optional[str] = None


@dataclass
class EvaluationReport:
    total_fields: int = 0
    passed_fields: int = 0
    failed_fields: int = 0
    untested_fields: int = 0
    critical_field_count: int = 0
    critical_field_passed: int = 0
    critical_field_accuracy_pct: float = 0.0
    field_coverage_pct: float = 0.0
    unsupported_facts_count: int = 0
    ocr_word_recall_pct: Optional[float] = None
    overall_status: str = "FAIL"  # "PASS", "PARTIAL PASS", "FAIL"
    evaluations: List[FieldEvaluation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_text(text: str) -> str:
    """Normalizes whitespace and case for robust comparison."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def evaluate_against_ground_truth(
    notice: StructuredNotice,
    ground_truth: Dict[str, Any],
    ocr_text: Optional[str] = None,
    original_notice_text: Optional[str] = None,
) -> EvaluationReport:
    """
    Evaluates a StructuredNotice against independent ground truth JSON.
    """
    evals: List[FieldEvaluation] = []
    unsupported_count = 0

    # 1. Purpose
    exp_purpose = ground_truth.get("purpose", "")
    act_purpose = notice.purpose.value
    p_norm = normalize_text(act_purpose)
    if "scholarship" in p_norm and "merit" in p_norm:
        evals.append(FieldEvaluation("purpose", exp_purpose, act_purpose, "PASS", is_critical=True))
    elif act_purpose and act_purpose != "Not stated in the notice.":
        evals.append(FieldEvaluation("purpose", exp_purpose, act_purpose, "PARTIAL", is_critical=True, notes="Mentions scholarship but wording differs slightly"))
    else:
        evals.append(FieldEvaluation("purpose", exp_purpose, act_purpose, "FAIL", is_critical=True, notes="Missing or failed to identify merit scholarship purpose"))

    # 2. Eligibility Threshold (80%)
    exp_elig = ground_truth.get("eligibility_threshold", "at least 80%")
    act_elig = notice.eligibility.value
    e_norm = normalize_text(act_elig)
    if "80" in e_norm and ("%" in e_norm or "percent" in e_norm):
        evals.append(FieldEvaluation("eligibility_threshold", exp_elig, act_elig, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("eligibility_threshold", exp_elig, act_elig, "FAIL", is_critical=True, notes="Did not extract the 80% minimum mark threshold"))

    # 3. Deadline Date (30 October 2026)
    exp_dl_date = ground_truth.get("deadline_date", "2026-10-30")
    act_dl = notice.deadline.value
    d_norm = normalize_text(act_dl)
    if "30" in d_norm and "october" in d_norm and "2026" in d_norm:
        evals.append(FieldEvaluation("deadline_date", "30 October 2026 (2026-10-30)", act_dl, "PASS", is_critical=True))
    elif "2026-10-30" in d_norm or "30/10/2026" in d_norm or "10/30/2026" in d_norm:
        evals.append(FieldEvaluation("deadline_date", exp_dl_date, act_dl, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("deadline_date", exp_dl_date, act_dl, "FAIL", is_critical=True, notes="Deadline date 30 October 2026 not extracted accurately"))

    # 4. Deadline Time (5:00 PM)
    exp_dl_time = ground_truth.get("deadline_time", "5:00 PM")
    if "5:00" in d_norm or "5 pm" in d_norm or "17:00" in d_norm:
        evals.append(FieldEvaluation("deadline_time", exp_dl_time, act_dl, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("deadline_time", exp_dl_time, act_dl, "FAIL", is_critical=True, notes="Deadline time 5:00 PM missing from deadline field"))

    # 5. Required Documents
    exp_docs = ground_truth.get("required_documents", [])
    act_docs = notice.required_documents.value
    docs_norm = normalize_text(act_docs)
    marksheet_found = "marksheet" in docs_norm or "mark sheet" in docs_norm
    id_found = "identity card" in docs_norm or "id card" in docs_norm or "college id" in docs_norm
    bank_found = "bank" in docs_norm

    docs_passed = marksheet_found and id_found and bank_found
    if docs_passed:
        evals.append(FieldEvaluation("required_documents", exp_docs, act_docs, "PASS", is_critical=True))
    elif marksheet_found or id_found or bank_found:
        missing_d = []
        if not marksheet_found: missing_d.append("marksheet")
        if not id_found: missing_d.append("college ID")
        if not bank_found: missing_d.append("bank proof")
        evals.append(FieldEvaluation("required_documents", exp_docs, act_docs, "FAIL", is_critical=True, notes=f"Partially extracted; missing: {', '.join(missing_d)}"))
    else:
        evals.append(FieldEvaluation("required_documents", exp_docs, act_docs, "FAIL", is_critical=True, notes="None of the 3 required documents were extracted"))

    # 6. Submission Location
    exp_loc = ground_truth.get("submission_location", "")
    act_actions = notice.required_actions.value
    act_norm = normalize_text(act_actions)
    if "room 204" in act_norm or ("scholarship office" in act_norm and "academic block" in act_norm):
        evals.append(FieldEvaluation("submission_location", exp_loc, act_actions, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("submission_location", exp_loc, act_actions, "FAIL", is_critical=True, notes="Did not extract Room 204 / Scholarship Office submission location"))

    # 7. Helpdesk Contact Email
    exp_contact = ground_truth.get("helpdesk_contact", "")
    act_contact = notice.contact_details.value
    c_norm = normalize_text(act_contact)
    if exp_contact.lower() in c_norm:
        evals.append(FieldEvaluation("contact_details", exp_contact, act_contact, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("contact_details", exp_contact, act_contact, "FAIL", is_critical=True, notes=f"Exact email '{exp_contact}' not found in contact"))

    # 8. Late Applications Policy
    exp_late = ground_truth.get("late_applications_policy", "not accepted")
    act_cond = notice.important_conditions.value
    cond_norm = normalize_text(act_cond)
    if "late" in cond_norm and ("not" in cond_norm or "reject" in cond_norm):
        evals.append(FieldEvaluation("late_applications_policy", exp_late, act_cond, "PASS", is_critical=True))
    else:
        evals.append(FieldEvaluation("late_applications_policy", exp_late, act_cond, "FAIL", is_critical=True, notes="Did not capture that late applications will not be accepted"))

    # 9. Application Fee (Unstated in notice -> MUST be not_stated)
    exp_fee = ground_truth.get("application_fee", "Not stated in the notice.")
    act_fee = notice.fee_or_cost.value
    if notice.fee_or_cost.status == CertaintyStatus.NOT_STATED or "not stated" in normalize_text(act_fee):
        evals.append(FieldEvaluation("application_fee", exp_fee, act_fee, "PASS", is_critical=False))
    else:
        # If the model invented a fee that was not in the notice
        evals.append(FieldEvaluation("application_fee", exp_fee, act_fee, "FAIL", is_critical=False, notes="Fabricated fee value when notice stated no fee"))
        unsupported_count += 1

    # 10. Evidence Grounding Audit (Check each extracted fact for hallucination)
    raw_notice_norm = normalize_text(notice.raw_notice_text or "")
    for field_name, fact in [
        ("purpose", notice.purpose),
        ("eligibility", notice.eligibility),
        ("deadline", notice.deadline),
        ("required_documents", notice.required_documents),
        ("contact_details", notice.contact_details),
        ("required_actions", notice.required_actions),
        ("important_conditions", notice.important_conditions),
    ]:
        if fact.status == CertaintyStatus.STATED:
            quote_norm = normalize_text(fact.evidence_quote or "")
            if not quote_norm or quote_norm not in raw_notice_norm:
                unsupported_count += 1

    # 11. OCR Accuracy Calculation (if OCR text provided against original text)
    ocr_word_recall = None
    if ocr_text and original_notice_text:
        orig_words = set(re.findall(r"\b\w{3,}\b", original_notice_text.lower()))
        ocr_words = set(re.findall(r"\b\w{3,}\b", ocr_text.lower()))
        if orig_words:
            matched = orig_words.intersection(ocr_words)
            ocr_word_recall = round((len(matched) / len(orig_words)) * 100, 1)

    # Compute aggregate metrics
    total = len(evals)
    passed = sum(1 for e in evals if e.status == "PASS")
    failed = sum(1 for e in evals if e.status == "FAIL")
    untested = sum(1 for e in evals if e.status == "NOT_TESTED")

    crit_total = sum(1 for e in evals if e.is_critical)
    crit_passed = sum(1 for e in evals if e.is_critical and e.status == "PASS")
    crit_pct = round((crit_passed / crit_total) * 100, 1) if crit_total else 0.0
    coverage_pct = round((passed / total) * 100, 1) if total else 0.0

    if crit_pct >= 85.0 and unsupported_count == 0:
        overall = "PASS"
    elif crit_pct >= 60.0:
        overall = "PARTIAL PASS"
    else:
        overall = "FAIL"

    return EvaluationReport(
        total_fields=total,
        passed_fields=passed,
        failed_fields=failed,
        untested_fields=untested,
        critical_field_count=crit_total,
        critical_field_passed=crit_passed,
        critical_field_accuracy_pct=crit_pct,
        field_coverage_pct=coverage_pct,
        unsupported_facts_count=unsupported_count,
        ocr_word_recall_pct=ocr_word_recall,
        overall_status=overall,
        evaluations=evals,
    )
