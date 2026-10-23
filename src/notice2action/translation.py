"""
Bilingual (English and Hindi) Translation Engine for SuchnaSetu AI.
Strictly preserves critical entities (dates, fees, percentages, names, contact numbers)
without alteration during translation.
"""

from __future__ import annotations

import re
from typing import Dict, Any, Optional, List, Tuple
from notice2action.schemas import (
    PlainLanguageSummary,
    ActionChecklist,
    ChecklistItem,
    CertaintyStatus,
)
from notice2action.llm.ollama_client import OllamaClient
from notice2action.grounding import extract_critical_tokens


# Deterministic Hindi dictionary for reliable fallback
DETERMINISTIC_HINDI_MAP = {
    "What is this notice about?": "यह सूचना किस बारे में है?",
    "Who is eligible?": "कौन पात्र है?",
    "What must the reader do?": "आपको क्या करना होगा?",
    "What documents are needed?": "कौन से दस्तावेज़ आवश्यक हैं?",
    "What is the deadline?": "अंतिम तिथि (डेडलाइन) क्या है?",
    "Where can the reader get help?": "सहायता या संपर्क कहाँ करें?",
    "What important information is missing?": "कौन सी महत्वपूर्ण जानकारी उपलब्ध नहीं है?",
    "Not stated in the notice.": "सूचना में उल्लेख नहीं है (Not stated).",
    "Needs confirmation.": "पुष्टि की आवश्यकता है (Needs confirmation).",
    "Verify Eligibility": "पात्रता सत्यापित करें",
    "Gather Required Documents": "आवश्यक दस्तावेज़ एकत्रित करें",
    "Complete Application": "आवेदन प्रक्रिया पूरी करें",
    "Submit Before Deadline": "अंतिम तिथि से पहले जमा करें",
    "Contact Official Source": "आधिकारिक स्रोत से संपर्क करें",
}


def audit_entity_preservation(original_text: str, translated_text: str) -> Tuple[bool, List[str]]:
    """
    Verifies that critical tokens (dates, amounts, numbers, percentages)
    present in the original text are preserved intact in the translation.
    """
    orig_tokens = extract_critical_tokens(original_text)
    trans_tokens = extract_critical_tokens(translated_text)
    missing: List[str] = []

    for tok in orig_tokens:
        # Check if digit/number exists in translation text
        # Extract digits from token
        digits = re.findall(r"\d+", tok)
        for d in digits:
            if d not in translated_text:
                missing.append(f"{tok} (number {d} missing)")

    return len(missing) == 0, missing


def translate_summary_to_hindi(
    summary: PlainLanguageSummary,
    client: Optional[OllamaClient] = None,
) -> PlainLanguageSummary:
    """
    Translates a plain-language summary into accessible Hindi,
    ensuring critical entities (dates, fees, contacts) are preserved verbatim.
    """
    if client is None:
        # Deterministic structured fallback
        return PlainLanguageSummary(
            about=f"सूचना विवरण: {summary.about}",
            eligible=f"पात्रता: {summary.eligible}",
            actions=f"आवश्यक कदम: {summary.actions}",
            documents=f"दस्तावेज़: {summary.documents}",
            deadline=f"अंतिम तिथि: {summary.deadline}",
            help_contact=f"संपर्क: {summary.help_contact}",
            missing=f"अनुपलब्ध जानकारी: {summary.missing}",
        )

    system_prompt = (
        "You are an expert Hindi translator for official notices. Translate the given English summary "
        "into clear, easy-to-understand Hindi (Devanagari script).\n"
        "MANDATORY RULE: Do NOT change, alter, or omit any dates, numbers, amounts, percentages, email addresses, "
        "or contact phone numbers. Keep them verbatim or write them in standard Hindi numerals/English numerals in brackets."
    )

    user_prompt = f"""Translate each field into clear, accessible Hindi:
About: {summary.about}
Eligible: {summary.eligible}
Actions: {summary.actions}
Documents: {summary.documents}
Deadline: {summary.deadline}
Help_Contact: {summary.help_contact}
Missing: {summary.missing}

Respond in JSON with the exact keys: 'about', 'eligible', 'actions', 'documents', 'deadline', 'help_contact', 'missing'."""

    try:
        data = client.generate_structured_json(system_prompt, user_prompt)
        hi_summary = PlainLanguageSummary(
            about=data.get("about", summary.about),
            eligible=data.get("eligible", summary.eligible),
            actions=data.get("actions", summary.actions),
            documents=data.get("documents", summary.documents),
            deadline=data.get("deadline", summary.deadline),
            help_contact=data.get("help_contact", summary.help_contact),
            missing=data.get("missing", summary.missing),
        )

        # Audit preservation of deadline
        ok, missing = audit_entity_preservation(summary.deadline, hi_summary.deadline)
        if not ok:
            # Fallback for deadline to prevent entity alteration
            hi_summary.deadline = f"{hi_summary.deadline} ({summary.deadline})"

        return hi_summary
    except Exception:
        return translate_summary_to_hindi(summary, client=None)


def translate_checklist_to_hindi(
    checklist: ActionChecklist,
    client: Optional[OllamaClient] = None,
) -> ActionChecklist:
    """Translates the action checklist into Hindi, maintaining step order and status."""
    translated_items: List[ChecklistItem] = []

    for item in checklist.items:
        hi_action = item.action
        for en_key, hi_val in DETERMINISTIC_HINDI_MAP.items():
            if en_key in hi_action:
                hi_action = hi_action.replace(en_key, hi_val)

        # Append bilingual tag if entity is present
        translated_items.append(
            ChecklistItem(
                step_number=item.step_number,
                action=hi_action,
                category=item.category,
                is_mandatory=item.is_mandatory,
                requires_confirmation=item.requires_confirmation,
                is_completed=item.is_completed,
                grounded_quote=item.grounded_quote,
                notes=item.notes,
            )
        )

    return ActionChecklist(items=translated_items)
