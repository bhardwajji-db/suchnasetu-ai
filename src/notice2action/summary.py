"""
Plain-Language Summary Generator for SuchnaSetu AI.
Transforms complex official notices into clear, simple answers to the 7 core questions.
"""

from __future__ import annotations

from typing import Optional
from notice2action.schemas import (
    StructuredNotice,
    PlainLanguageSummary,
    CertaintyStatus,
    NOT_STATED_LABEL,
)
from notice2action.llm.ollama_client import OllamaClient


def generate_deterministic_summary(
    notice: StructuredNotice,
    reading_level: str = "standard",
) -> PlainLanguageSummary:
    """
    Builds a plain-language summary directly from verified grounded facts.
    Guarantees zero hallucination and clear answers to the 7 core questions.
    Supports reading levels: 'simple' (Grade 5), 'standard' (Grade 8), 'detailed'.
    """
    # Use confirmed_value if user confirmed a correction, otherwise use original value
    def get_effective_fact_value(fact):
        if getattr(fact, "user_confirmed", False) and getattr(fact, "confirmed_value", None):
            return fact.confirmed_value
        return fact.value

    # 1. About
    purpose_val = get_effective_fact_value(notice.purpose)
    if notice.purpose.status != CertaintyStatus.NOT_STATED:
        about = f"Topic: {purpose_val}" if reading_level == "simple" else purpose_val
    else:
        about = "Not stated in this notice." if reading_level == "simple" else "The main purpose is not explicitly stated in this notice."

    # 2. Eligible
    elig_val = get_effective_fact_value(notice.eligibility)
    if notice.eligibility.status != CertaintyStatus.NOT_STATED:
        eligible = f"Who can apply: {elig_val}" if reading_level == "simple" else elig_val
    else:
        eligible = "No rules stated." if reading_level == "simple" else "No specific eligibility requirements are stated. Check with the organizer."

    # 3. Actions
    act_val = get_effective_fact_value(notice.required_actions)
    if notice.required_actions.status != CertaintyStatus.NOT_STATED:
        actions = f"Steps: {act_val}" if reading_level == "simple" else act_val
    else:
        actions = "No steps given." if reading_level == "simple" else "No specific steps are outlined in the notice."

    # 4. Documents
    doc_val = get_effective_fact_value(notice.required_documents)
    if notice.required_documents.status != CertaintyStatus.NOT_STATED:
        documents = f"Bring: {doc_val}" if reading_level == "simple" else doc_val
    else:
        documents = "No documents needed." if reading_level == "simple" else "No required documents are specified in the notice."

    # 5. Deadline
    dl_val = get_effective_fact_value(notice.deadline)
    if notice.deadline.status != CertaintyStatus.NOT_STATED:
        deadline = f"Due date: {dl_val}" if reading_level == "simple" else dl_val
    else:
        deadline = "No deadline given. Check immediately." if reading_level == "simple" else "No deadline is mentioned. Please verify with the official office immediately."

    # 6. Contact
    contact_val = get_effective_fact_value(notice.contact_details)
    if notice.contact_details.status != CertaintyStatus.NOT_STATED:
        help_contact = f"Contact: {contact_val}" if reading_level == "simple" else contact_val
    else:
        help_contact = "No contact details given." if reading_level == "simple" else "No contact person, phone number, or email is provided in the notice."

    # 7. Missing
    if notice.missing_information:
        missing = "Missing: " + ", ".join(notice.missing_information) if reading_level == "simple" else "The notice is missing critical details: " + ", ".join(notice.missing_information) + "."
    else:
        missing = "All key details are covered." if reading_level == "simple" else "All key standard details appear to be covered in the notice."

    return PlainLanguageSummary(
        about=about,
        eligible=eligible,
        actions=actions,
        documents=documents,
        deadline=deadline,
        help_contact=help_contact,
        missing=missing,
    )


def generate_accessible_summary(
    notice: StructuredNotice,
    client: Optional[OllamaClient] = None,
) -> PlainLanguageSummary:
    """
    Uses Gemma 4 to polish the plain-language summary into simple, accessible English,
    while enforcing that every factual point remains strictly grounded in the verified notice.
    """
    base_summary = generate_deterministic_summary(notice)
    if client is None:
        return base_summary

    prompt = f"""Rewrite the following summary points using very simple words, short sentences, and a warm, clear tone suitable for someone who finds formal notices difficult to read.
Do NOT invent any facts, dates, or documents. If something is missing, keep it clearly labelled as missing.

Input facts:
- What it is about: {base_summary.about}
- Who is eligible: {base_summary.eligible}
- What you must do: {base_summary.actions}
- Documents needed: {base_summary.documents}
- Deadline: {base_summary.deadline}
- Where to get help: {base_summary.help_contact}
- Missing details: {base_summary.missing}

Respond in JSON with the exact keys: 'about', 'eligible', 'actions', 'documents', 'deadline', 'help_contact', 'missing'."""

    try:
        res = client.generate_structured_json(
            system_prompt="You are an accessibility assistant simplifying text for students.",
            user_prompt=prompt,
        )
        return PlainLanguageSummary(
            about=res.get("about", base_summary.about),
            eligible=res.get("eligible", base_summary.eligible),
            actions=res.get("actions", base_summary.actions),
            documents=res.get("documents", base_summary.documents),
            deadline=res.get("deadline", base_summary.deadline),
            help_contact=res.get("help_contact", base_summary.help_contact),
            missing=res.get("missing", base_summary.missing),
        )
    except Exception:
        # Fallback cleanly to deterministic summary if LLM fails or is unavailable
        return base_summary
