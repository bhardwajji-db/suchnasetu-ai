"""
Notice Analysis Pipeline for SuchnaSetu AI.
Guides the configured LLM (Ollama, OpenRouter, Gemini, or Hugging Face)
to extract structured semantic facts, the Six Core Fields, quotation evidence,
and uncertainty flags, followed by strict deterministic grounding verification.
"""

from __future__ import annotations

import re
import json
import logging
from typing import Dict, Any, Optional, List

from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    StructuredNotice,
    SixCoreFields,
    NOT_STATED_LABEL,
    normalize_string_list,
)
from notice2action.llm.base import (
    BaseLLMClient,
    LLMClientError,
    LLMConnectionError,
    LLMModelError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMConfigError,
    LLMAuthError,
)
from notice2action.llm.factory import get_llm_client
from notice2action.grounding import verify_structured_notice
from notice2action.security import wrap_untrusted_notice

logger = logging.getLogger(__name__)


ANALYSIS_SYSTEM_PROMPT = """You are SuchnaSetu AI. Extract critical facts into strictly formatted JSON. Return ONLY the final JSON object immediately.
Do not include any preamble, thinking, reasoning, or markdown explanations. Output only valid JSON.

RULES:
1. Grounding: Extract facts ONLY from the notice. Never invent dates, fees, rules, or contacts.
2. Missing Info: If unmentioned, set "value" to "Not stated in the notice.", "status" to "not_stated", "evidence_quote" to null.
3. Quotation: For stated facts, provide an exact verbatim quotation ("evidence_quote") from the notice proving the fact.
4. Uncertainty: If tentative, provisional, or ambiguous, set "status" to "uncertain", "requires_confirmation" to true, and specify "uncertainty_type" ("document_ambiguity", "ocr_quality", "missing_in_text", or "conflict").
5. Conciseness: Keep each field "value" and "evidence_quote" concise (under 25 words). Do not repeat the entire notice.

Format:
{
  "issuing_authority": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "notice_reference_number": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "notice_date": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "recipient": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "main_subject": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "required_action_and_deadline": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},

  "purpose": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "eligibility": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "deadline": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "fee_or_cost": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "required_documents": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "contact_details": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "required_actions": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "important_conditions": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "missing_information": ["List of critical aspects missing from the notice, e.g. 'Application fee', 'Selection criteria'"],
  "uncertain_or_conflicting_details": ["List of ambiguous or contradictory details in the notice"]
}"""


def parse_fact_dict(field_name: str, data: Optional[Dict[str, Any]]) -> ExtractedFact:
    """Parses a dictionary into an ExtractedFact with safe fallbacks."""
    if not isinstance(data, dict):
        return ExtractedFact(
            field_name=field_name,
            value=NOT_STATED_LABEL,
            status=CertaintyStatus.NOT_STATED,
            evidence_quote=None,
            requires_confirmation=False,
        )

    val = str(data.get("value", "")).strip()
    status_str = str(data.get("status", "stated")).lower().strip()
    try:
        status = CertaintyStatus(status_str)
    except ValueError:
        status = CertaintyStatus.UNCERTAIN

    quote = data.get("evidence_quote")
    quote_clean = str(quote).strip() if quote else None
    if quote_clean and quote_clean.lower() in ["null", "none", "n/a", ""]:
        quote_clean = None

    req_conf = bool(data.get("requires_confirmation", False))
    explanation = data.get("explanation")
    exp_clean = str(explanation).strip() if explanation else None

    unc_type = data.get("uncertainty_type")
    unc_clean = str(unc_type).strip() if unc_type else None
    if not unc_clean and status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]:
        unc_clean = "document_ambiguity"

    return ExtractedFact(
        field_name=field_name,
        value=val if val else NOT_STATED_LABEL,
        status=status,
        evidence_quote=quote_clean,
        requires_confirmation=req_conf,
        explanation=exp_clean,
        uncertainty_type=unc_clean,
    )


