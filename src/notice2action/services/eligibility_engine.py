"""
Explainable Applicant Eligibility Engine for SuchnaSetu AI.
Evaluates applicant parameters (Age/DOB, Qualifications, Marks %, Category)
against criteria extracted from administrative notices using deterministic Python logic.
Enforces epistemic honesty: outputs PASS, FAIL, or UNKNOWN with verbatim source citations.
"""

from __future__ import annotations

import re
import datetime
from typing import List, Optional, Tuple, Dict
from notice2action.schemas import (
    StructuredNotice,
    EligibilityCriterion,
    CriterionType,
    ApplicantProfile,
    CriterionEvaluationResult,
    EligibilityAssessment,
    EvaluationStatus,
    CertaintyStatus,
)


class EligibilityEngine:
    """
    Pure Python deterministic eligibility evaluation engine.
    Zero hallucination: only evaluates objective conditions found in notice text.
    """

    def extract_criteria(self, notice: StructuredNotice) -> List[EligibilityCriterion]:
        """
        Parses structured notice eligibility facts and important conditions into
        machine-evaluable criteria.
        """
        criteria: List[EligibilityCriterion] = []
        elig_fact = getattr(notice, "eligibility", None)
        elig_text = elig_fact.value if elig_fact else ""
        quote = getattr(elig_fact, "evidence_quote", "") or elig_text

        if not elig_text or (elig_fact and elig_fact.status == CertaintyStatus.NOT_STATED):
            # No eligibility rules stated in notice
            return [
                EligibilityCriterion(
                    id="crit_general_0",
                    criterion_type=CriterionType.OTHER,
                    description="General Eligibility Requirements",
                    operator="==",
                    threshold_value="Not stated in this notice",
                    evidence_quote="No specific eligibility rules stated in notice.",
                )
            ]

        # 1. Age Limit Criterion
        age_crit = self._extract_age_criterion(elig_text, quote)
        if age_crit:
            criteria.append(age_crit)

        # 2. Percentage / Marks Criterion
        marks_crit = self._extract_marks_criterion(elig_text, quote)
        if marks_crit:
            criteria.append(marks_crit)

        # 3. Qualification / Degree Criterion
        qual_crit = self._extract_qualification_criterion(elig_text, quote)
        if qual_crit:
            criteria.append(qual_crit)

        # If no specific criteria were matched by regex, create a single descriptive criterion
        if not criteria:
            criteria.append(
                EligibilityCriterion(
                    id="crit_text_0",
                    criterion_type=CriterionType.OTHER,
                    description=elig_text[:200],
                    operator="CONTAINS",
                    threshold_value=elig_text[:100],
                    evidence_quote=quote[:300],
                )
            )

        return criteria

    def evaluate_profile(
        self,
        criteria: List[EligibilityCriterion],
        profile: ApplicantProfile,
        session_id: Optional[str] = None,
    ) -> EligibilityAssessment:
        """
        Deterministically evaluates an ApplicantProfile against extracted notice criteria.
        """
        results: List[CriterionEvaluationResult] = []
        has_fail = False
        has_unknown = False

        for crit in criteria:
            if crit.criterion_type == CriterionType.AGE:
                res = self._evaluate_age(crit, profile)
            elif crit.criterion_type == CriterionType.PERCENTAGE:
                res = self._evaluate_marks(crit, profile)
            elif crit.criterion_type == CriterionType.QUALIFICATION:
                res = self._evaluate_qualification(crit, profile)
            else:
                # Other/General criteria
                res = CriterionEvaluationResult(
                    criterion_id=crit.id,
                    criterion_type=crit.criterion_type,
                    description=crit.description,
                    status=EvaluationStatus.UNKNOWN,
                    applicant_value=profile.notes or "Not evaluated",
                    requirement_value=crit.threshold_value,
                    evidence_quote=crit.evidence_quote,
                    explanation="General or qualitative requirement. Manual verification with official notice advised.",
                    missing_info="Manual verification needed",
                )

            if res.status == EvaluationStatus.FAIL:
                has_fail = True
            elif res.status == EvaluationStatus.UNKNOWN:
                has_unknown = True

            results.append(res)

        # Determine overall status
        if has_fail:
            overall = "NOT_ELIGIBLE"
            summary = "One or more mandatory eligibility criteria were not satisfied."
        elif has_unknown:
            overall = "INCONCLUSIVE"
            summary = "Certain criteria could not be evaluated due to missing applicant information or ambiguous notice terms."
        else:
            overall = "ELIGIBLE"
            summary = "All evaluated eligibility criteria appear to be satisfied based on available documentation."

        return EligibilityAssessment(
            session_id=session_id,
            overall_status=overall,
            results=results,
            summary=summary,
        )

    # -------------------------------------------------------------
    # Extraction Helpers
    # -------------------------------------------------------------

    def _extract_age_criterion(self, text: str, quote: str) -> Optional[EligibilityCriterion]:
        # Match "not exceed 25 years", "maximum 28 years", "between 18 and 25 years"
        m_range = re.search(r"(\d{2})\s*(?:to|-|and)\s*(\d{2})\s*years", text, re.IGNORECASE)
        m_max = re.search(r"(?:maximum|not\s+exceed|under|upto|up\s+to|age\s+limit\s*(?:is|:)?)\s*(\d{2})\s*years", text, re.IGNORECASE)

        if not m_range and not m_max:
            return None

        # Check for cutoff date: "as on 01-08-2026", "as of 15.02.2026"
        cutoff_m = re.search(r"as\s+(?:on|of)\s+([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})", text, re.IGNORECASE)
        cutoff_date = cutoff_m.group(1) if cutoff_m else None

        # Check category relaxations: "3 years for OBC", "5 years for SC/ST"
        relaxations: Dict[str, str] = {}
        if re.search(r"3\s*years.*OBC", text, re.IGNORECASE):
            relaxations["OBC"] = "3"
        if re.search(r"5\s*years.*(?:SC|ST)", text, re.IGNORECASE):
            relaxations["SC"] = "5"
            relaxations["ST"] = "5"

        threshold = m_max.group(1) if m_max else (m_range.group(2) if m_range else "25")

        desc = f"Maximum age limit: {threshold} years"
        if cutoff_date:
            desc += f" as of {cutoff_date}"
        if relaxations:
            desc += " (Relaxations applicable for reserved categories)"

        return EligibilityCriterion(
            id="crit_age_1",
            criterion_type=CriterionType.AGE,
            description=desc,
            operator="<=",
            threshold_value=threshold,
            cutoff_date=cutoff_date,
            category_relaxations=relaxations,
            evidence_quote=quote,
        )

    def _extract_marks_criterion(self, text: str, quote: str) -> Optional[EligibilityCriterion]:
        # Match "minimum 60% marks", "at least 65%", "60% aggregate"
        m = re.search(r"(?:minimum|at\s+least|with)?\s*(\d{2}(?:\.\d+)?)\s*%\s*(?:marks|aggregate)?", text, re.IGNORECASE)
        if not m:
            return None

        min_pct = m.group(1)
        relaxations: Dict[str, str] = {}

        # Look for category relaxations e.g. "55% for SC/ST", "60% for OBC"
        rev_m = re.findall(r"(\d{2}(?:\.\d+)?)\s*%\s*for\s*(OBC|SC|ST)", text, re.IGNORECASE)
        for pct_val, cat in rev_m:
            relaxations[cat.upper()] = pct_val

        desc = f"Minimum qualifying percentage: {min_pct}%"
        if relaxations:
            desc += f" (Relaxed quotas: {', '.join(f'{k}: {v}%' for k, v in relaxations.items())})"

        return EligibilityCriterion(
            id="crit_marks_1",
            criterion_type=CriterionType.PERCENTAGE,
            description=desc,
            operator=">=",
            threshold_value=min_pct,
            category_relaxations=relaxations,
            evidence_quote=quote,
        )

    def _extract_qualification_criterion(self, text: str, quote: str) -> Optional[EligibilityCriterion]:
        # Look for typical educational degrees
        degrees = [
            "Bachelor's Degree", "Bachelor", "Master's Degree", "Master",
            "B.Sc", "B.Tech", "B.E", "B.Com", "B.A", "M.Sc", "M.Tech", "MBA",
            "12th", "Intermediate", "10th", "Matriculation", "Diploma",
        ]
        found = []
        for deg in degrees:
            if re.search(r"\b" + re.escape(deg) + r"\b", text, re.IGNORECASE):
                found.append(deg)

        if not found:
            return None

        clean_found = list(dict.fromkeys(found))
        desc = f"Essential Qualification: {', '.join(clean_found)}"
        return EligibilityCriterion(
            id="crit_qual_1",
            criterion_type=CriterionType.QUALIFICATION,
            description=desc,
            operator="IN",
            threshold_value=", ".join(clean_found),
            evidence_quote=quote,
        )

    # -------------------------------------------------------------
    # Deterministic Evaluators
    # -------------------------------------------------------------

    def _evaluate_age(
        self,
        crit: EligibilityCriterion,
        profile: ApplicantProfile,
    ) -> CriterionEvaluationResult:
        # Determine candidate age
        candidate_age: Optional[float] = None

        if profile.date_of_birth:
            candidate_age = self._calculate_age_from_dob(profile.date_of_birth, crit.cutoff_date)
        elif profile.age_years is not None:
            candidate_age = profile.age_years

        if candidate_age is None:
            return CriterionEvaluationResult(
                criterion_id=crit.id,
                criterion_type=crit.criterion_type,
                description=crit.description,
                status=EvaluationStatus.UNKNOWN,
                applicant_value="Not provided",
                requirement_value=f"<= {crit.threshold_value} years",
                evidence_quote=crit.evidence_quote,
                explanation="Applicant date of birth or age was not provided.",
                missing_info="Date of Birth / Age required",
            )

        # Calculate applicable age limit taking category relaxation into account
        base_limit = float(crit.threshold_value)
        cat = (profile.category or "General").upper()
        relaxation_years = 0.0

        if cat in crit.category_relaxations:
            try:
                relaxation_years = float(crit.category_relaxations[cat])
            except ValueError:
                pass

        effective_limit = base_limit + relaxation_years

        if candidate_age <= effective_limit:
            status = EvaluationStatus.PASS
            reason = (
                f"Candidate age ({candidate_age:.1f} years) satisfies the maximum limit of "
                f"{effective_limit:.0f} years"
            )
            if relaxation_years > 0:
                reason += f" (including {relaxation_years:.0f}-year {cat} category relaxation)."
            else:
                reason += "."
        else:
            status = EvaluationStatus.FAIL
            reason = (
                f"Candidate age ({candidate_age:.1f} years) exceeds the maximum allowed age of "
                f"{effective_limit:.0f} years."
            )

        return CriterionEvaluationResult(
            criterion_id=crit.id,
            criterion_type=crit.criterion_type,
            description=crit.description,
            status=status,
            applicant_value=f"{candidate_age:.1f} years (Category: {cat})",
            requirement_value=f"<= {effective_limit:.0f} years",
            evidence_quote=crit.evidence_quote,
            explanation=reason,
        )

    def _evaluate_marks(
        self,
        crit: EligibilityCriterion,
        profile: ApplicantProfile,
    ) -> CriterionEvaluationResult:
        if profile.marks_percentage is None:
            return CriterionEvaluationResult(
                criterion_id=crit.id,
                criterion_type=crit.criterion_type,
                description=crit.description,
                status=EvaluationStatus.UNKNOWN,
                applicant_value="Not provided",
                requirement_value=f">= {crit.threshold_value}%",
                evidence_quote=crit.evidence_quote,
                explanation="Applicant marks percentage was not provided.",
                missing_info="Marks percentage required",
            )

        candidate_pct = profile.marks_percentage
        cat = (profile.category or "General").upper()

        # Check for category-specific percentage requirement
        effective_min = float(crit.threshold_value)
        if cat in crit.category_relaxations:
            try:
                effective_min = float(crit.category_relaxations[cat])
            except ValueError:
                pass

        # Strict comparison: never round up 59.9 to 60.0
        if candidate_pct >= effective_min:
            status = EvaluationStatus.PASS
            reason = f"Candidate score of {candidate_pct:.1f}% satisfies the minimum requirement of {effective_min:.1f}%."
        else:
            status = EvaluationStatus.FAIL
            reason = f"Candidate score of {candidate_pct:.1f}% does not meet the minimum required threshold of {effective_min:.1f}%."

        return CriterionEvaluationResult(
            criterion_id=crit.id,
            criterion_type=crit.criterion_type,
            description=crit.description,
            status=status,
            applicant_value=f"{candidate_pct:.1f}% (Category: {cat})",
            requirement_value=f">= {effective_min:.1f}%",
            evidence_quote=crit.evidence_quote,
            explanation=reason,
        )

    def _evaluate_qualification(
        self,
        crit: EligibilityCriterion,
        profile: ApplicantProfile,
    ) -> CriterionEvaluationResult:
        if not profile.degree or not profile.degree.strip():
            return CriterionEvaluationResult(
                criterion_id=crit.id,
                criterion_type=crit.criterion_type,
                description=crit.description,
                status=EvaluationStatus.UNKNOWN,
                applicant_value="Not provided",
                requirement_value=crit.threshold_value,
                evidence_quote=crit.evidence_quote,
                explanation="Applicant qualification or degree was not specified.",
                missing_info="Degree / Qualification required",
            )

        cand_deg = profile.degree.strip().lower()
        req_degrees = [d.strip().lower() for d in crit.threshold_value.split(",")]

        # Match check
        matched = any(
            req in cand_deg or cand_deg in req
            for req in req_degrees
        )

        if matched:
            status = EvaluationStatus.PASS
            reason = f"Applicant's degree '{profile.degree}' satisfies documented requirement."
        else:
            status = EvaluationStatus.FAIL
            reason = f"Applicant's degree '{profile.degree}' does not match required qualification: {crit.threshold_value}."

        return CriterionEvaluationResult(
            criterion_id=crit.id,
            criterion_type=crit.criterion_type,
            description=crit.description,
            status=status,
            applicant_value=profile.degree,
            requirement_value=crit.threshold_value,
            evidence_quote=crit.evidence_quote,
            explanation=reason,
        )

    def _calculate_age_from_dob(self, dob_str: str, cutoff_str: Optional[str] = None) -> Optional[float]:
        """Calculates age in decimal years as of cutoff date (or today)."""
        try:
            # Parse DOB
            dob = datetime.date.fromisoformat(dob_str.strip())
            # Parse Cutoff
            if cutoff_str:
                clean_cutoff = cutoff_str.strip().replace("/", "-").replace(".", "-")
                parts = clean_cutoff.split("-")
                if len(parts) == 3:
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        cutoff = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                    else:  # DD-MM-YYYY
                        cutoff = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    cutoff = datetime.date.today()
            else:
                cutoff = datetime.date.today()

            days = (cutoff - dob).days
            if days < 0:
                return 0.0
            return days / 365.25
        except Exception:
            return None


eligibility_engine = EligibilityEngine()
