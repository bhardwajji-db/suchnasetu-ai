"""
Multilingual Translation Engine for SuchnaSetu AI.
Supports 10 Indian official languages:
- en: English
- hi: Hindi (हिन्दी)
- bn: Bengali (বাংলা)
- ta: Tamil (தமிழ்)
- te: Telugu (తెలుగు)
- mr: Marathi (मराठी)
- gu: Gujarati (ગુજરાતી)
- pa: Punjabi (ਪੰਜਾਬੀ)
- kn: Kannada (ಕನ್ನಡ)
- ur: Urdu (اردو)

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
)
from notice2action.llm.base import BaseLLMClient
from notice2action.grounding import extract_critical_tokens


SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "dir": "ltr", "script": "Latin"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "dir": "ltr", "script": "Devanagari"},
    "bn": {"name": "Bengali", "native": "বাংলা", "dir": "ltr", "script": "Bengali script"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "dir": "ltr", "script": "Tamil script"},
    "te": {"name": "Telugu", "native": "తెలుగు", "dir": "ltr", "script": "Telugu script"},
    "mr": {"name": "Marathi", "native": "मराठी", "dir": "ltr", "script": "Devanagari"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "dir": "ltr", "script": "Gujarati script"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "dir": "ltr", "script": "Gurmukhi"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "dir": "ltr", "script": "Kannada script"},
    "ur": {"name": "Urdu", "native": "اردو", "dir": "rtl", "script": "Arabic-derived"},
}

# Deterministic glossary for recurring notice concepts
DETERMINISTIC_TRANSLATION_MAPS: Dict[str, Dict[str, str]] = {
    "en": {
        "prefix_about": "About",
        "prefix_eligible": "Eligibility",
        "prefix_actions": "Required Actions",
        "prefix_documents": "Documents",
        "prefix_deadline": "Deadline",
        "prefix_help_contact": "Contact",
        "prefix_missing": "Missing Information",
        "not_stated": "Not stated in the notice.",
        "submit_form": "Submit Application Form",
        "pay_fee": "Pay Application Fee",
        "verify_eligibility": "Verify Eligibility Requirements",
        "prepare_documents": "Prepare Required Documents",
        "review_notice": "Review Notification Details",
        "note_deadline": "Note Submission Deadline",
        "contact_helpdesk": "Contact Helpdesk for Clarifications",
    },
    "hi": {
        "prefix_about": "सूचना विवरण",
        "prefix_eligible": "पात्रता",
        "prefix_actions": "आवश्यक कदम",
        "prefix_documents": "दस्तावेज़",
        "prefix_deadline": "अंतिम तिथि",
        "prefix_help_contact": "संपर्क",
        "prefix_missing": "अनुपलब्ध जानकारी",
        "not_stated": "सूचना में उल्लेख नहीं है।",
        "submit_form": "आवेदन पत्र जमा करें",
        "pay_fee": "आवेदन शुल्क का भुगतान करें",
        "verify_eligibility": "पात्रता शर्तों की जांच करें",
        "prepare_documents": "आवश्यक दस्तावेज़ तैयार करें",
        "review_notice": "सूचना विवरण की समीक्षा करें",
        "note_deadline": "आवेदन की अंतिम तिथि नोट करें",
        "contact_helpdesk": "सहायता केंद्र से संपर्क करें",
    },
    "bn": {
        "prefix_about": "বিজ্ঞপ্তি বিবরণ",
        "prefix_eligible": "যোগ্যতা",
        "prefix_actions": "প্রয়োজনীয় পদক্ষেপ",
        "prefix_documents": "প্রয়োজনীয় নথিপত্র",
        "prefix_deadline": "আবেদনের শেষ তারিখ",
        "prefix_help_contact": "যোগাযোগ",
        "prefix_missing": "অনুপস্থিত তথ্য",
        "not_stated": "বিজ্ঞপ্তিতে উল্লেখ নেই।",
        "submit_form": "আবেদনপত্র জমা দিন",
        "pay_fee": "আবেদন ফি প্রদান করুন",
        "verify_eligibility": "যোগ্যতার শর্তাবলী যাচাই করুন",
        "prepare_documents": "প্রয়োজনীয় নথিপত্র প্রস্তুত করুন",
    },
    "ta": {
        "prefix_about": "அறிவிப்பு விவரம்",
        "prefix_eligible": "தகுதி வரம்பு",
        "prefix_actions": "தேவையான நடவடிக்கைகள்",
        "prefix_documents": "தேவையான ஆவணங்கள்",
        "prefix_deadline": "கடைசி தேதி",
        "prefix_help_contact": "தொடர்பு விவரங்கள்",
        "prefix_missing": "குறிப்பிடப்படாத தகவல்",
        "not_stated": "அறிவிப்பில் குறிப்பிடப்படவில்லை.",
        "submit_form": "விண்ணப்ப படிவத்தை சமர்ப்பிக்கவும்",
        "pay_fee": "விண்ணப்பக் கட்டணத்தை செலுத்தவும்",
        "verify_eligibility": "தகுதி நிபந்தனைகளை சரிபார்க்கவும்",
        "prepare_documents": "தேவையான ஆவணங்களைத் தயார் செய்யவும்",
    },
    "te": {
        "prefix_about": "నోటీసు వివరాలు",
        "prefix_eligible": "అర్హత ప్రమాణాలు",
        "prefix_actions": "అవసరమైన చర్యలు",
        "prefix_documents": "అవసరమైన పత్రాలు",
        "prefix_deadline": "చివరి తేదీ",
        "prefix_help_contact": "సంప్రదింపు వివరాలు",
        "prefix_missing": "అందుబాటులో లేని సమాచారం",
        "not_stated": "నోటీసులో పేర్కొనబడలేదు.",
        "submit_form": "దరఖాస్తు ఫారమ్‌ను సమర్పించండి",
        "pay_fee": "దరఖాస్తు రుసుము చెల్లించండి",
        "verify_eligibility": "అర్హత నిబంధనలను పరిశీలించండి",
        "prepare_documents": "అవసరమైన పత్రాలను సిద్ధం చేసుకోండి",
    },
    "mr": {
        "prefix_about": "सूचना तपशील",
        "prefix_eligible": "पात्रता निकष",
        "prefix_actions": "आवश्यक कृती",
        "prefix_documents": "आवश्यक कागदपत्रे",
        "prefix_deadline": "अंतिम मुदत",
        "prefix_help_contact": "संपर्क तपशील",
        "prefix_missing": "अनुपलब्ध माहिती",
        "not_stated": "सूचनेत नमूद केलेले नाही.",
        "submit_form": "अर्ज सादर करा",
        "pay_fee": "अर्ज शुल्क भरा",
        "verify_eligibility": "पात्रतेच्या अटी तपासा",
        "prepare_documents": "आवश्यक कागदपत्रे तयार ठेवा",
    },
    "gu": {
        "prefix_about": "સૂચના વિગતો",
        "prefix_eligible": "પાત્રતા માપદંડ",
        "prefix_actions": "જરૂરી પગલાં",
        "prefix_documents": "જરૂરી દસ્તાવેજો",
        "prefix_deadline": "છેલ્લી તારીખ",
        "prefix_help_contact": "સંપર્ક વિગતો",
        "prefix_missing": "અનુપલબ્ધ માહિતી",
        "not_stated": "સૂચનામાં ઉલ્લેખ નથી.",
        "submit_form": "અરજી ફોર્મ જમા કરો",
        "pay_fee": "અરજી ફી ભરો",
        "verify_eligibility": "પાત્રતા શરતો તપાસો",
        "prepare_documents": "જરૂરી દસ્તાવેજો તૈયાર કરો",
    },
    "pa": {
        "prefix_about": "ਨੋਟਿਸ ਵੇਰਵਾ",
        "prefix_eligible": "ਯੋਗਤਾ ਸ਼ਰਤਾਂ",
        "prefix_actions": "ਲੋੜੀਂਦੀ ਕਾਰਵਾਈ",
        "prefix_documents": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼",
        "prefix_deadline": "ਆਖਰੀ ਮਿਤੀ",
        "prefix_help_contact": "ਸੰਪਰਕ ਵੇਰਵੇ",
        "prefix_missing": "ਗੁੰਮ ਜਾਣਕਾਰੀ",
        "not_stated": "ਨੋਟਿਸ ਵਿੱਚ ਦਰਜ ਨਹੀਂ ਹੈ।",
        "submit_form": "ਅਰਜ਼ੀ ਫਾਰਮ ਜਮ੍ਹਾਂ ਕਰੋ",
        "pay_fee": "ਅਰਜ਼ੀ ਫੀਸ ਅਦਾ ਕਰੋ",
        "verify_eligibility": "ਯੋਗਤਾ ਸ਼ਰਤਾਂ ਦੀ ਜਾਂਚ ਕਰੋ",
        "prepare_documents": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼ ਤਿਆਰ ਕਰੋ",
    },
    "kn": {
        "prefix_about": "ಪ್ರಕಟಣೆ ವಿವರ",
        "prefix_eligible": "ಅರ್ಹತಾ ಮಾನದಂಡಗಳು",
        "prefix_actions": "ಅಗತ್ಯ ಕ್ರಮಗಳು",
        "prefix_documents": "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
        "prefix_deadline": "ಅಂತಿಮ ದಿನಾಂಕ",
        "prefix_help_contact": "ಸಂಪರ್ಕ ವಿವರಗಳು",
        "prefix_missing": "ತಿಳಿಸದಿರುವ ಮಾಹಿತಿ",
        "not_stated": "ಪ್ರಕಟಣೆಯಲ್ಲಿ ತಿಳಿಸಲಾಗಿಲ್ಲ.",
        "submit_form": "ಅರ್ಜಿ ನಮೂನೆಯನ್ನು ಸಲ್ಲಿಸಿ",
        "pay_fee": "ಅರ್ಜಿ ಶುಲ್ಕವನ್ನು ಪಾವತಿಸಿ",
        "verify_eligibility": "ಅರ್ಹತಾ ಷರತ್ತುಗಳನ್ನು ಪರಿಶೀಲಿಸಿ",
        "prepare_documents": "ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿಕೊಳ್ಳಿ",
    },
    "ur": {
        "prefix_about": "نوٹس کی تفصیل",
        "prefix_eligible": "اہلیت کے معیارات",
        "prefix_actions": "مطلوبہ اقدامات",
        "prefix_documents": "مطلوبہ دستاویزات",
        "prefix_deadline": "آخری تاریخ",
        "prefix_help_contact": "رابطے کی تفصیلات",
        "prefix_missing": "غیر موجود معلومات",
        "not_stated": "نوٹس میں درج نہیں ہے۔",
        "submit_form": "درخواست فارم جمع کروائیں",
        "pay_fee": "درخواست فیس ادا کریں",
        "verify_eligibility": "اہلیت کی شرائط کی تصدیق کریں",
        "prepare_documents": "مطلوبہ دستاویزات تیار کریں",
    },
}

# Legacy Hindi map alias for backwards compatibility
DETERMINISTIC_HINDI_MAP = {
    "What is this notice about?": "यह सूचना किस बारे में है?",
    "Who is eligible?": "कौन पात्र है?",
    "What must the reader do?": "आपको क्या करना होगा?",
    "What documents are needed?": "कौन से दस्तावेज़ आवश्यक हैं?",
    "What is the deadline?": "अंतिम तिथि (डेडलाइन) क्या है?",
    "Where can the reader get help?": "सहायता या संपर्क कहाँ करें?",
    "What important information is missing?": "कौन सी महत्वपूर्ण जानकारी उपलब्ध नहीं है?",
    "Not stated in the notice.": "सूचना में उल्लेख नहीं है।",
    "Submit Application Form": "आवेदन पत्र जमा करें",
    "Pay Application Fee": "आवेदन शुल्क का भुगतान करें",
    "Verify Eligibility Requirements": "पात्रता शर्तों की जांच करें",
    "Prepare Required Documents": "आवश्यक दस्तावेज़ तैयार करें",
}


def audit_entity_preservation(source_text: str, translated_text: str) -> Tuple[bool, List[str]]:
    """
    Checks that critical tokens (dates, fees, numbers) from source_text
    appear uncorrupted in translated_text.
    Returns (True, []) if compliant, or (False, list_of_missing_tokens).
    """
    source_tokens = extract_critical_tokens(source_text)
    missing = []

    for tok in source_tokens:
        digits = re.findall(r"\d+", tok)
        for d in digits:
            if d not in translated_text:
                missing.append(f"{tok} (number {d} missing)")

    return len(missing) == 0, missing


def translate_summary(
    summary: PlainLanguageSummary,
    target_lang: str = "en",
    client: Optional[BaseLLMClient] = None,
) -> PlainLanguageSummary:
    """
    Translates a plain-language summary into any of the 10 supported languages,
    ensuring critical entities (dates, fees, contacts) are preserved verbatim.
    """
    lang = target_lang.lower().strip()
    if lang not in SUPPORTED_LANGUAGES or lang == "en":
        return summary

    lang_meta = SUPPORTED_LANGUAGES[lang]
    glossary = DETERMINISTIC_TRANSLATION_MAPS.get(lang, DETERMINISTIC_TRANSLATION_MAPS["en"])

    if client is None:
        # Deterministic structured fallback with natural prefix headers
        return PlainLanguageSummary(
            about=f"{glossary['prefix_about']}: {summary.about}",
            eligible=f"{glossary['prefix_eligible']}: {summary.eligible}",
            actions=f"{glossary['prefix_actions']}: {summary.actions}",
            documents=f"{glossary['prefix_documents']}: {summary.documents}",
            deadline=f"{glossary['prefix_deadline']}: {summary.deadline}",
            help_contact=f"{glossary['prefix_help_contact']}: {summary.help_contact}",
            missing=f"{glossary['prefix_missing']}: {summary.missing}",
        )

    system_prompt = (
        f"You are an expert translator for official notices translating into {lang_meta['name']} ({lang_meta['native']}).\n"
        f"Script: {lang_meta['script']}. Direction: {lang_meta['dir'].upper()}.\n"
        "MANDATORY RULE: Do NOT change, alter, or omit any dates, numbers, amounts, percentages, email addresses, "
        "portal URLs, or contact phone numbers. Keep them verbatim or write them in standard numerals in brackets.\n"
        "Output strictly valid JSON with the exact keys: 'about', 'eligible', 'actions', 'documents', 'deadline', 'help_contact', 'missing'."
    )

    user_prompt = f"""Translate each field into clear, accessible {lang_meta['name']}:
