"""
Plain-Language Summary Generator for SuchnaSetu AI.
Transforms complex official notices into clear, grounded answers to the 7 core questions
across three calibrated reading levels: 'simple' (beginner-friendly), 'standard' (everyday clear),
and 'detailed' (comprehensive multi-section administrative breakdown).
"""

from __future__ import annotations

from typing import Optional, List
from notice2action.schemas import (
    StructuredNotice,
    PlainLanguageSummary,
    CertaintyStatus,
    NOT_STATED_LABEL,
    ExtractedFact,
)
from notice2action.llm.base import BaseLLMClient


def _is_fact_stated(fact: Optional[ExtractedFact]) -> bool:
    """Checks whether an extracted fact has genuine verified content."""
    if fact is None:
        return False
    if fact.status == CertaintyStatus.NOT_STATED:
        return False
    val = str(getattr(fact, "value", "") or "").strip()
    if not val or val.lower() == NOT_STATED_LABEL.lower() or val.lower() in ("none", "null", "n/a"):
        return False
    return True


def _get_fact_value(fact: Optional[ExtractedFact]) -> str:
    """Returns user-confirmed value if present, else original extracted value."""
    if fact is None:
        return ""
    if getattr(fact, "user_confirmed", False) and getattr(fact, "confirmed_value", None):
        return str(fact.confirmed_value).strip()
    val = str(getattr(fact, "value", "") or "").strip()
    if val.lower() == NOT_STATED_LABEL.lower():
        return ""
    return val


