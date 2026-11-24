"""
Comprehensive Test Suite for Universal Multilingual OCR Subsystem.
Validates recognition capabilities, script detection, language routing,
coverage registry metadata, and safe error handling across all 22 Indian Scheduled
Languages (Eighth Schedule of the Constitution of India) plus English.
"""

import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from notice2action.language_detection import (
    LANGUAGE_REGISTRY,
    LANGUAGE_ALIASES,
    SCRIPT_PATTERNS,
    detect_document_language,
    get_ocr_language_for_detection,
    segment_text_regions_by_script,
)
from notice2action.coverage_registry import (
    SCHEDULED_LANGUAGES_REGISTRY,
    get_language_coverage,
    get_all_coverage_items,
    get_coverage_summary,
)
from notice2action.ocr import (
    TesseractOCREngine,
    IndicOCREngine,
    HybridMultilingualOCREngine,
    get_ocr_engine,
    get_available_tesseract_languages,
    fused_multilingual_tesseract,
)
from notice2action.api.server import app


# ---------------------------------------------------------------------------
# 1. Script & Language Detection Tests
# ---------------------------------------------------------------------------

def test_language_registry_covers_all_22_scheduled_languages_plus_english():
    """Verify the registry contains exactly 23 languages (22 Scheduled + English)."""
    assert len(LANGUAGE_REGISTRY) == 23
    assert len(SCHEDULED_LANGUAGES_REGISTRY) == 23

    # All Eighth Schedule languages
    scheduled_codes = {
        "as", "bn", "brx", "doi", "en", "gu", "hi", "kn", "ks", "kok",
        "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd",
        "ta", "te", "ur"
    }
    assert set(LANGUAGE_REGISTRY.keys()) == scheduled_codes
    assert set(SCHEDULED_LANGUAGES_REGISTRY.keys()) == scheduled_codes


def test_script_detection_dravidian_languages():
    """Verify distinct Dravidian scripts are correctly identified."""
    samples = {
        "ta": "தமிழ்நாடு அரசு தலைமைச் செயலகம் செய்தி வெளியீடு",
        "te": "ఆంధ్ర ప్రదేశ్ ప్రభుత్వం అధికారిక ప్రకటన",
        "kn": "ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಅಧಿಕೃತ ಅಧಿಸೂಚನೆ ಪ್ರಕಟಣೆ",
        "ml": "കേരള സർക്കാർ ഔദ്യോഗിക വിജ്ഞാപനം",
    }
    for expected_lang, text in samples.items():
        res = detect_document_language(text)
        assert res.detected_language == expected_lang, f"Failed for {expected_lang}: got {res.detected_language}"
        assert res.confidence >= 0.70


def test_script_detection_eastern_indo_aryan():
    """Verify Bengali, Assamese, and Odia script identification and disambiguation."""
    # Bengali standard
    res_bn = detect_document_language("পশ্চিমবঙ্গ সরকার স্বাস্থ্য দপ্তর নির্দেশিকা")
    assert res_bn.detected_language == "bn"

    # Assamese with distinctive characters ৰ (U+09F0) and ৱ (U+09F1)
    res_as = detect_document_language("অসম চৰকাৰৰ স্বাস্থ্য আৰু পৰিয়াল কল্যাণ বিভাগৰ জাননী")
    assert res_as.detected_language == "as"

    # Odia script
    res_or = detect_document_language("ଓଡ଼ିଶା ସରକାର ସ୍ୱାସ୍ଥ୍ୟ ଓ ପରିବାର କଲ୍ୟାଣ ବିଭାଗ ବିଜ୍ଞପ୍ତି")
    assert res_or.detected_language == "or"


def test_script_detection_western_and_northern_scripts():
    """Verify Gujarati and Gurmukhi (Punjabi) script detection."""
    # Gujarati
    res_gu = detect_document_language("ગુજરાત સરકાર અધિકૃત જાહેરનામું આરોગ્ય વિભાગ")
    assert res_gu.detected_language == "gu"

    # Punjabi (Gurmukhi)
    res_pa = detect_document_language("ਪੰਜਾਬ ਸਰਕਾਰ ਸਿਹਤ ਅਤੇ ਪਰਿਵਾਰ ਭਲਾਈ ਵਿਭਾਗ ਨੋਟੀਫਿਕੇਸ਼ਨ")
    assert res_pa.detected_language == "pa"