About: {summary.about}
Eligible: {summary.eligible}
Actions: {summary.actions}
Documents: {summary.documents}
Deadline: {summary.deadline}
Help_Contact: {summary.help_contact}
Missing: {summary.missing}

Respond with strictly valid JSON."""

    try:
        data = client.generate_structured_json(system_prompt, user_prompt)
        translated = PlainLanguageSummary(
            about=data.get("about", summary.about),
            eligible=data.get("eligible", summary.eligible),
            actions=data.get("actions", summary.actions),
            documents=data.get("documents", summary.documents),
            deadline=data.get("deadline", summary.deadline),
            help_contact=data.get("help_contact", summary.help_contact),
            missing=data.get("missing", summary.missing),
        )

        # Audit preservation of deadline
        ok, missing = audit_entity_preservation(summary.deadline, translated.deadline)
        if not ok:
            translated.deadline = f"{translated.deadline} ({summary.deadline})"

        return translated
    except Exception:
        return translate_summary(summary, target_lang=lang, client=None)


def translate_checklist(
    checklist: ActionChecklist,
    target_lang: str = "en",
    client: Optional[BaseLLMClient] = None,
) -> ActionChecklist:
    """Translates the action checklist into any of the 10 supported languages, maintaining step order and status."""
    lang = target_lang.lower().strip()
    if lang not in SUPPORTED_LANGUAGES or lang == "en":
        return checklist

    glossary = DETERMINISTIC_TRANSLATION_MAPS.get(lang, DETERMINISTIC_TRANSLATION_MAPS["en"])
    translated_items: List[ChecklistItem] = []

    for item in checklist.items:
        action_text = item.action

        # Replace standard action phrases with localized terms
        phrase_maps = [
            ("Submit Application Form", "submit_form"),
            ("Pay Application Fee", "pay_fee"),
            ("Verify Eligibility Requirements", "verify_eligibility"),
            ("Prepare Required Documents", "prepare_documents"),
            ("Review Notification Details", "review_notice"),
            ("Note Submission Deadline", "note_deadline"),
            ("Contact Helpdesk for Clarifications", "contact_helpdesk"),
        ]
        for en_key, map_key in phrase_maps:
            if en_key.lower() in action_text.lower() and map_key in glossary:
                pattern = re.compile(re.escape(en_key), re.IGNORECASE)
                action_text = pattern.sub(glossary[map_key], action_text)

        translated_items.append(
            ChecklistItem(
                step_number=item.step_number,
                action=action_text,
                category=item.category,
                is_mandatory=item.is_mandatory,
                requires_confirmation=item.requires_confirmation,
                is_completed=item.is_completed,
                grounded_quote=item.grounded_quote,
                notes=item.notes,
            )
        )

    return ActionChecklist(items=translated_items)


# Backwards compatibility wrappers for existing callers
def translate_summary_to_hindi(
    summary: PlainLanguageSummary,
    client: Optional[BaseLLMClient] = None,
) -> PlainLanguageSummary:
    return translate_summary(summary, target_lang="hi", client=client)


def translate_checklist_to_hindi(
    checklist: ActionChecklist,
    client: Optional[BaseLLMClient] = None,
) -> ActionChecklist:
    return translate_checklist(checklist, target_lang="hi", client=client)
