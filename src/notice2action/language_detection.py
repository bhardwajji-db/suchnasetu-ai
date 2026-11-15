"""
Language Detection Engine for SuchnaSetu AI.
Deterministic, local, privacy-preserving script analysis and lexicon matching
for the 10 constitutional/primary Indian civic notice languages:
en (English), hi (Hindi), bn (Bengali), ta (Tamil), te (Telugu),
mr (Marathi), gu (Gujarati), pa (Punjabi), kn (Kannada), ur (Urdu).
"""

from __future__ import annotations

import re
import os
from dataclasses import dataclass, field
from pathlib import Path
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


def get_ocr_language_for_detection(detection: LanguageDetectionResult) -> str:
    """
    Maps a LanguageDetectionResult to the optimal OCR engine language parameter.
    e.g. en -> 'eng', hi -> 'hin', mixed/bilingual -> 'hin+eng'
    """
    if detection.is_mixed:
        return "hin+eng"
    lang = detection.detected_language
    if lang == "en":
        return "eng"
    if lang in ("hi", "mr"):
        if detection.script_distribution.get("en", 0.0) >= 0.10:
            return "hin+eng"
        return "hin"
    lang_map = {
        "bn": "ben",
        "gu": "guj",
        "pa": "pan",
        "ta": "tam",
        "te": "tel",
        "kn": "kan",
        "ur": "urd",
    }
    return lang_map.get(lang, "hin+eng")


def detect_image_language(image) -> LanguageDetectionResult:
    """
    Intelligently detects natural language directly from an image or scanned document.
    Executes a fast script & character analysis pass:
    1. Tesseract OSD script detection (Orientation and Script Detection).
    2. Fast text sampling via bilingual OCR or RapidOCR.
    3. Character block distribution and lexical analysis across 10 languages.
    """
    from PIL import Image as PILImage
    import pytesseract
    import numpy as np
    from notice2action.config import config

    if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
        meta = LANGUAGE_REGISTRY["en"]
        return LanguageDetectionResult(
            detected_language="en",
            language_name=meta.name,
            native_name=meta.native_name,
            confidence=0.5,
            script="Latin",
            is_mixed=False,
            script_distribution={"en": 1.0},
            uncertainty_warning="OCR binary unavailable; defaulted to English.",
        )

    pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
    if config.tessdata_dir and Path(config.tessdata_dir).is_dir():
        os.environ["TESSDATA_PREFIX"] = str(Path(config.tessdata_dir).resolve())

    # 1. Quick OSD check for script classification
    osd_script = None
    try:
        w, h = image.size
        scale = min(1.0, 1000.0 / max(w, h))
        osd_img = image.resize((int(w * scale), int(h * scale)), PILImage.Resampling.BILINEAR) if scale < 1.0 else image
        osd_text = pytesseract.image_to_osd(osd_img)
        sm = re.search(r"Script:\s*([A-Za-z]+)", osd_text)
        if sm:
            osd_script = sm.group(1).lower()
    except Exception:
        pass

    # 2. Fast sampling text extraction
    sample_text = ""
    # If OSD detected Devanagari, prioritize Tesseract hin+eng because standard RapidOCR
    # is trained on Latin/Chinese and will misclassify Devanagari by only reading English headings.
    if osd_script == "devanagari":
        try:
            w, h = image.size
            scale = min(1.0, 1400.0 / max(w, h))
            sample_img = image.resize((int(w * scale), int(h * scale)), PILImage.Resampling.BILINEAR) if scale < 1.0 else image
            sample_text = pytesseract.image_to_string(sample_img, lang="hin+eng")
        except Exception:
            pass

    if not sample_text:
        try:
            from rapidocr_onnxruntime import RapidOCR
            engine = RapidOCR()
            res, _ = engine(np.array(image))
            if res:
                sample_text = " ".join(item[1] for item in res)
        except Exception:
            pass

    if not sample_text or len(sample_text.strip()) < 30:
        try:
            w, h = image.size
            scale = min(1.0, 1400.0 / max(w, h))
            sample_img = image.resize((int(w * scale), int(h * scale)), PILImage.Resampling.BILINEAR) if scale < 1.0 else image
            sample_text = pytesseract.image_to_string(sample_img, lang="hin+eng")
        except Exception:
            pass

    # 3. Analyze sample text distribution
    if sample_text and sample_text.strip():
        det = detect_document_language(sample_text)
        if osd_script == "devanagari" and det.detected_language == "en":
            det.detected_language = "hi"
            det.is_mixed = True
        return det

    # 4. If text extraction produced no characters, fall back to OSD script or English
    if osd_script == "devanagari":
        meta = LANGUAGE_REGISTRY["hi"]
        return LanguageDetectionResult(
            detected_language="hi",
            language_name=meta.name,
            native_name=meta.native_name,
            confidence=0.75,
            script="Devanagari",
            is_mixed=False,
            script_distribution={"devanagari": 1.0},
        )
    elif osd_script == "latin":
        meta = LANGUAGE_REGISTRY["en"]
        return LanguageDetectionResult(
            detected_language="en",
            language_name=meta.name,
            native_name=meta.native_name,
            confidence=0.85,
            script="Latin",
            is_mixed=False,
            script_distribution={"en": 1.0},
        )

    meta = LANGUAGE_REGISTRY["en"]
    return LanguageDetectionResult(
        detected_language="en",
        language_name=meta.name,
        native_name=meta.native_name,
        confidence=0.40,
        script="Latin",
        is_mixed=False,
        script_distribution={"en": 1.0},
        uncertainty_warning="Low document content detected. Defaulted to English with manual override enabled.",
    )

