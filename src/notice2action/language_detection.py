"""
Language Detection Engine for SuchnaSetu AI.
Deterministic, local, privacy-preserving script analysis and lexicon matching
for all 22 Indian Scheduled Languages (Eighth Schedule) plus English:
as (Assamese), bn (Bengali), brx (Bodo), doi (Dogri), en (English),
gu (Gujarati), hi (Hindi), kn (Kannada), ks (Kashmiri), kok (Konkani),
mai (Maithili), ml (Malayalam), mni (Manipuri), mr (Marathi), ne (Nepali),
or (Odia), pa (Punjabi), sa (Sanskrit), sat (Santali), sd (Sindhi),
ta (Tamil), te (Telugu), ur (Urdu).
"""

from __future__ import annotations

import re
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


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
    "as": LanguageMeta("as", "Assamese", "অসমীয়া", "Bengali-Assamese", "ltr"),
    "bn": LanguageMeta("bn", "Bengali", "বাংলা", "Bengali", "ltr"),
    "brx": LanguageMeta("brx", "Bodo", "बड़ो", "Devanagari", "ltr"),
    "doi": LanguageMeta("doi", "Dogri", "डोगरी", "Devanagari", "ltr"),
    "gu": LanguageMeta("gu", "Gujarati", "ગુજરાતી", "Gujarati", "ltr"),
    "kn": LanguageMeta("kn", "Kannada", "ಕನ್ನಡ", "Kannada", "ltr"),
    "ks": LanguageMeta("ks", "Kashmiri", "کٲشُر", "Arabic-derived", "rtl"),
    "kok": LanguageMeta("kok", "Konkani", "कोंकणी", "Devanagari", "ltr"),
    "mai": LanguageMeta("mai", "Maithili", "मैथिली", "Devanagari", "ltr"),
    "ml": LanguageMeta("ml", "Malayalam", "മലയാളം", "Malayalam", "ltr"),
    "mni": LanguageMeta("mni", "Manipuri", "মৈতৈলোন্", "Meetei Mayek / Bengali", "ltr"),
    "mr": LanguageMeta("mr", "Marathi", "मराठी", "Devanagari", "ltr"),
    "ne": LanguageMeta("ne", "Nepali", "नेपाली", "Devanagari", "ltr"),
    "or": LanguageMeta("or", "Odia", "ଓଡ଼ିଆ", "Odia", "ltr"),
    "pa": LanguageMeta("pa", "Punjabi", "ਪੰਜਾਬੀ", "Gurmukhi", "ltr"),
    "sa": LanguageMeta("sa", "Sanskrit", "संस्कृतम्", "Devanagari", "ltr"),
    "sat": LanguageMeta("sat", "Santali", "ᱥᱟᱱᱛᱟᱲᱤ", "Ol Chiki", "ltr"),
    "sd": LanguageMeta("sd", "Sindhi", "سنڌي", "Arabic-derived", "rtl"),
    "ta": LanguageMeta("ta", "Tamil", "தமிழ்", "Tamil", "ltr"),
    "te": LanguageMeta("te", "Telugu", "తెలుగు", "Telugu", "ltr"),
    "ur": LanguageMeta("ur", "Urdu", "اردو", "Arabic-derived", "rtl"),
}

# ISO 639-2 / 639-3 Code Aliases for OCR Engine mapping
LANGUAGE_ALIASES: Dict[str, str] = {
    "eng": "en",
    "hin": "hi",
    "asm": "as",
    "ben": "bn",
    "bod": "brx",
    "dgo": "doi",
    "guj": "gu",
    "kan": "kn",
    "kas": "ks",
    "kok": "kok",
    "mai": "mai",
    "mal": "ml",
    "mni": "mni",
    "mar": "mr",
    "nep": "ne",
    "ori": "or",
    "pan": "pa",
    "san": "sa",
    "sat": "sat",
    "snd": "sd",
    "tam": "ta",
    "tel": "te",
    "urd": "ur",
}