class NoticeAnalyzer:
    """Orchestrates structured notice analysis using the configured LLM and grounding checks."""

    def __init__(self, client: Optional[BaseLLMClient] = None):
        self.client = client or get_llm_client()

    def _deterministic_fallback_extraction(
        self,
        text: str,
        target_lang: str = "en",
        source_lang: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extracts foundational facts using deterministic heuristics when
        the model response fails JSON validation. Guarantees zero blank screen failures.
        Supports both English and Hindi source documents and target explanation languages.
        """
        is_hi_target = (target_lang or "").lower().strip() == "hi"
        not_stated_val = "सूचना में उल्लेख नहीं है।" if is_hi_target else NOT_STATED_LABEL

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        authority = lines[0] if lines else ("सक्षम प्राधिकारी" if is_hi_target else "Official Department")
        if len(lines) > 1 and len(authority) < 40 and not any(k in lines[1].lower() for k in ("ref", "date", "notice", "subject", "संदर्भ", "दिनांक", "पत्रांक", "विषय")):
            authority = f"{authority}, {lines[1]}"

        # Reference number heuristic (bilingual)
        ref_match = re.search(
            r'(?:Reference|Ref\.?|Notice\s+No\.?|Advt\.?\s+No\.?|संदर्भ(?:\s+सं)?|पत्रांक|क्रमांक|विज्ञापन\s+संख्या)\s*[:\-]?\s*([A-Za-z0-9/_.\- ]{4,40})',
            text,
            re.IGNORECASE,
        )
        ref_no = ref_match.group(1).strip() if ref_match else not_stated_val

        # Date heuristic (bilingual)
        date_match = re.search(
            r'(?:Date|Dated|दिनांक|तारीख)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            text,
            re.IGNORECASE,
        )
        notice_date = date_match.group(1).strip() if date_match else not_stated_val

        # Subject heuristic (bilingual)
        subj_match = re.search(
            r'(?:Subject|Sub|Employment\s+Notification|Notification|Circular|विषय|अधिसूचना|विज्ञप्ति)\s*[:\-]?\s*([^\n\r]+)',
            text,
            re.IGNORECASE,
        )
        subject = (
            subj_match.group(1).strip()
            if subj_match
            else (lines[2] if len(lines) > 2 else ("आधिकारिक प्रशासनिक सूचना" if is_hi_target else "Official Administrative Notice"))
        )

        # Contact heuristic (bilingual)
        contact_match = re.search(
            r'(?:Head\s+office|Office|Contact|Website|Email|Phone|हेड\s+ऑफिस|कार्यालय|संपर्क|वेबसाइट|ईमेल|फोन)\s*[:\-]?\s*([^\n\r]+)',
            text,
            re.IGNORECASE,
        )
        contact = contact_match.group(1).strip() if contact_match else not_stated_val

        # Deadline heuristic (bilingual) - prioritize specific submission deadline lines over generic section headers
        dl_match = re.search(
            r'(?:Final\s+submission\s+deadline|Submission\s+deadline|Last\s+date\s+for\s+submission|Final\s+deadline|आवेदन\s+की\s+अंतिम\s+तिथि)\s*[:\-]?\s*([^\n\r,]+)',
            text,
            re.IGNORECASE,
        )
        if not dl_match:
            dl_match = re.search(
                r'(?:Deadline|Last\s+Date|Due\s+Date|Cut-off\s+Date|अंतिम\s+तिथि|अंतिम\s+दिनांक|समाप्ति\s+तिथि)\s*[:\-]?\s*([^\n\r,]+)',
                text,
                re.IGNORECASE,
            )
        deadline_val = dl_match.group(1).strip() if dl_match else not_stated_val

        # Fee heuristic (bilingual)
        fee_match = re.search(
            r'(?:Application\s+Fee|Fee|Cost|शुल्क|आवेदन\s+शुल्क|फीस)\s*[:\-]?\s*([^\n\r,]+)',
            text,
            re.IGNORECASE,
        )
        fee_val = fee_match.group(1).strip() if fee_match else not_stated_val

        # Eligibility heuristic (bilingual)
        elig_match = re.search(
            r'(?:Eligibility|Qualification|पात्रता|शैक्षणिक\s+योग्यता)\s*[:\-]?\s*([^\n\r]+)',
            text,
            re.IGNORECASE,
        )
        if elig_match:
            elig_val = elig_match.group(1).strip()
        else:
            elig_val = (
                "सूचना में उल्लिखित पात्रता शर्तों व न्यूनतम योग्यताओं की जांच करें।"
                if is_hi_target
                else "Review criteria and minimum qualifications stated in the notice body."
            )

        purpose_val = (
            f"प्रशासनिक निर्देश: {subject}"
            if is_hi_target
            else f"Administrative directive concerning: {subject}"
        )
        action_dl_val = (
            "पात्रता शर्तों की जांच करें और अंतिम तिथि से पहले आवेदन जमा करें।"
            if is_hi_target
            else "Review requirements and submit application before cut-off date."
        )
        actions_val = (
            "दस्तावेज़ विवरण सत्यापित करें और निर्धारित आवेदन या अनुपालन चरण पूरा करें।"
            if is_hi_target
            else "Verify document details and submit required application or compliance steps."
        )
        docs_val = (
            "अधिसूचना कार्यक्रम में उल्लिखित प्रमाण पत्र एवं आवश्यक दस्तावेज़।"
            if is_hi_target
            else "Certificates and documents specified in the notification schedule."
        )
        conditions_val = (
            "सभी सूचीबद्ध विनियामक एवं प्रशासनिक दिशानिर्देशों का अनुपालन अनिवार्य है।"
            if is_hi_target
            else "Compliance with all listed regulatory guidelines."
        )
        recipient_val = (
            "नागरिक / संबंधित आवेदक"
            if is_hi_target
            else "Citizens / Intended Applicants"
        )
        missing_info = (
            ["आवेदन की अंतिम तिथि", "आवेदन शुल्क तालिका"]
            if is_hi_target
            else ["Official application deadline", "Application fee schedule"]
        )

        return {
            "issuing_authority": {"value": authority, "status": "stated", "evidence_quote": authority},
            "notice_reference_number": {"value": ref_no, "status": "stated" if ref_no != not_stated_val else "not_stated", "evidence_quote": ref_match.group(0) if ref_match else None},
            "notice_date": {"value": notice_date, "status": "stated" if notice_date != not_stated_val else "not_stated", "evidence_quote": date_match.group(0) if date_match else None},
            "recipient": {"value": recipient_val, "status": "stated", "evidence_quote": None},
            "main_subject": {"value": subject, "status": "stated", "evidence_quote": subj_match.group(0) if subj_match else None},
            "required_action_and_deadline": {"value": action_dl_val, "status": "stated", "evidence_quote": None},
            "purpose": {"value": purpose_val, "status": "stated", "evidence_quote": subj_match.group(0) if subj_match else None},
            "eligibility": {"value": elig_val, "status": "stated", "evidence_quote": elig_match.group(0) if elig_match else None},
            "deadline": {"value": deadline_val, "status": "stated" if deadline_val != not_stated_val else "not_stated", "evidence_quote": dl_match.group(0) if dl_match else None},
            "fee_or_cost": {"value": fee_val, "status": "stated" if fee_val != not_stated_val else "not_stated", "evidence_quote": fee_match.group(0) if fee_match else None},
            "required_documents": {"value": docs_val, "status": "stated", "evidence_quote": None},
            "contact_details": {"value": contact, "status": "stated" if contact != not_stated_val else "not_stated", "evidence_quote": contact_match.group(0) if contact_match else None},
            "required_actions": {"value": actions_val, "status": "stated", "evidence_quote": None},
            "important_conditions": {"value": conditions_val, "status": "stated", "evidence_quote": None},
            "missing_information": missing_info,
            "uncertain_or_conflicting_details": [],
        }

    def analyze_notice(
        self,
        notice_text: str,
        target_lang: str = "en",
        source_lang: Optional[str] = None,
    ) -> StructuredNotice:
        """
        Takes raw notice text, queries the LLM for structured extraction,
        and applies deterministic evidence verification.
        Honors target_lang for explanations/syntheses while strictly preserving
        verbatim evidence quotations in the original source notice text language.
        """
        wrapped_input = wrap_untrusted_notice(notice_text)
        target_lang_clean = (target_lang or "en").lower().strip()
        lang_label = "Hindi" if target_lang_clean == "hi" else ("English" if target_lang_clean == "en" else target_lang_clean)

        system_prompt = ANALYSIS_SYSTEM_PROMPT
        if target_lang_clean != "en":
            system_prompt += (
                f"\n\nOUTPUT EXPLANATION LANGUAGE: {lang_label.upper()} ({target_lang_clean}).\n"
                f"1. You MUST provide all citizen-facing explanations, interpretations, and synthesized field 'value's in {lang_label}.\n"
                f"2. CRITICAL PRESERVATION: Keep all reference numbers, dates, deadlines, monetary amounts, fees, URLs, emails, and phone numbers exact and uncorrupted.\n"
                f"3. VERBATIM SOURCE CITATIONS: The 'evidence_quote' field MUST remain an exact verbatim substring in the ORIGINAL LANGUAGE of the source notice text, matching its original script."
            )

        user_prompt = f"Analyze the following notice text and return structured JSON in {lang_label}:\n\n{wrapped_input}"

        try:
            raw_json = self.client.generate_structured_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except (LLMConnectionError, LLMModelError, LLMTimeoutError, LLMRateLimitError, LLMConfigError, LLMAuthError):
            # Pass operational infrastructure exceptions up to server handlers
            raise
        except Exception as e:
            logger.warning(
                f"Model response JSON parsing failed ({e}). Applying resilient fallback extraction.",
                exc_info=True,
            )
            raw_json = self._deterministic_fallback_extraction(
                notice_text, target_lang=target_lang_clean, source_lang=source_lang
            )

        if not isinstance(raw_json, dict):
            raw_json = self._deterministic_fallback_extraction(
                notice_text, target_lang=target_lang_clean, source_lang=source_lang
            )

        # Parse Six Core Fields
        issuing_authority = parse_fact_dict("issuing_authority", raw_json.get("issuing_authority"))
        notice_reference_number = parse_fact_dict("notice_reference_number", raw_json.get("notice_reference_number"))
        notice_date = parse_fact_dict("notice_date", raw_json.get("notice_date"))
        recipient = parse_fact_dict("recipient", raw_json.get("recipient"))
        main_subject = parse_fact_dict("main_subject", raw_json.get("main_subject"))
        required_action_and_deadline = parse_fact_dict("required_action_and_deadline", raw_json.get("required_action_and_deadline"))

        # Parse Procedural Fields
        purpose = parse_fact_dict("purpose", raw_json.get("purpose"))
        eligibility = parse_fact_dict("eligibility", raw_json.get("eligibility"))
        deadline = parse_fact_dict("deadline", raw_json.get("deadline"))
        fee_or_cost = parse_fact_dict("fee_or_cost", raw_json.get("fee_or_cost"))
        required_documents = parse_fact_dict("required_documents", raw_json.get("required_documents"))
        contact_details = parse_fact_dict("contact_details", raw_json.get("contact_details"))
        required_actions = parse_fact_dict("required_actions", raw_json.get("required_actions"))
        important_conditions = parse_fact_dict("important_conditions", raw_json.get("important_conditions"))

        unverified = StructuredNotice(
            issuing_authority=issuing_authority,
            notice_reference_number=notice_reference_number,
            notice_date=notice_date,
            recipient=recipient,
            main_subject=main_subject,
            required_action_and_deadline=required_action_and_deadline,
            purpose=purpose,
            eligibility=eligibility,
            deadline=deadline,
            fee_or_cost=fee_or_cost,
            required_documents=required_documents,
            contact_details=contact_details,
            required_actions=required_actions,
            important_conditions=important_conditions,
            missing_information=normalize_string_list(raw_json.get("missing_information", [])),
            uncertain_or_conflicting_details=normalize_string_list(raw_json.get("uncertain_or_conflicting_details", [])),
            raw_notice_text=notice_text,
        )

        # Apply evidence grounding verification
        verified = verify_structured_notice(unverified, notice_text)
        return verified