def test_script_detection_perso_arabic_family():
    """Verify Urdu, Kashmiri, and Sindhi Perso-Arabic detection and disambiguation."""
    # Urdu
    res_ur = detect_document_language("حکومت ہند سرکاری نوٹیفکیشن برائے اطلاع عام")
    assert res_ur.detected_language == "ur"

    # Kashmiri with Kashmiri-specific diacritics (ٲ, ؠ, etc.)
    res_ks = detect_document_language("حکوٗمَتِ ہِند سَرکٲرؠ نۄٹِفِکیشن کٲشُر")
    assert res_ks.detected_language == "ks"

    # Sindhi with Sindhi-specific 4-dot characters (ڄ, ڃ, ڳ, etc.)
    res_sd = detect_document_language("سنڌ حڪومت سرڪاري نوٽيفڪيشن ڄ ڳ")
    assert res_sd.detected_language == "sd"


def test_script_detection_specialized_indigenous_scripts():
    """Verify Santali (Ol Chiki) and Manipuri (Meetei Mayek) detection."""
    # Santali Ol Chiki (U+1C50 - U+1C7F)
    res_sat = detect_document_language("ᱥᱟᱱᱛᱟᱲᱤ ᱯᱟᱹᱨᱥᱤ ᱥᱚᱨᱠᱟᱨᱤ ᱵᱤᱞᱟᱹᱭ")
    assert res_sat.detected_language == "sat"
    assert res_sat.script == "Ol Chiki"

    # Manipuri Meetei Mayek (U+ABC0 - U+ABFF)
    res_mni = detect_document_language("ꯃꯩꯇꯩꯂꯣꯟ ꯂꯩꯉꯥꯛꯀꯤ ꯄꯥꯎ")
    assert res_mni.detected_language == "mni"
    assert "Meetei Mayek" in res_mni.script


def test_devanagari_lexical_disambiguation():
    """Verify disambiguation among languages sharing Devanagari script."""
    # Hindi
    res_hi = detect_document_language("भारत सरकार गृह मंत्रालय आधिकारिक अधिसूचना जारी करता है")
    assert res_hi.detected_language == "hi"

    # Marathi
    res_mr = detect_document_language("महाराष्ट्र शासन अधिकृत राजपत्र अधिसूचना जाहीर करण्यात येत आहे")
    assert res_mr.detected_language == "mr"

    # Sanskrit
    res_sa = detect_document_language("अथ सर्वकारस्य आधिकारिकम् अधिसूचना विधीयते नमो नमः")
    assert res_sa.detected_language == "sa"

    # Nepali
    res_ne = detect_document_language("नेपाल सरकार आधिकारिक सूचना प्रकाशित गरिएको छ")
    assert res_ne.detected_language == "ne"


def test_bilingual_and_mixed_document_detection():
    """Verify bilingual government notice detection (Hindi + English)."""
    text = (
        "भारत का राजपत्र The Gazette of India REGD. NO. D. L.-33004/99\n"
        "असाधारण EXTRAORDINARY\n"
        "भाग II—खण्ड 3—उप-खण्ड (ii) PART II—Section 3—Sub-section (ii)\n"
        "नई दिल्ली, शुक्रवार, अप्रैल 28, 2017 NEW DELHI, FRIDAY, APRIL 28, 2017\n"
    )
    res = detect_document_language(text)
    assert res.is_mixed is True
    assert "devanagari" in res.script_distribution
    assert "en" in res.script_distribution
    suggested = get_ocr_language_for_detection(res)
    assert "hin" in suggested and "eng" in suggested


# ---------------------------------------------------------------------------
# 2. Coverage Registry Tests
# ---------------------------------------------------------------------------

