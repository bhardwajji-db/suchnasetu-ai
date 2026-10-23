"""
Language Detection Engine for SuchnaSetu AI.
Deterministic, local, privacy-preserving script analysis and lexicon matching
for the 10 constitutional/primary Indian civic notice languages:
en (English), hi (Hindi), bn (Bengali), ta (Tamil), te (Telugu),
mr (Marathi), gu (Gujarati), pa (Punjabi), kn (Kannada), ur (Urdu).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class LanguageMeta:
    code: str
    name: str
    native_name: str
    script: str
    direction: str = "ltr"


LANGUAGE_REGISTRY: Dict[str, LanguageMeta] = {
    "en": LanguageMeta("en", "English", "English", "Latin", "ltr"),
    "hi": LanguageMeta("hi", "Hindi", "हिन्दी", "Devanagari", "ltr"),
    "bn": LanguageMeta("bn", "Bengali", "বাংলা", "Bengali", "ltr"),
    "ta": LanguageMeta("ta", "Tamil", "தமிழ்", "Tamil", "ltr"),
    "te": LanguageMeta("te", "Telugu", "తెలుగు", "Telugu", "ltr"),
    "mr": LanguageMeta("mr", "Marathi", "मराठी", "Devanagari", "ltr"),
    "gu": LanguageMeta("gu", "Gujarati", "ગુજરાતી", "Gujarati", "ltr"),
    "pa": LanguageMeta("pa", "Punjabi", "ਪੰਜਾਬੀ", "Gurmukhi", "ltr"),
    "kn": LanguageMeta("kn", "Kannada", "ಕನ್ನಡ", "Kannada", "ltr"),
    "ur": LanguageMeta("ur", "Urdu", "اردو", "Arabic-derived", "rtl"),
}


# Unicode Block Regexes for Indic & Arabic Scripts
SCRIPT_PATTERNS = {
    "bn": re.compile(r"[\u0980-\u09FF]"),        # Bengali / Assamese
    "pa": re.compile(r"[\u0A00-\u0A7F]"),        # Gurmukhi
    "gu": re.compile(r"[\u0A80-\u0AFF]"),        # Gujarati
    "ta": re.compile(r"[\u0B80-\u0BFF]"),        # Tamil
    "te": re.compile(r"[\u0C00-\u0C7F]"),        # Telugu
    "kn": re.compile(r"[\u0C80-\u0CFF]"),        # Kannada
    "ur": re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"), # Arabic / Urdu
    "devanagari": re.compile(r"[\u0900-\u097F]"), # Hindi & Marathi
    "en": re.compile(r"[a-zA-Z]"),              # Latin / English
}

# Lexical Discriminating Markers for Devanagari (Hindi vs Marathi)
HINDI_WORDS = {
    "है", "हैं", "में", "के", "की", "का", "को", "और", "से", "पर", "ने", "लिए",
    "या", "यह", "था", "थी", "होगा", "कृपया", "तक", "अपना", "आवेदन", "जमा",
    "दस्तावेज", "किया", "गया", "सूचना", "प्रमाण", "पत्र", "शुल्क", "अंतिम", "तिथि",
}

MARATHI_WORDS = {
    "आहे", "आहेत", "मध्ये", "च्या", "आणि", "झाले", "करणे", "नाही", "करणार", "यांचे",
    "दिनांक", "करण्यात", "येईल", "सर्व", "विद्यार्थी", "विद्यार्थ्यांनी", "अर्ज",
    "पर्यंत", "करावे", "जोडावीत", "आवश्यक", "कागदपत्रे", "सादर", "पात्रता", "शुल्क",
    "मुदत", "शासकीय", "प्रमाणपत्र", "तारीख", "शुल्क", "कागदपत्र",
}

URDU_SPECIFIC_CHARS = re.compile(r"[ٹڈڑںہےہبھپھتھٹھجھچھکھگھ]")


@dataclass
class LanguageDetectionResult:
    detected_language: str
    language_name: str
    native_name: str
    confidence: float
    script: str
    is_mixed: bool
    script_distribution: Dict[str, float]
    secondary_languages: List[str] = field(default_factory=list)
    detection_method: str = "unicode_script_and_lexicon"
    uncertainty_warning: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "detected_language": self.detected_language,
            "language_name": self.language_name,
            "native_name": self.native_name,
            "confidence": round(self.confidence, 3),
            "script": self.script,
            "is_mixed": self.is_mixed,
            "script_distribution": {k: round(v, 3) for k, v in self.script_distribution.items()},
            "secondary_languages": self.secondary_languages,
            "detection_method": self.detection_method,
            "uncertainty_warning": self.uncertainty_warning,
        }


def detect_document_language(text: Optional[str]) -> LanguageDetectionResult:
    """
    Detects the natural language of document text using character script distribution
    and localized lexical tokens across the 10 supported languages.
    """
    if not text or not text.strip():
        meta = LANGUAGE_REGISTRY["en"]
        return LanguageDetectionResult(
            detected_language="en",
            language_name=meta.name,
            native_name=meta.native_name,
            confidence=0.0,
            script="Unknown",
            is_mixed=False,
            script_distribution={},
            uncertainty_warning="Notice text is empty. Defaulted to English.",
        )

    clean_text = text.strip()
    total_chars = len(clean_text)

    # 1. Count character occurrences per script block
    counts: Dict[str, int] = {}
    for script_key, pattern in SCRIPT_PATTERNS.items():
        matches = pattern.findall(clean_text)
        if matches:
            counts[script_key] = len(matches)

    meaningful_chars = sum(counts.values())
    if meaningful_chars < 15:
        # Very short text or mostly digits/punctuation
        meta = LANGUAGE_REGISTRY["en"]
        return LanguageDetectionResult(
            detected_language="en",
            language_name=meta.name,
            native_name=meta.native_name,
            confidence=0.40,
            script="Latin",
            is_mixed=False,
            script_distribution={k: v / max(meaningful_chars, 1) for k, v in counts.items()},
            uncertainty_warning="Text is too brief for confident language classification. Please verify.",
        )

    # Distribution proportions
    distribution: Dict[str, float] = {k: v / meaningful_chars for k, v in counts.items()}

    # Identify primary and secondary scripts
    sorted_scripts = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    primary_script, primary_share = sorted_scripts[0]
    
    # Check if mixed
    is_mixed = len(sorted_scripts) > 1 and sorted_scripts[1][1] >= 0.15
    secondary_langs = []

    if primary_script == "devanagari":
        # Disambiguate Hindi vs Marathi using lexical tokens
        tokens = set(re.findall(r"[\u0900-\u097F]+", clean_text))
        hi_score = len(tokens.intersection(HINDI_WORDS))
        mr_score = len(tokens.intersection(MARATHI_WORDS))

        if mr_score > hi_score:
            detected = "mr"
            if hi_score > 0:
                secondary_langs.append("hi")
        else:
            detected = "hi"
            if mr_score > 0:
                secondary_langs.append("mr")

        confidence = max(0.85, primary_share)
    elif primary_script in LANGUAGE_REGISTRY:
        detected = primary_script
        confidence = primary_share
    else:
        # Fallback to English
        detected = "en"
        confidence = primary_share

    # Add secondary scripts
    for script, share in sorted_scripts[1:]:
        if share >= 0.12:
            code = "hi" if script == "devanagari" else script
            if code in LANGUAGE_REGISTRY and code != detected and code not in secondary_langs:
                secondary_langs.append(code)

    meta = LANGUAGE_REGISTRY.get(detected, LANGUAGE_REGISTRY["en"])
    
    warning = None
    if confidence < 0.60:
        warning = f"Language detection confidence is moderate ({confidence:.0%}). Manual override available."
    elif is_mixed:
        sec_names = ", ".join(LANGUAGE_REGISTRY[s].name for s in secondary_langs if s in LANGUAGE_REGISTRY)
        warning = f"Document contains mixed languages: primary {meta.name} with secondary {sec_names}."

    return LanguageDetectionResult(
        detected_language=detected,
        language_name=meta.name,
        native_name=meta.native_name,
        confidence=min(1.0, confidence),
        script=meta.script,
        is_mixed=is_mixed,
        script_distribution=distribution,
        secondary_languages=secondary_langs,
        uncertainty_warning=warning,
    )
