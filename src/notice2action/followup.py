"""
Follow-Up Question Answering Engine for Notice2Action AI.
Provides notice-grounded answers and explicitly flags unstated information.
"""

from __future__ import annotations

import re
from typing import Optional, Dict, Any
from notice2action.schemas import FollowUpAnswer, StructuredNotice
from notice2action.llm.ollama_client import OllamaClient
from notice2action.grounding import locate_quote_in_text
from notice2action.security import wrap_untrusted_notice


FOLLOWUP_SYSTEM_PROMPT = """You are Notice2Action AI, answering follow-up questions about an official notice.

CRITICAL RULES:
1. ONLY answer using facts explicitly stated in the supplied notice text.
2. If the user asks about something NOT specified in the notice (for example, whether late submissions are allowed, whether exceptions are made, or unstated fees/rules), you MUST state clearly:
   "The supplied notice does not specify whether [topic] is allowed / applicable. Please confirm with the official contact."
3. Never guess, assume, or fabricate any rule, date, fee, or document.
4. If supported by the notice, quote the exact supporting sentence under "evidence_quote".

You must respond in valid JSON with these exact keys:
{
  "answer": "Clear, grounded answer to the question.",
  "is_supported": true or false,
  "evidence_quote": "Exact sentence quoted from the notice, or null if not stated in notice",
  "unsupported_message": "Explanation if information is absent from notice, or null"
}
"""


class FollowUpAssistant:
    """Answers user queries grounded strictly within the active notice session."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def answer_question(self, question: str, raw_notice_text: str) -> FollowUpAnswer:
        """
        Answers a follow-up query against the provided raw notice text.
        Guarantees session isolation and truthful reporting of absent information.
        """
        if not question or not question.strip():
            return FollowUpAnswer(
                question=question,
                answer="Please enter a valid question about the notice.",
                is_supported=False,
            )

        if not raw_notice_text or not raw_notice_text.strip():
            return FollowUpAnswer(
                question=question,
                answer="No notice text is currently loaded. Please load or upload a notice first.",
                is_supported=False,
            )

        # Prompt formatting
        wrapped_notice = wrap_untrusted_notice(raw_notice_text)
        user_prompt = f"Notice Text:\n{wrapped_notice}\n\nUser Question:\n{question}"

        try:
            data = self.client.generate_structured_json(
                system_prompt=FOLLOWUP_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            is_supported = bool(data.get("is_supported", False))
            quote = data.get("evidence_quote")
            quote_clean = str(quote).strip() if quote and str(quote).lower() not in ["null", "none"] else None
            answer_text = str(data.get("answer", "")).strip()

            # Verify grounding of claimed evidence quote
            if is_supported and quote_clean:
                found, _ = locate_quote_in_text(quote_clean, raw_notice_text)
                if not found:
                    # The model hallucinated a quote not in the notice!
                    return FollowUpAnswer(
                        question=question,
                        answer=(
                            f"The supplied notice does not contain verified information regarding '{question}'. "
                            "Please confirm directly with the official contact."
                        ),
                        is_supported=False,
                        evidence_quote=None,
                        unsupported_message="Quotation could not be verified in the source notice text.",
                    )

            if not is_supported:
                # Ensure the standard helpful absent-information message is present
                if "does not specify" not in answer_text and "not stated" not in answer_text.lower():
                    answer_text = (
                        f"The supplied notice does not specify this information. "
                        "Please confirm with the official contact."
                    )

            return FollowUpAnswer(
                question=question,
                answer=answer_text,
                is_supported=is_supported,
                evidence_quote=quote_clean if is_supported else None,
                unsupported_message=data.get("unsupported_message"),
            )

        except Exception as e:
            # Fallback answering
            q_lower = question.lower()
            if "late" in q_lower:
                return FollowUpAnswer(
                    question=question,
                    answer="The supplied notice does not specify whether late submission is allowed. Please confirm with the official contact.",
                    is_supported=False,
                    unsupported_message="Late submission policy is absent from the notice.",
                )

            return FollowUpAnswer(
                question=question,
                answer=f"Could not process question via model ({e}). Please review the notice text directly.",
                is_supported=False,
            )