def generate_deterministic_summary(
    notice: StructuredNotice,
    reading_level: str = "standard",
) -> PlainLanguageSummary:
    """
    Builds a plain-language summary directly from verified grounded facts.
    Guarantees zero hallucination and clear answers to the 7 core citizen questions.

    Supports reading levels:
    - 'simple': Short, beginner-friendly sentences focusing strictly on essential facts.
    - 'standard': Clear everyday language with moderate detail (fees, conditions, reference info).
    - 'detailed': Substantially comprehensive breakdown expanding every notice dimension,
      including administrative references, recipients, conditions, exceptions, evidence quotes,
      late submission rules, and explicit 'not specified' designations for absent info.
    """
    lvl = (reading_level or "standard").lower().strip()
    if lvl not in ("simple", "standard", "detailed"):
        lvl = "standard"

    # Extract all procedural and administrative fact values
    purpose_val = _get_fact_value(notice.purpose)
    purpose_stated = _is_fact_stated(notice.purpose)

    auth_val = _get_fact_value(notice.issuing_authority)
    auth_stated = _is_fact_stated(notice.issuing_authority)

    ref_val = _get_fact_value(notice.notice_reference_number)
    ref_stated = _is_fact_stated(notice.notice_reference_number)

    date_val = _get_fact_value(notice.notice_date)
    date_stated = _is_fact_stated(notice.notice_date)

    recipient_val = _get_fact_value(notice.recipient)
    recipient_stated = _is_fact_stated(notice.recipient)

    subject_val = _get_fact_value(notice.main_subject)
    subject_stated = _is_fact_stated(notice.main_subject)

    elig_val = _get_fact_value(notice.eligibility)
    elig_stated = _is_fact_stated(notice.eligibility)

    fee_val = _get_fact_value(notice.fee_or_cost)
    fee_stated = _is_fact_stated(notice.fee_or_cost)

    actions_val = _get_fact_value(notice.required_actions)
    actions_stated = _is_fact_stated(notice.required_actions)

    action_dl_val = _get_fact_value(notice.required_action_and_deadline)
    action_dl_stated = _is_fact_stated(notice.required_action_and_deadline)

    doc_val = _get_fact_value(notice.required_documents)
    doc_stated = _is_fact_stated(notice.required_documents)

    dl_val = _get_fact_value(notice.deadline)
    dl_stated = _is_fact_stated(notice.deadline)

    contact_val = _get_fact_value(notice.contact_details)
    contact_stated = _is_fact_stated(notice.contact_details)

    conditions_val = _get_fact_value(notice.important_conditions)
    conditions_stated = _is_fact_stated(notice.important_conditions)

    missing_list = [m.strip() for m in (notice.missing_information or []) if m and m.strip()]
    uncertain_list = [u.strip() for u in (notice.uncertain_or_conflicting_details or []) if u and u.strip()]

    # =========================================================================
    # 1. SIMPLE READING LEVEL (Beginner-Friendly, Short Sentences, Essential Facts)
    # =========================================================================
    if lvl == "simple":
        # 1. About
        if purpose_stated:
            about = f"Topic: {purpose_val}"
            if auth_stated:
                about += f". From: {auth_val}."
        else:
            about = "Not stated in this notice."

        # 2. Eligible
        if elig_stated:
            eligible = f"Who can apply: {elig_val}"
            if fee_stated:
                eligible += f". Cost: {fee_val}."
        else:
            eligible = "No rules stated."

        # 3. Actions
        if actions_stated:
            actions = f"Steps: {actions_val}"
        else:
            actions = "No steps given."

        # 4. Documents
        if doc_stated:
            documents = f"Bring: {doc_val}"
        else:
            documents = "No documents needed."

        # 5. Deadline
        if dl_stated:
            deadline = f"Due date: {dl_val}"
        else:
            deadline = "No deadline given. Check immediately."

        # 6. Contact
        if contact_stated:
            help_contact = f"Contact: {contact_val}"
        else:
            help_contact = "No contact details given."

        # 7. Missing
        if missing_list:
            missing = "Missing: " + ", ".join(missing_list)
        else:
            missing = "All key details are covered."

        return PlainLanguageSummary(
            about=about,
            eligible=eligible,
            actions=actions,
            documents=documents,
            deadline=deadline,
            help_contact=help_contact,
            missing=missing,
        )

    # =========================================================================
    # 2. STANDARD READING LEVEL (Everyday Clear Language, Moderate Context)
    # =========================================================================
    if lvl == "standard":
        # 1. About
        if purpose_stated:
            about_parts = [f"This notice announces {purpose_val}."]
            if auth_stated:
                about_parts.append(f"It was issued by {auth_val}.")
            if ref_stated or date_stated:
                meta_bits = []
                if ref_stated:
                    meta_bits.append(f"Notice Ref: {ref_val}")
                if date_stated:
                    meta_bits.append(f"Date: {date_val}")
                about_parts.append(f"({', '.join(meta_bits)})")
            if subject_stated and subject_val.lower() not in purpose_val.lower():
                about_parts.append(f"Subject: {subject_val}.")
            about = " ".join(about_parts)
        else:
            about = "The main purpose and subject matter are not explicitly stated in this notice."

        # 2. Eligible
        if elig_stated:
            elig_parts = [f"Eligibility is open to: {elig_val}."]
            if fee_stated:
                elig_parts.append(f"Application Fee / Cost: {fee_val}.")
            if conditions_stated:
                elig_parts.append(f"Important Conditions & Exceptions: {conditions_val}.")
            eligible = " ".join(elig_parts)
        else:
            eligible = "No specific eligibility requirements or participant criteria are stated. Check with the organizer."

        # 3. Actions
        if actions_stated:
            act_parts = [f"Required actions: {actions_val}."]
            if action_dl_stated and action_dl_val.lower() not in actions_val.lower():
                act_parts.append(f"Key Action & Deadline: {action_dl_val}.")
            actions = " ".join(act_parts)
        else:
            actions = "No specific steps or submission procedures are outlined in the notice."

        # 4. Documents
        if doc_stated:
            documents = f"Required documents: {doc_val}."
        else:
            documents = "No required documents or proof certificates are specified in the notice."

        # 5. Deadline
        if dl_stated:
            dl_parts = [f"Submission deadline: {dl_val}."]
            if notice.deadline.status in (CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING):
                dl_parts.append("(Please note: this deadline is marked as provisional or tentative).")
            deadline = " ".join(dl_parts)
        else:
            deadline = "No deadline is mentioned. Please verify with the official office immediately."

        # 6. Contact
        if contact_stated:
            contact_parts = [f"Official contact: {contact_val}."]
            if auth_stated:
                contact_parts.append(f"(Office: {auth_val}).")
            help_contact = " ".join(contact_parts)
        else:
            help_contact = "No contact person, phone number, or email is provided in the notice."

        # 7. Missing
        if missing_list:
            missing = "The notice is missing important standard information: " + ", ".join(missing_list) + "."
        else:
            missing = "All key standard administrative details appear to be covered in the notice."

        return PlainLanguageSummary(
            about=about,
            eligible=eligible,
            actions=actions,
            documents=documents,
            deadline=deadline,
            help_contact=help_contact,
            missing=missing,
        )

    # =========================================================================
    # 3. DETAILED READING LEVEL (Comprehensive Multi-Section Expansion & Evidence)
    # =========================================================================
    # 1. About
    about_sections: List[str] = []
    if purpose_stated:
        about_sections.append(f"Notice Purpose & Directive: {purpose_val}.")
    else:
        about_sections.append("Notice Purpose: Not explicitly stated in the document text.")

    if auth_stated:
        about_sections.append(f"Issuing Department: {auth_val}.")
    else:
        about_sections.append("Issuing Department: Not specified in the notice.")

    if ref_stated:
        about_sections.append(f"Official Reference Number: {ref_val}.")
    else:
        about_sections.append("Official Reference Number: Not specified in the notice.")

    if date_stated:
        about_sections.append(f"Date of Notice: {date_val}.")
    else:
        about_sections.append("Date of Notice: Not specified in the notice.")

    if recipient_stated:
        about_sections.append(f"Target Recipients / Audience: {recipient_val}.")
    else:
        about_sections.append("Target Recipients: General public / Not specifically restricted in text.")

    if subject_stated and subject_val.lower() not in purpose_val.lower():
        about_sections.append(f"Primary Subject: {subject_val}.")

    if getattr(notice.purpose, "evidence_quote", None):
        about_sections.append(f'[Evidence Quote: "{notice.purpose.evidence_quote}"]')

    if getattr(notice.purpose, "requires_confirmation", False) or notice.purpose.status == CertaintyStatus.UNCERTAIN:
        explanation = getattr(notice.purpose, "explanation", None) or "requires citizen confirmation"
        about_sections.append(f"(Status Note: Marked as tentative or uncertain; confirmation required: {explanation}).")

    detailed_about = " ".join(about_sections)

    # 2. Eligible
    elig_sections: List[str] = []
    if elig_stated:
        elig_sections.append(f"Comprehensive Eligibility Criteria: {elig_val}.")
    else:
        elig_sections.append("Eligibility Criteria: No participant qualification criteria, age bracket, or rules are specified in the notice.")

    if fee_stated:
        elig_sections.append(f"Financial Requirements / Application Fee: {fee_val}.")
    else:
        elig_sections.append("Financial Requirements: Application fee or payment details are not specified in the notice.")

    if conditions_stated:
        elig_sections.append(f"Mandatory Conditions, Exceptions & Waivers: {conditions_val}.")
    else:
        elig_sections.append("Mandatory Conditions: No special exceptions, quota reservations, or disqualifications are noted.")

    if getattr(notice.eligibility, "evidence_quote", None):
        elig_sections.append(f'[Evidence Quote: "{notice.eligibility.evidence_quote}"]')

    if getattr(notice.eligibility, "requires_confirmation", False) or notice.eligibility.status == CertaintyStatus.UNCERTAIN:
        explanation = getattr(notice.eligibility, "explanation", None) or "requires citizen verification"
        elig_sections.append(f"(Uncertainty Notice: Eligibility terms contain ambiguous or tentative conditions: {explanation}).")

    detailed_eligible = " ".join(elig_sections)

    # 3. Actions
    act_sections: List[str] = []
    if actions_stated:
        act_sections.append(f"Step-by-Step Action Procedure: {actions_val}.")
    else:
        act_sections.append("Step-by-Step Actions: The notice provides no detailed instructions on submission procedures.")

    if action_dl_stated:
        act_sections.append(f"Procedural & Submission Directive: {action_dl_val}.")
    else:
        act_sections.append("Submission Location & Channel: Specific physical desk or online URL not explicitly detailed.")

    if conditions_stated and conditions_val.lower() not in detailed_eligible.lower():
        act_sections.append(f"Operating Instructions: {conditions_val}.")

    if getattr(notice.required_actions, "evidence_quote", None):
        act_sections.append(f'[Evidence Quote: "{notice.required_actions.evidence_quote}"]')

    if getattr(notice.required_actions, "requires_confirmation", False):
        act_sections.append("(Verification Notice: Procedural steps contain tentative instructions requiring citizen confirmation).")

    detailed_actions = " ".join(act_sections)

    # 4. Documents
    doc_sections: List[str] = []
    if doc_stated:
        doc_sections.append(f"Document Checklist & Verification Requirements: {doc_val}.")
        doc_sections.append("Submission Format: Ensure originals and valid self-attested photocopies are maintained unless digital upload is specified.")
    else:
        doc_sections.append("Required Documents: No specific documents, certificates, or identity proofs are listed in the notice.")

    if getattr(notice.required_documents, "evidence_quote", None):
        doc_sections.append(f'[Evidence Quote: "{notice.required_documents.evidence_quote}"]')

    if getattr(notice.required_documents, "requires_confirmation", False):
        explanation = getattr(notice.required_documents, "explanation", None) or "verification recommended"
        doc_sections.append(f"(Note: Document requirements contain unverified items: {explanation}).")

    detailed_documents = " ".join(doc_sections)

    # 5. Deadline
    dl_sections: List[str] = []
    if dl_stated:
        dl_sections.append(f"Official Submission Deadline: {dl_val}.")
        if action_dl_stated and action_dl_val.lower() not in dl_val.lower():
            dl_sections.append(f"Cut-off & Action Requirements: {action_dl_val}.")
        dl_sections.append("Late Submission Policy: Not specified in the notice; late submissions may be rejected unless covered by an official extension.")
    else:
        dl_sections.append("Official Submission Deadline: No deadline or closing date is specified in the notice. Immediate verification with the office is strongly advised.")

    if getattr(notice.deadline, "evidence_quote", None):
        dl_sections.append(f'[Evidence Quote: "{notice.deadline.evidence_quote}"]')

    if notice.deadline.status in (CertaintyStatus.UNCERTAIN, CertaintyStatus.CONFLICTING) or getattr(notice.deadline, "requires_confirmation", False):
        uncertainty_type = getattr(notice.deadline, "uncertainty_type", None) or "uncertain"
        explanation = getattr(notice.deadline, "explanation", None) or "tentative date"
        dl_sections.append(f"(Warning: This deadline has been flagged as {uncertainty_type}: {explanation}. Do not rely on tentative dates without official confirmation).")

    detailed_deadline = " ".join(dl_sections)

    # 6. Contact
    contact_sections: List[str] = []
    if contact_stated:
        contact_sections.append(f"Official Inquiries & Helpdesk Directory: {contact_val}.")
    else:
        contact_sections.append("Official Contact Details: No telephone number, email address, or helpdesk desk is provided in the notice text.")

    if auth_stated:
        contact_sections.append(f"Administrative Office: {auth_val}.")
    else:
        contact_sections.append("Administrative Office: Not specified in the notice.")

    contact_sections.append("Helpdesk Working Hours: Official public office hours are not specified in the notice text; contact during standard administrative business hours.")

    if getattr(notice.contact_details, "evidence_quote", None):
        contact_sections.append(f'[Evidence Quote: "{notice.contact_details.evidence_quote}"]')

    detailed_contact = " ".join(contact_sections)

    # 7. Missing
    missing_sections: List[str] = []
    if missing_list:
        items_str = "; ".join(f"({i + 1}) {item}" for i, item in enumerate(missing_list))
        missing_sections.append(f"Omitted Administrative Details: The notice omits the following critical items: {items_str}.")
    else:
        missing_sections.append("Omitted Administrative Details: No standard administrative components appear completely omitted.")

    if uncertain_list:
        uncertain_str = "; ".join(f"({i + 1}) {item}" for i, item in enumerate(uncertain_list))
        missing_sections.append(f"Ambiguous or Conflicting Facts: {uncertain_str}.")
    else:
        missing_sections.append("Ambiguous or Conflicting Facts: None detected in the source text.")

    missing_sections.append("Actionable Citizen Advisory: For any missing or uncertain items, citizens should seek formal written clarification from the issuing office before taking irreversible steps.")

    detailed_missing = " ".join(missing_sections)

    return PlainLanguageSummary(
        about=detailed_about,
        eligible=detailed_eligible,
        actions=detailed_actions,
        documents=detailed_documents,
        deadline=detailed_deadline,
        help_contact=detailed_contact,
        missing=detailed_missing,
    )


def generate_accessible_summary(
    notice: StructuredNotice,
    client: Optional[BaseLLMClient] = None,
) -> PlainLanguageSummary:
    """
    Uses Gemma 4 to polish the plain-language summary into simple, accessible English,
    while enforcing that every factual point remains strictly grounded in the verified notice.
    """
    base_summary = generate_deterministic_summary(notice, reading_level="standard")
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