# Unicode Block Regexes for Indic, Arabic & Latin Scripts
SCRIPT_PATTERNS = {
    "devanagari": re.compile(r"[\u0900-\u097F]"),  # Hindi, Marathi, Sanskrit, Nepali, Bodo, Dogri, Maithili, Konkani
    "bn_as": re.compile(r"[\u0980-\u09FF]"),       # Bengali & Assamese
    "pa": re.compile(r"[\u0A00-\u0A7F]"),          # Gurmukhi / Punjabi
    "gu": re.compile(r"[\u0A80-\u0AFF]"),          # Gujarati
    "or": re.compile(r"[\u0B00-\u0B7F]"),          # Odia
    "ta": re.compile(r"[\u0B80-\u0BFF]"),          # Tamil
    "te": re.compile(r"[\u0C00-\u0C7F]"),          # Telugu
    "kn": re.compile(r"[\u0C80-\u0CFF]"),          # Kannada
    "ml": re.compile(r"[\u0D00-\u0D7F]"),          # Malayalam
    "sat": re.compile(r"[\u1C50-\u1C7F]"),         # Ol Chiki (Santali)
    "mni": re.compile(r"[\uABC0-\uABFF]"),         # Meetei Mayek (Manipuri)
    "ur": re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"), # Arabic / Urdu / Kashmiri / Sindhi
    "en": re.compile(r"[a-zA-Z]"),                 # Latin / English
}

# Lexical Discriminating Markers for Devanagari Group
HINDI_WORDS = {
    "है", "हैं", "में", "के", "की", "का", "को", "और", "से", "पर", "ने", "लिए",
    "या", "यह", "था", "थी", "होगा", "कृपया", "तक", "अपना", "आवेदन", "जमा",
    "दस्तावेज", "किया", "गया", "सूचना", "प्रमाण", "पत्र", "शुल्क", "अंतिम", "तिथि",
    "सरकार", "भारत", "मंत्रालय", "अधिसूचना", "विभाग", "निदेशालय", "जारी", "करता",
}

MARATHI_WORDS = {
    "आहे", "आहेत", "मध्ये", "च्या", "आणि", "झाले", "करणे", "नाही", "करणार", "यांचे",
    "दिनांक", "करण्यात", "येईल", "सर्व", "विद्यार्थी", "विद्यार्थ्यांनी", "अर्ज",
    "पर्यंत", "करावे", "जोडावीत", "आवश्यक", "कागदपत्रे", "सादर", "पात्रता", "शुल्क",
    "मुदत", "शासकीय", "प्रमाणपत्र", "तारीख", "कागदपत्र",
}

NEPALI_WORDS = {
    "छ", "छन्", "भएको", "गर्नु", "पर्ने", "तथा", "मिति", "नेपाल", "सरकार", "सूचना",
    "लागि", "प्रदेश", "विद्यार्थी", "आवेदन", "शुल्क", "अन्तिम", "भनी", "भने",
}

SANSKRIT_WORDS = {
    "अस्ति", "सन्ति", "भवति", "इति", "च", "तथा", "एवम्", "सर्वकारः", "संस्कृतम्",
    "विश्वविद्यालयः", "विद्या", "प्राप्तम्", "करोति", "कुरुते", "विद्यार्थी",
    "अथ", "सर्वकारस्य", "आधिकारिकम्", "विधीयते", "नमः", "नमो", "अधिसूचनायाः",
}

MAITHILI_WORDS = {
    "अछि", "अछी", "छथि", "कयल", "गेल", "आ", "सँ", "मे", "मिथिला", "सूचना",
    "आवेदन", "देल", "गेलैक", "छैक",
}

KONKANI_WORDS = {
    "आसा", "आसात", "आनी", "केला", "करचें", "खातीर", "गोंय", "सरकार", "अर्ज",
    "दस्तावेजां", "पात्रताय",
}

BODO_WORDS = {
    "दों", "गैया", "आरो", "खामानि", "थाखाय", "बिथांखि", "फरायसुला",
    "बिजाब", "गाहाय",
}

DOGRI_WORDS = {
    "ऐ", "न", "गी", "कन्ने", "आह्दे", "डोगरी", "सूचना", "तारीख",
}