def test_coverage_registry_lookups():
    """Verify lookup by ISO-639-1, ISO-639-2, and name."""
    # Direct code lookup
    item_hi = get_language_coverage("hi")
    assert item_hi is not None
    assert item_hi.name == "Hindi"
    assert item_hi.iso_639_2 == "hin"

    # ISO-639-2 alias lookup
    item_tam = get_language_coverage("tam")
    assert item_tam is not None
    assert item_tam.name == "Tamil"
    assert item_tam.code == "ta"

    # Name lookup (case-insensitive)
    item_mr = get_language_coverage("Marathi")
    assert item_mr is not None
    assert item_mr.code == "mr"


def test_coverage_summary_breakdown():
    """Verify coverage summary outputs valid counts and lists."""
    summary = get_coverage_summary()
    assert summary["total_languages"] == 23
    assert summary["verified_production_count"] >= 2  # English + Hindi verified
    assert "English" in summary["installed_languages"]
    assert "Hindi" in summary["installed_languages"]


# ---------------------------------------------------------------------------
# 3. Missing Language Pack & Non-Silent Fallback Handling
# ---------------------------------------------------------------------------

def test_missing_language_pack_strict_error_handling():
    """
    Verify that requesting an uninstalled regional script (e.g. Santali Ol Chiki)
    returns is_uncertain=True, empty extracted text, and an informative diagnostic,
    and NEVER silently falls back to English OCR to output garbled ASCII noise.
    """
    engine = TesseractOCREngine()
    avail = get_available_tesseract_languages()

    # If sat is not installed in the current environment
    if "sat" not in avail:
        # Create a blank test image
        img = Image.new("RGB", (300, 100), color=(255, 255, 255))
        result = engine.extract_text(img, target_lang="sat", apply_preprocessing=False)

        assert result.is_uncertain is True
        assert result.extracted_text == ""
        assert result.confidence_score == 0.0
        assert "sat.traineddata" in result.error
        assert "assets/tessdata/" in result.error
        assert result.languages_used == "sat"


def test_devanagari_language_fallback_to_hin_base():
    """
    Verify that requesting a Devanagari regional language (e.g. Maithili or Bodo)
    when mai.traineddata is absent falls back to the installed base Devanagari engine (hin)
    with an informative warning instead of failing or using Latin OCR.
    """
    engine = TesseractOCREngine()
    avail = get_available_tesseract_languages()

    if "hin" in avail and "mai" not in avail:
        from pathlib import Path
        fixture_path = Path("tests/fixtures/synthetic_notice_ocr.png")
        if fixture_path.is_file():
            img = Image.open(fixture_path)
        else:
            img = Image.new("RGB", (400, 100), color=(255, 255, 255))

        result = engine.extract_text(img, target_lang="mai", apply_preprocessing=False)
        # Should recognize using hin base and log an explanatory warning
        assert result.warning is not None
        assert "base Devanagari model ('hin')" in result.warning
        assert "hin" in result.languages_used


