"""
Notice Analysis Pipeline for Notice2Action AI.
Guides Gemma 4 to extract structured semantic facts, quotation evidence,
and uncertainty flags, followed by strict deterministic grounding verification.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import json

from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    StructuredNotice,
    NOT_STATED_LABEL,
)
from notice2action.llm.ollama_client import OllamaClient
from notice2action.grounding import verify_structured_notice
from notice2action.security import wrap_untrusted_notice


ANALYSIS_SYSTEM_PROMPT = """You are Notice2Action AI. Extract critical facts into strictly formatted JSON.
Do not include any preamble, thinking, reasoning, or markdown explanations. Output only valid JSON.

RULES:
1. Grounding: Extract facts ONLY from the notice. Never invent dates, fees, rules, or contacts.
2. Missing Info: If unmentioned, set "value" to "Not stated in the notice.", "status" to "not_stated", "evidence_quote" to null.
3. Quotation: For stated facts, provide an exact verbatim quotation ("evidence_quote") from the notice proving the fact.
4. Uncertainty: If tentative or provisional, set "status" to "uncertain" and "requires_confirmation" to true.

Format:
{
  "purpose": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "eligibility": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "deadline": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "fee_or_cost": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "required_documents": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "contact_details": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "required_actions": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "important_conditions": {"value": "...", "status": "stated|not_stated|uncertain", "evidence_quote": "..."},
  "missing_information": [],
  "uncertain_or_conflicting_details": []
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

    return ExtractedFact(
        field_name=field_name,
        value=val if val else NOT_STATED_LABEL,
        status=status,
        evidence_quote=quote_clean,
        requires_confirmation=req_conf or (status in [CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING]),
        explanation=exp_clean,
    )


class NoticeAnalyzer:
    """Orchestrates structured notice analysis using Gemma 4 and grounding checks."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def analyze_notice(self, notice_text: str) -> StructuredNotice:
        """
        Takes raw notice text, queries Gemma 4 for structured extraction,
        and applies deterministic evidence verification.
        """
        wrapped_input = wrap_untrusted_notice(notice_text)
        user_prompt = f"Analyze the following notice text and return structured JSON:\n\n{wrapped_input}"

        raw_json = self.client.generate_structured_json(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        unverified = StructuredNotice(
            purpose=parse_fact_dict("purpose", raw_json.get("purpose")),
            eligibility=parse_fact_dict("eligibility", raw_json.get("eligibility")),
            deadline=parse_fact_dict("deadline", raw_json.get("deadline")),
            fee_or_cost=parse_fact_dict("fee_or_cost", raw_json.get("fee_or_cost")),
            required_documents=parse_fact_dict("required_documents", raw_json.get("required_documents")),
            contact_details=parse_fact_dict("contact_details", raw_json.get("contact_details")),
            required_actions=parse_fact_dict("required_actions", raw_json.get("required_actions")),
            important_conditions=parse_fact_dict("important_conditions", raw_json.get("important_conditions")),
            missing_information=raw_json.get("missing_information", []),
            uncertain_or_conflicting_details=raw_json.get("uncertain_or_conflicting_details", []),
            raw_notice_text=notice_text,
        )

        # Apply evidence grounding verification
        verified = verify_structured_notice(unverified, notice_text)
        return verified
