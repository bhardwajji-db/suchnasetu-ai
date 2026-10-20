"""
Notice Analysis Pipeline for Notice2Action AI.
Guides the configured LLM (Ollama, OpenRouter, Gemini, or Hugging Face)
to extract structured semantic facts, the Six Core Fields, quotation evidence,
and uncertainty flags, followed by strict deterministic grounding verification.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import json

from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    StructuredNotice,
    SixCoreFields,
    NOT_STATED_LABEL,
    normalize_string_list,
)
from notice2action.llm.base import BaseLLMClient
from notice2action.llm.factory import get_llm_client
from notice2action.grounding import verify_structured_notice
from notice2action.security import wrap_untrusted_notice


ANALYSIS_SYSTEM_PROMPT = """You are Notice2Action AI. Extract critical facts into strictly formatted JSON.
Do not include any preamble, thinking, reasoning, or markdown explanations. Output only valid JSON.

RULES:
1. Grounding: Extract facts ONLY from the notice. Never invent dates, fees, rules, or contacts.
2. Missing Info: If unmentioned, set "value" to "Not stated in the notice.", "status" to "not_stated", "evidence_quote" to null.
3. Quotation: For stated facts, provide an exact verbatim quotation ("evidence_quote") from the notice proving the fact.
4. Uncertainty: If tentative, provisional, or ambiguous, set "status" to "uncertain", "requires_confirmation" to true, and specify "uncertainty_type" ("document_ambiguity", "ocr_quality", "missing_in_text", or "conflict").

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
        requires_confirmation=req_conf or (status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]),
        explanation=exp_clean,
        uncertainty_type=unc_clean,
    )


def _normalize_str_list(items: Any) -> List[str]:
    """Ensures missing_information and uncertain_details are lists of clean strings."""
    return normalize_string_list(items)


class NoticeAnalyzer:
    """Orchestrates structured notice analysis using the configured LLM and grounding checks."""

    def __init__(self, client: Optional[BaseLLMClient] = None):
        self.client = client or get_llm_client()

    def analyze_notice(self, notice_text: str) -> StructuredNotice:
        """
        Takes raw notice text, queries the LLM for structured extraction,
        and applies deterministic evidence verification.
        """
        wrapped_input = wrap_untrusted_notice(notice_text)
        user_prompt = f"Analyze the following notice text and return structured JSON:\n\n{wrapped_input}"

        raw_json = self.client.generate_structured_json(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if not isinstance(raw_json, dict):
            raw_json = {}

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