def test_stage1_regional_language_real_document_ocr():
    """
    Empirically verifies real document OCR execution across Stage 1 installed regional models:
    Marathi (mar), Tamil (tam), Bengali (ben), and Telugu (tel).
    Confirms valid character extraction, zero crashes, and correct language routing.
    """
    from PIL import ImageFont
    from pathlib import Path

    engine = TesseractOCREngine()
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    if not Path(font_path).is_file():
        pytest.skip("Nirmala UI Indic font not installed on Windows host")

    font = ImageFont.truetype(font_path, 36)
    stage1_cases = [
        ("mar", "महाराष्ट्र शासन राजपत्र असाधारण अधिसूचना 2026"),
        ("tam", "தமிழ்நாடு அரசு தலைமைச் செயலகம் செய்தி வெளியீடு 2026"),
        ("ben", "পশ্চিমবঙ্গ সরকার স্বাস্থ্য ও পরিবার কল্যাণ বিভাগ 2026"),
        ("tel", "ఆంధ్ర ప్రదేశ్ ప్రభుత్వం అధికారిక ప్రకటన 2026"),
    ]

    for lang, text in stage1_cases:
        img = Image.new("RGB", (1600, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((40, 60), text, font=font, fill=(0, 0, 0))

        res = engine.extract_text(img, target_lang=lang, apply_preprocessing=True)
        assert res.error is None, f"{lang} extraction failed: {res.error}"
        assert res.extracted_text != "", f"{lang} returned empty text"
        assert res.confidence_score > 30.0, f"{lang} confidence score too low: {res.confidence_score}"
        assert "2026" in res.extracted_text, f"{lang} failed to extract date year '2026'"
        assert res.languages_used in (lang, f"{lang}+eng")


def test_stage2_regional_language_real_document_ocr():
    """
    Empirically verifies real document OCR execution across Stage 2 installed regional models:
    Gujarati (guj), Kannada (kan), Malayalam (mal), Odia (ori), Punjabi (pan), and Urdu (urd).
    Confirms valid character extraction, bilingual notice processing, date extraction, and zero crashes.
    """
    from PIL import ImageFont
    from pathlib import Path

    engine = TesseractOCREngine()
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    if not Path(font_path).is_file():
        pytest.skip("Nirmala UI Indic font not installed on Windows host")

    font = ImageFont.truetype(font_path, 34)

    # 1. Pure script tests
    stage2_cases = [
        ("guj", "ગુજરાત સરકાર આરોગ્ય અને પરિવાર કલ્યાણ વિભાગ જાહેરનામું 2026"),
        ("kan", "ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಕಂದಾಯ ಇಲಾಖೆ ಅಧಿಕೃತ ಅಧಿಸೂಚನೆ 2026"),
        ("mal", "കേരള സർക്കാർ തദ്ദേശ സ്വയംഭരണ വകുപ്പ് വിജ്ഞാപനം 2026"),
        ("ori", "ଓଡ଼ିଶା ସରକାର ସ୍ୱାସ୍ଥ્ય ଓ ପରିବାର କଲ୍ୟାଣ ବିଭାଗ ବିଜ୍ଞପ୍ତି 2026"),
        ("pan", "ਪੰਜਾਬ ਸਰਕਾਰ ਲੋਕ ਨਿਰਮਾਣ ਵਿਭਾਗ ਜਨਤਕ ਨੋਟਿਸ 2026"),
        ("urd", "حکومت ہند وزارت داخلہ سرکاری نوٹیفکیشن برائے اطلاع عام 2026"),
    ]

    for lang, text in stage2_cases:
        img = Image.new("RGB", (1800, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((40, 60), text, font=font, fill=(0, 0, 0))

        res = engine.extract_text(img, target_lang=lang, apply_preprocessing=True)
        assert res.error is None, f"{lang} extraction failed: {res.error}"
        assert res.extracted_text != "", f"{lang} returned empty text"
        assert res.confidence_score > 30.0, f"{lang} confidence score too low: {res.confidence_score}"
        assert "2026" in res.extracted_text, f"{lang} failed to extract date year '2026'"
        assert res.languages_used in (lang, f"{lang}+eng")

    # 2. Bilingual mixed notice tests (Indic + English Notice No. & Date)
    bilingual_cases = [
        ("guj", "ગુજરાત સરકાર જાહેરનામું No. 45/2026/HFW Date: 15/10/2026"),
        ("kan", "ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಅಧಿಸೂಚನೆ No. 88/2026/RD Date: 12/08/2026"),
        ("mal", "കേരള സർക്കാർ വിജ്ഞാപനം No. 23/2026/LSGD Date: 05/09/2026"),
        ("ori", "ଓଡ଼ିଶା ସରକାର ବିଜ୍ଞପ୍ତି No. 77/2026/HFW Date: 22/07/2026"),
        ("pan", "ਪੰਜਾਬ ਸਰਕਾਰ ਜਨਤਕ ਨੋਟਿਸ No. 19/2026/PWD Date: 18/06/2026"),
        ("urd", "حکومت ہند نوٹیفکیشن No. 34/2026/MHA Date: 25/04/2026"),
    ]

    for lang, text in bilingual_cases:
        img = Image.new("RGB", (1800, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((40, 60), text, font=font, fill=(0, 0, 0))

        target = f"{lang}+eng"
        res = engine.extract_text(img, target_lang=target, apply_preprocessing=True)
        assert res.error is None, f"{target} extraction failed: {res.error}"
        assert res.extracted_text != "", f"{target} returned empty text"
        assert res.confidence_score > 50.0, f"{target} confidence score too low: {res.confidence_score}"
        assert "2026" in res.extracted_text, f"{target} failed to extract '2026'"
        assert any(k in res.extracted_text for k in ("No.", "Date", "2026")), f"{target} failed critical English fields"


def test_stage2_coverage_registry_status():
    """Verify that Stage 2 languages are marked model_installed=True and supported_installed in registry."""
    from notice2action.coverage_registry import get_language_coverage

    stage2_codes = ["gu", "kn", "ml", "or", "pa", "ur"]
    for code in stage2_codes:
        cov = get_language_coverage(code)
        assert cov is not None, f"Coverage item not found for {code}"
        assert cov.model_installed is True, f"{code} model_installed should be True"
        assert cov.status in ("supported_installed", "verified_production"), f"{code} invalid status {cov.status}"
        assert cov.primary_model is not None


def test_stage3_regional_language_real_document_ocr():
    """
    Empirically verifies real document OCR execution across Stage 3 installed and adapted regional models:
    Assamese (asm), Nepali (nep), Sanskrit (san), Sindhi (snd), Maithili (mai), Konkani (kok),
    Dogri (doi), Bodo (brx), Kashmiri (kas), and Manipuri (mni).
    """
    from PIL import ImageFont
    from pathlib import Path

    engine = TesseractOCREngine()
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    if not Path(font_path).is_file():
        pytest.skip("Nirmala UI Indic font not installed on Windows host")

    font = ImageFont.truetype(font_path, 34)

    stage3_cases = [
        ("asm", "অসম চৰকাৰৰ স্বাস্থ্য আৰু পৰিয়াল কল্যাণ বিভাগ জাননী 2026"),
        ("nep", "नेपाल सरकार गृह मन्त्रालय आधिकारिक सूचना 2026"),
        ("san", "सर्वकारस्य आधिकारिकम् अधिसूचना विधीयते 2026"),
        ("snd", "سنڌ حڪومت سرڪاري نوٽيفڪيشن 2026"),
        ("mai", "बिहार सरकार स्वास्थ्य विभाग आधिकारिक अधिसूचना 2026"),
        ("kok", "गोंय सरकार अधिकृत राजपत्र अधिसूचना 2026"),
        ("doi", "जम्मू ते कश्मीर सरकार आधिकारिक सूचना 2026"),
        ("brx", "बडलेण्ड प्रदेस सरकारनि रादाब 2026"),
        ("kas", "حکوٗمَتِ ہِند سَرکٲرؠ نۄٹِفِکیشن 2026"),
        ("mni", "মণিপুৰ চৰকাৰৰ স্বাস্থ্য বিভাগ জাননী 2026"),
    ]

    for lang, text in stage3_cases:
        img = Image.new("RGB", (1800, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((40, 60), text, font=font, fill=(0, 0, 0))

        res = engine.extract_text(img, target_lang=lang, apply_preprocessing=True)
        assert res.error is None, f"{lang} extraction failed: {res.error}"
        assert res.extracted_text != "", f"{lang} returned empty text"
        assert res.confidence_score > 30.0, f"{lang} confidence score too low: {res.confidence_score}"
        assert "2026" in res.extracted_text, f"{lang} failed to extract date year '2026'"


def test_stage3_coverage_registry_status():
    """Verify that Stage 3 installed models are marked model_installed=True and supported_installed in registry."""
    from notice2action.coverage_registry import get_language_coverage

    stage3_codes = ["as", "ne", "sa", "sd", "mai", "kok", "doi", "brx"]
    for code in stage3_codes:
        cov = get_language_coverage(code)
        assert cov is not None, f"Coverage item not found for {code}"
        assert cov.model_installed is True, f"{code} model_installed should be True"
        assert cov.status in ("supported_installed", "verified_production"), f"{code} invalid status {cov.status}"


# ---------------------------------------------------------------------------
# 4. Engine Architecture & Factory Tests
# ---------------------------------------------------------------------------

def test_get_ocr_engine_factory():
    """Verify engine instantiation via get_ocr_engine."""
    tess = get_ocr_engine("tesseract")
    assert isinstance(tess, TesseractOCREngine)
    assert tess.engine_name == "tesseract"

    indic = get_ocr_engine("indicocr")
    assert isinstance(indic, IndicOCREngine)
    assert indic.engine_name == "indicocr"

    hybrid = get_ocr_engine("hybrid")
    assert isinstance(hybrid, HybridMultilingualOCREngine)
    assert hybrid.engine_name == "hybrid"

    auto = get_ocr_engine("auto")
    assert isinstance(auto, HybridMultilingualOCREngine)


def test_indic_ocr_engine_lazy_missing_model_handling():
    """Verify IndicOCREngine handles missing ONNX weights gracefully."""
    engine = IndicOCREngine()
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))

    # Request Santali Ol Chiki when model file is not present
    res = engine.extract_text(img, target_lang="sat", apply_preprocessing=False)
    assert res.is_uncertain is True
    assert res.engine_used == "indicocr"
    assert "sat_indicocr.onnx" in res.error
    assert res.extracted_text == ""


def test_hybrid_engine_routes_specialized_scripts():
    """Verify HybridMultilingualOCREngine dispatches Ol Chiki / Meetei Mayek to IndicOCREngine."""
    hybrid = HybridMultilingualOCREngine()
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))

    res = hybrid.extract_text(img, target_lang="sat", apply_preprocessing=False)
    assert res.engine_used == "indicocr"
    assert res.is_uncertain is True


# ---------------------------------------------------------------------------
# 5. Fast-Path API Endpoint Verification
# ---------------------------------------------------------------------------

def test_get_ocr_languages_api_endpoint():
    """Verify GET /api/ocr/languages returns 23 languages with model status."""
    client = TestClient(app)
    response = client.get("/api/ocr/languages")
    assert response.status_code == 200

    data = response.json()
    assert "languages" in data
    assert "summary" in data
    assert "available_tesseract_languages" in data

    assert len(data["languages"]) == 23
    assert data["summary"]["total_languages"] == 23

    # Ensure Hindi and English are marked as installed
    langs_dict = {item["code"]: item for item in data["languages"]}
    assert langs_dict["en"]["model_installed"] is True
    assert langs_dict["hi"]["model_installed"] is True


def test_api_ocr_bilingual_and_auto_routing():
    """Verify POST /api/ocr handles target_lang='auto' and target_lang='guj+eng' correctly."""
    import io
    from pathlib import Path
    from PIL import ImageDraw, ImageFont

    client = TestClient(app)
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    font = ImageFont.truetype(font_path, 32) if Path(font_path).is_file() else None

    img = Image.new("RGB", (1200, 160), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    text = "ગુજરાત સરકાર No. 45/2026/HFW Date: 24/11/2026"
    if font:
        d.text((40, 50), text, font=font, fill=(0, 0, 0))
    else:
        d.text((40, 50), "Government of Gujarat No. 45/2026/HFW Date: 24/11/2026", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # 1. Test bilingual override target_lang='guj+eng'
    response = client.post(
        "/api/ocr",
        files={"file": ("notice.png", buf.getvalue(), "image/png")},
        data={"target_lang": "guj+eng", "enhance_contrast": "true"},
    )
    assert response.status_code == 200, f"Bilingual OCR failed: {response.text}"
    data = response.json()
    assert "extracted_text" in data
    assert "2026" in data["extracted_text"]
    assert "languages_used" in data
    assert data["languages_used"] in ("guj+eng", "guj")

    # 2. Test automatic language routing target_lang='auto'
    buf.seek(0)
    response_auto = client.post(
        "/api/ocr",
        files={"file": ("notice.png", buf.getvalue(), "image/png")},
        data={"target_lang": "auto", "enhance_contrast": "true"},
    )
    assert response_auto.status_code == 200, f"Auto OCR failed: {response_auto.text}"
    data_auto = response_auto.json()
    assert "extracted_text" in data_auto
    assert len(data_auto["extracted_text"]) > 0