# Assamese vs Bengali Markers
ASSAMESE_UNIQUE_CHARS = re.compile(r"[\u09F0\u09F1]")  # ৰ (ra), ৱ (wa)
ASSAMESE_WORDS = {
    "হৈছে", "কৰা", "আছে", "লৈ", "পৰা", "অসম", "চৰকাৰ", "বিজ্ঞপ্তি", "আবেদন",
    "মাচুল", "অন্তিম", "তাৰিখ", "ছাত্র-ছাত্ৰী",
}
BENGALI_WORDS = {
    "হচ্ছে", "করা", "আছে", "থেকে", "পশ্চিমবঙ্গ", "বিজ্ঞপ্তি", "আবেদন",
    "ফি", "শেষ", "তারিখ", "ছাত্রছাত্রী", "সরকার",
}

# Perso-Arabic Disambiguation Markers
SINDHI_SPECIFIC_CHARS = re.compile(r"[\u067B\u0684\u0683\u0691\u068F\u06BB\u067E\u0680\u068A\u068D\u06FD]")  # ٻ, ڄ, ڃ, ڱ, ڏ, ڻ
KASHMIRI_SPECIFIC_CHARS = re.compile(r"[\u065A\u065B\u0620\u0672\u06C6]")  # ٚ, ٛ, ؠ, ٲ, ۄ
URDU_SPECIFIC_CHARS = re.compile(r"[ٹڈڑںہئےبھپھتھٹھجھچھکھگھ]")


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

    def to_dict(self) -> Dict[str, Any]:
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
    and localized lexical tokens across all 22 Indian Scheduled Languages plus English.
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

    detected = "en"
    confidence = primary_share

    if primary_script == "devanagari":
        # Disambiguate languages within the Devanagari family
        tokens = set(re.findall(r"[\u0900-\u097F]+", clean_text))
        
        scores = {
            "hi": len(tokens.intersection(HINDI_WORDS)) * 1.0,
            "mr": len(tokens.intersection(MARATHI_WORDS)) * 1.1,  # slight boost for distinctive Marathi affixes
            "ne": len(tokens.intersection(NEPALI_WORDS)) * 1.1,
            "sa": len(tokens.intersection(SANSKRIT_WORDS)) * 1.2,
            "mai": len(tokens.intersection(MAITHILI_WORDS)) * 1.1,
            "kok": len(tokens.intersection(KONKANI_WORDS)) * 1.1,
            "brx": len(tokens.intersection(BODO_WORDS)) * 1.2,
            "doi": len(tokens.intersection(DOGRI_WORDS)) * 1.2,
        }

        # Check for Marathi lateral consonant ळ (\u0933)
        if "\u0933" in clean_text:
            scores["mr"] += 3.0

        best_dev_lang = max(scores.items(), key=lambda x: x[1])
        if best_dev_lang[1] > 0:
            detected = best_dev_lang[0]
            # Add runner-up as secondary if noticeable
            for l_code, s_val in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:]:
                if s_val > 1.0 and l_code not in secondary_langs:
                    secondary_langs.append(l_code)
                    break
        else:
            detected = "hi"  # Default Devanagari to Hindi if no lexicon triggers

        confidence = max(0.85, primary_share)

    elif primary_script == "bn_as":
        # Disambiguate Bengali vs Assamese
        as_chars = len(ASSAMESE_UNIQUE_CHARS.findall(clean_text))
        tokens = set(re.findall(r"[\u0980-\u09FF]+", clean_text))
        as_words = len(tokens.intersection(ASSAMESE_WORDS))
        bn_words = len(tokens.intersection(BENGALI_WORDS))

        if as_chars > 0 or as_words > bn_words:
            detected = "as"
            if bn_words > 0:
                secondary_langs.append("bn")
        else:
            detected = "bn"
            if as_words > 0 or as_chars > 0:
                secondary_langs.append("as")

        confidence = max(0.85, primary_share)

    elif primary_script == "ur":
        # Disambiguate Urdu, Kashmiri, Sindhi
        sd_chars = len(SINDHI_SPECIFIC_CHARS.findall(clean_text))
        ks_chars = len(KASHMIRI_SPECIFIC_CHARS.findall(clean_text))

        if sd_chars > 0:
            detected = "sd"
        elif ks_chars > 0:
            detected = "ks"
        else:
            detected = "ur"

        confidence = max(0.85, primary_share)

    elif primary_script == "sat":
        detected = "sat"
        confidence = primary_share

    elif primary_script == "mni":
        detected = "mni"
        confidence = primary_share

    elif primary_script in LANGUAGE_REGISTRY:
        detected = primary_script
        confidence = primary_share

    else:
        detected = "en"
        confidence = primary_share

    # Add secondary scripts
    for script, share in sorted_scripts[1:]:
        if share >= 0.12:
            code = "hi" if script == "devanagari" else ("bn" if script == "bn_as" else ("ur" if script == "ur" else script))
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
    e.g. en -> 'eng', hi -> 'hin', bn -> 'ben', as -> 'asm', mixed -> '<lang>+eng'
    """
    lang = detection.detected_language
    
    lang_map = {
        "en": "eng",
        "hi": "hin",
        "as": "asm",
        "bn": "ben",
        "brx": "hin",     # Bodo in Devanagari script uses hin base
        "doi": "hin",     # Dogri in Devanagari script uses hin base
        "gu": "guj",
        "kn": "kan",
        "ks": "urd",      # Kashmiri in Perso-Arabic uses urd base in Tesseract
        "kok": "mar",     # Konkani in Devanagari uses mar/hin base
        "mai": "hin",     # Maithili in Devanagari uses hin base
        "ml": "mal",
        "mni": "ben",     # Manipuri in Bengali script uses ben base
        "mr": "mar",
        "ne": "nep",
        "or": "ori",
        "pa": "pan",
        "sa": "san",
        "sat": "sat",     # Santali Ol Chiki
        "sd": "snd",      # Sindhi in Arabic script
        "ta": "tam",
        "te": "tel",
        "ur": "urd",
    }
    
    base_code = lang_map.get(lang, "hin")
    
    # If document is mixed-language or contains bilingual Indic+English content
    if detection.is_mixed:
        if lang != "en":
            return f"{base_code}+eng"
        # Primary was classified as English, but contains significant regional script
        for sec in detection.secondary_languages:
            if sec != "en" and sec in lang_map:
                return f"{lang_map[sec]}+eng"
        # Check script distribution for prominent Indic scripts
        script_to_lang = {
            "devanagari": "hin", "bn_as": "ben", "ta": "tam", "te": "tel",
            "kn": "kan", "ml": "mal", "gu": "guj", "pa": "pan", "or": "ori", "ur": "urd",
            "sat": "sat", "mni": "ben",
        }
        for script, share in detection.script_distribution.items():
            if script != "en" and share >= 0.15:
                if script in script_to_lang:
                    return f"{script_to_lang[script]}+eng"
        return "eng"

    # Single-script with minor secondary Latin (dates, codes)
    if lang != "en" and detection.script_distribution.get("en", 0.0) >= 0.10:
        return f"{base_code}+eng"
        
    return base_code


def segment_text_regions_by_script(text: str) -> List[Dict[str, Any]]:
    """
    Segments a multilingual text notice into contiguous spans grouped by dominant script.
    Useful for multi-column and mixed-script notice processing.
    """
    if not text or not text.strip():
        return []

    lines = text.splitlines()
    regions: List[Dict[str, Any]] = []

    for line_idx, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line:
            continue

        line_det = detect_document_language(clean_line)
        regions.append({
            "line_number": line_idx + 1,
            "text": clean_line,
            "detected_language": line_det.detected_language,
            "script": line_det.script,
            "confidence": line_det.confidence,
            "is_mixed": line_det.is_mixed,
        })

    return regions


def detect_image_language(image) -> LanguageDetectionResult:
    """
    Intelligently detects natural language directly from an image or scanned document.
    Executes a fast script & character analysis pass:
    1. Tesseract OSD script detection (Orientation and Script Detection).
    2. Fast text sampling via bilingual OCR or RapidOCR.
    3. Character block distribution and lexical analysis across 22 Scheduled Languages + English.
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
            detection_method="tesseract_osd",
        )

    meta = LANGUAGE_REGISTRY["en"]
    return LanguageDetectionResult(
        detected_language="en",
        language_name=meta.name,
        native_name=meta.native_name,
        confidence=0.50,
        script="Latin",
        is_mixed=False,
        script_distribution={"en": 1.0},
        detection_method="fallback_default",
        uncertainty_warning="Unable to reliably identify language from image sample. Defaulted to English.",
    )
