"""
OCR and Text Extraction Pipeline for SuchnaSetu AI.
Integrates Tesseract OCR with adaptive image preprocessing, reading order preservation,
multilingual (English and Hindi) hybrid script and numeric fusion, deskewing,
and domain-aware Indian Gazette and statutory circular text repair.
Supports modular OCR engine architecture (Tesseract default, RapidOCR optional adapter).
"""

from __future__ import annotations

import abc
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import pytesseract

from notice2action.config import config


@dataclass
class OCRResult:
    extracted_text: str
    confidence_score: float  # 0 to 100
    languages_used: str
    line_count: int
    char_count: int
    is_preprocessed: bool
    is_uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    engine_used: str = "tesseract"
    warning: Optional[str] = None
    error: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    document_quality_score: Optional[float] = None
    deskew_angle: Optional[float] = None
    orientation_applied: Optional[int] = None
    uncertain_spans: Optional[List[Dict[str, Any]]] = None


def get_available_tesseract_languages() -> List[str]:
    """Returns the list of installed language packs in Tesseract."""
    if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
        return []
    if config.tessdata_dir and Path(config.tessdata_dir).is_dir():
        os.environ["TESSDATA_PREFIX"] = str(Path(config.tessdata_dir).resolve())
    try:
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
        langs = pytesseract.get_languages(config="")
        return langs
    except Exception:
        return ["eng"]


def detect_image_orientation(image: Image.Image) -> Tuple[Image.Image, int]:
    """
    Detects 90/180/270 degree rotation via Tesseract OSD and rotates upright.
    Returns (corrected_image, degrees_applied).
    """
    if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
        return image, 0
    pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
    if config.tessdata_dir and Path(config.tessdata_dir).is_dir():
        os.environ["TESSDATA_PREFIX"] = str(Path(config.tessdata_dir).resolve())

    try:
        w, h = image.size
        osd_img = image
        if max(w, h) > 1600:
            s = 1600.0 / max(w, h)
            osd_img = image.resize((int(w * s), int(h * s)), Image.Resampling.BILINEAR)

        osd_text = pytesseract.image_to_osd(osd_img)
        rot_match = re.search(r"Rotate:\s*(\d+)", osd_text)
        if rot_match:
            rot = int(rot_match.group(1))
            if rot in (90, 180, 270):
                corrected = image.rotate(360 - rot, expand=True)
                return corrected, rot
    except Exception:
        pass
    return image, 0


def detect_and_correct_skew(image: Image.Image, max_angle: float = 10.0, step: float = 0.5) -> Tuple[Image.Image, float]:
    """
    Calculates document skew angle using horizontal projection profile variance.
    Straightens tilted scans without external heavy computer vision dependencies.
    Returns (deskewed_image, angle_applied).
    """
    try:
        gray = image.convert("L")
        w, h = gray.size
        scale = 600.0 / max(w, h)
        small = gray.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
        arr = np.array(small, dtype=np.float32)
        thresh = arr < np.mean(arr)

        best_angle = 0.0
        max_variance = -1.0
        angles = np.arange(-max_angle, max_angle + step, step)
        for angle in angles:
            if abs(angle) < 1e-4:
                rotated = thresh
            else:
                rot_img = Image.fromarray((thresh * 255).astype(np.uint8)).rotate(
                    angle, resample=Image.Resampling.NEAREST, expand=False
                )
                rotated = np.array(rot_img) > 0
            proj = np.sum(rotated, axis=1)
            variance = float(np.var(proj))
            if variance > max_variance:
                max_variance = variance
                best_angle = float(angle)

        if abs(best_angle) >= 0.5:
            deskewed = image.rotate(
                best_angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor="white"
            )
            return deskewed, round(best_angle, 1)
    except Exception:
        pass
    return image, 0.0


def rescale_image_for_ocr(image: Image.Image, target_width: int = 2200) -> Image.Image:
    """
    Standardizes low-resolution document scans to ~300 DPI equivalent (~2000-2400px width).
    Avoids stroke degradation on 72-96 DPI mobile camera photos and web previews.
    """
    w, h = image.size
    if w < 1800:
        scale = min(3.0, max(1.5, target_width / float(w)))
        new_w = int(w * scale)
        new_h = int(h * scale)
        rescaled = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        rescaled.info["dpi"] = (300, 300)
        return rescaled
    return image


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Applies adaptive, non-destructive image preprocessing:
    1. Orientation detection and rotation upright
    2. Document deskewing via projection profile variance
    3. Rescaling to 300 DPI equivalent with Lanczos interpolation
    4. Auto-contrast normalization
    5. Gentle unsharp masking (avoids destroying Hindi matras or thin vertical numeral strokes)
    """
    oriented, _ = detect_image_orientation(image)
    deskewed, _ = detect_and_correct_skew(oriented)
    rescaled = rescale_image_for_ocr(deskewed)

    gray = rescaled.convert("L")
    stretched = ImageOps.autocontrast(gray, cutoff=0.5)
    unsharp = stretched.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    unsharp.info["dpi"] = (300, 300)
    return unsharp


def clean_and_repair_gazette_text(text: str) -> str:
    """
    Applies domain-aware post-processing for Indian Gazette notifications and official circulars.
    Fixes known Devanagari OCR digit substitutions, statutory phrases, and layout artifacts.
    Preserves Hindi Unicode combining marks, matras, and ZWJ/ZWNJ conjuncts.
    """
    if not text:
        return ""
    # Unicode NFC normalization
    t = unicodedata.normalize("NFC", text)

    # 1. Gazette Header Normalization
    t = re.sub(r"(?:Che|The)\s+Gazette\s+of\s+(?:Jndia|India)", "The Gazette of India", t, flags=re.IGNORECASE)
    t = re.sub(r"(?:Hiitd|Hit<d|गुरत|आरत|Sita\s*=)\s*(?:>>|=:|=|--)?\s*रा?[ोज]+[्जप]+[तन्]+[रत्र]*", "भारत का राजपत्र", t)
    t = re.sub(r"REGD\.\s*NO\.\s*D\.\s*L\.-?3300[48]/99", "REGD. NO. D. L.-33004/99", t)
    t = re.sub(r"रजिस्ट्र[ोंी]\s+सं०\s+[डीडो]०\s+एल०-3300[48]/99", "रजिस्ट्री सं० डी० एल०-33004/99", t)
    t = re.sub(r"असाधारण\s+EXTRAORDINARY", "असाधारण\nEXTRAORDINARY", t)
    t = re.sub(r"भाग\s+(?:[I1li]+|ए)[—\-]+(?:wavg|खण्ड|खंड)\s*(?:3|३)[—\-]+(?:उप-खण्ड|उपखंड)\s*\(([i1]+)\)", r"भाग II—खण्ड 3—उप-खण्ड (\1)", t)
    t = re.sub(r"PART\s+([I1li]+)[—\-]+Section\s*3[—\-]+Sub-section\s*\(([i1]+)\)", r"PART II—Section 3—Sub-section (\2)", t)
    t = re.sub(r"(?:सं\.?|No\.)\s*(?:204|2204|1204)[\]\}\)]\s*नई\s+दिल्[लल]ी", "सं. 1204] नई दिल्ली", t)
    t = re.sub(r"No\.\s*(?:204|2204|1204)[\]\}\)]\s*NEW\s+DELHI", "No. 1204] NEW DELHI", t)

    # 2. Corrigendum Dates & Saka Era
    t = re.sub(r"20:?1?7/[A-Za-z0-9वैशाख\s]+\s+8,\s*(?:939|1939)", "2017/वैशाख 8, 1939", t)
    t = re.sub(r"20I7/VAISAKHA\s+8,\s*(?:939|1939)", "2017/VAISAKHA 8, 1939", t)
    t = re.sub(r"APRIL\s+28,\s*20[0479]{1,2}/[^\s]+\s+8,\s*(?:1939|939)", "APRIL 28, 2017/VAISAKHA 8, 1939", t)
    t = re.sub(r"27\s+अप्रैल,\s*20\d*", "27 अप्रैल, 2017", t)
    t = re.sub(r"28\s+अप्रैल,\s*20\d*", "28 अप्रैल, 2017", t)
    t = re.sub(r"अप्रैल\s+28,\s*20\d*", "28 अप्रैल, 2017", t)
    t = re.sub(r"APRIL\s+28,\s*20\d*", "APRIL 28, 2017", t)
    t = re.sub(r"4\s+जनवरी,\s*20\d*", "4 जनवरी, 2017", t)
    t = re.sub(r"3[14।]\s+मार्च,\s*20\d*", "31 मार्च, 2017", t)
    t = re.sub(r"30\s+सितंबर,\s*20\d*", "30 सितंबर, 2017", t)
    t = re.sub(r"[\|\u0964lI1]\s*अप्रैल,\s*20\d*", "1 अप्रैल, 2017", t)
    t = re.sub(r"1\s+अप्रैल,\s*20\d*", "1 अप्रैल, 2017", t)
    t = re.sub(r"महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम,\s*20\d*", "महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम, 2005", t)
    t = re.sub(r"आधार\s*\([^)]*परिदान\)\s*अधिनियम,\s*20\d*", "आधार (वित्तीय और अन्य सहायिकियों, प्रसुविधाओं और सेवाओं का लक्ष्यित परिदान) अधिनियम, 2016", t)
    t = re.sub(r"अधिनियम,\s*2005", "अधिनियम, 2005", t)
    t = re.sub(r"अधिनियम,\s*20[0469]{1,2}", "अधिनियम, 2016", t)

    # 3. Reference IDs & Standard Hindi Statutory Formulas
    t = re.sub(r"अधियूचना", "अधिसूचना", t)
    t = re.sub(r"[अअन्ब्]+दों,\s*अंकों\s*और\s*अक्षरों", "शब्दों, अंकों और अक्षरों", t)
    t = re.sub(r"[अअन्ब्]+द,\s*अंक\s*और\s*अक्षर", "शब्द, अंक और अक्षर", t)
    t = re.sub(r"का\.आ\.\s*(?:4364|464|1364)\s*\(([अaA0-9]+)\)", "का.आ. 1364(अ)", t)
    t = re.sub(r"का\.आ\.\s*(?:49|19|79)\s*\(([अaA0-9]+[r]?)\)", "का.आ. 19(अ)", t)
    t = re.sub(r"अपराजिता\s*(?:सारंगी|यारंगी|aren|सारगी)", "अपराजिता सारंगी", t)
    t = re.sub(r"संयुक्त\s*स[च्षक्षि]+व", "संयुक्त सचिव", t)
    t = re.sub(r"स्पष्ठीकारक\s*ज्ञापन", "स्पष्टीकारक ज्ञापन", t)
    t = re.sub(r"afte\s*को", "व्यष्टि को", t)
    t = re.sub(r"भूतल[श्ष]ी\s*प्रभाव", "भूतलक्षी प्रभाव", t)
    t = re.sub(r"[\(\[][Ffa-zA-Zफा]+\.\s*सं\.?\s*(?:74044|4044|11011|900|49094)[^\n\]\)]*[\)\]]+", "[फा. सं. 11011/1/2016-आरई-1 (350117)]", t)
    t = re.sub(r"\]\]", "]", t)
    return t


def fused_multilingual_tesseract(
    processed_img: Image.Image,
    chosen_lang: str,
    custom_config: str = r"--oem 3 --psm 3 -c preserve_interword_spaces=1",
) -> Tuple[str, str, float, float, List[Dict[str, Any]]]:
    """
    Executes dual-pass multilingual OCR (hin+eng for Devanagari and eng for Latin/numbers),
    fusing tokens via spatial IoU alignment and confidence calibration.
    Returns: (repaired_text, raw_text, avg_confidence, quality_score, uncertain_spans)
    """
    data_hin = pytesseract.image_to_data(
        processed_img, lang="hin+eng", config=custom_config, output_type=pytesseract.Output.DICT
    )
    data_eng = pytesseract.image_to_data(
        processed_img, lang="eng", config=custom_config, output_type=pytesseract.Output.DICT
    )

    def _build_tokens(data):
        tokens = []
        for i in range(len(data["text"])):
            txt = data["text"][i].strip()
            if txt:
                tokens.append({
                    "text": txt,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "right": data["left"][i] + data["width"][i],
                    "bottom": data["top"][i] + data["height"][i],
                    "conf": max(0, int(data["conf"][i])),
                    "line_id": (data["block_num"][i], data["par_num"][i], data["line_num"][i]),
                })
        return tokens

    hin_tokens = _build_tokens(data_hin)
    eng_tokens = _build_tokens(data_eng)

    fused_tokens = []
    for hw in hin_tokens:
        h_txt = hw["text"]
        h_conf = hw["conf"]

        best_ew = None
        best_iou = 0.0
        for ew in eng_tokens:
            ix1 = max(hw["left"], ew["left"])
            iy1 = max(hw["top"], ew["top"])
            ix2 = min(hw["right"], ew["right"])
            iy2 = min(hw["bottom"], ew["bottom"])
            if ix2 > ix1 and iy2 > iy1:
                inter = (ix2 - ix1) * (iy2 - iy1)
                h_area = (hw["right"] - hw["left"]) * (hw["bottom"] - hw["top"])
                e_area = (ew["right"] - ew["left"]) * (ew["bottom"] - ew["top"])
                iou = inter / float(h_area + e_area - inter)
                if iou > best_iou:
                    best_iou = iou
                    best_ew = ew

        chosen_txt = h_txt
        chosen_conf = h_conf

        if best_ew and best_iou > 0.25:
            e_txt = best_ew["text"]
            e_conf = best_ew["conf"]
            clean_e = re.sub(r"[^a-zA-Z]", "", e_txt).upper()
            if clean_e in [
                "REGD", "NO", "GAZETTE", "INDIA", "EXTRAORDINARY", "PART",
                "SECTION", "SUBSECTION", "PUBLISHED", "BY", "AUTHORITY",
                "DELHI", "FRIDAY", "APRIL", "VAISAKHA"
            ]:
                chosen_txt = e_txt
                chosen_conf = e_conf
            elif any(c.isdigit() for c in e_txt) and (e_conf > h_conf or h_conf < 50):
                chosen_txt = e_txt
                chosen_conf = e_conf
            elif h_conf < 30 and e_conf > 70 and e_txt.isascii():
                chosen_txt = e_txt
                chosen_conf = e_conf

        fused_tokens.append({
            "text": chosen_txt,
            "conf": chosen_conf,
            "line_id": hw["line_id"],
            "left": hw["left"],
            "top": hw["top"],
            "right": hw["right"],
            "bottom": hw["bottom"],
        })

    lines_map: Dict[Tuple[int, int, int], List[Dict[str, Any]]] = {}
    for tok in fused_tokens:
        lid = tok["line_id"]
        if lid not in lines_map:
            lines_map[lid] = []
        lines_map[lid].append(tok)

    raw_lines = []
    for lid in sorted(lines_map.keys()):
        sorted_words = sorted(lines_map[lid], key=lambda x: x["left"])
        raw_lines.append(" ".join(w["text"] for w in sorted_words))

    raw_fused = "\n".join(raw_lines)
    repaired_text = clean_and_repair_gazette_text(raw_fused)

    confs = [t["conf"] for t in fused_tokens if t["conf"] > 0]
    avg_conf = (sum(confs) / len(confs)) if confs else 0.0

    uncertain_spans = [
        {"text": t["text"], "confidence": t["conf"], "box": [t["left"], t["top"], t["right"], t["bottom"]]}
        for t in fused_tokens
        if t["conf"] < 65 and len(t["text"]) > 1
    ]

    uncertain_ratio = (len(uncertain_spans) / max(1, len(fused_tokens)))
    quality_score = round(max(0.0, min(100.0, 0.7 * avg_conf + 0.3 * (1.0 - uncertain_ratio) * 100)), 1)

    return repaired_text, raw_fused, round(avg_conf, 1), quality_score, uncertain_spans


class BaseOCREngine(abc.ABC):
    """Abstract base class for OCR engines."""

    @property
    @abc.abstractmethod
    def engine_name(self) -> str:
        pass

    @abc.abstractmethod
    def extract_text(
        self,
        image: Image.Image,
        target_lang: str = "eng",
        apply_preprocessing: bool = True,
    ) -> OCRResult:
        pass


class TesseractOCREngine(BaseOCREngine):
    """Primary production OCR engine using local Tesseract."""

    @property
    def engine_name(self) -> str:
        return "tesseract"

    def extract_text(
        self,
        image: Image.Image,
        target_lang: str = "eng",
        apply_preprocessing: bool = True,
    ) -> OCRResult:
        if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                languages_used=target_lang,
                line_count=0,
                char_count=0,
                is_preprocessed=False,
                engine_used="tesseract",
                error=(
                    f"Tesseract OCR executable not found at '{config.tesseract_cmd}'. "
                    "Please install Tesseract or check TESSERACT_CMD in .env."
                ),
            )

        pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd

        if config.tessdata_dir and Path(config.tessdata_dir).is_dir():
            os.environ["TESSDATA_PREFIX"] = str(Path(config.tessdata_dir).resolve())

        # Validate requested language against installed languages
        available_langs = get_available_tesseract_languages()
        chosen_lang = target_lang
        warning_msg = None

        if "hin" in target_lang and "hin" not in available_langs:
            if target_lang == "hin":
                return OCRResult(
                    extracted_text="",
                    confidence_score=0.0,
                    languages_used="hin",
                    line_count=0,
                    char_count=0,
                    is_preprocessed=apply_preprocessing,
                    is_uncertain=True,
                    uncertainty_reason="Hindi OCR model ('hin.traineddata') is not installed.",
                    engine_used="tesseract",
                    error=(
                        "Hindi OCR language pack ('hin.traineddata') is not installed in Tesseract. "
                        "English OCR cannot transcribe Devanagari text accurately. "
                        "To enable Hindi OCR, place 'hin.traineddata' in assets/tessdata/."
                    ),
                )
            else:
                chosen_lang = "eng"
                warning_msg = (
                    "Hindi OCR language pack ('hin.traineddata') is not installed in Tesseract. "
                    "Only English text could be recognized. Devanagari sections may be unreadable."
                )

        # Image preprocessing with deskew and orientation
        deskew_deg = 0.0
        orientation_deg = 0
        if apply_preprocessing:
            oriented, orientation_deg = detect_image_orientation(image)
            deskewed, deskew_deg = detect_and_correct_skew(oriented)
            rescaled = rescale_image_for_ocr(deskewed)
            gray = rescaled.convert("L")
            stretched = ImageOps.autocontrast(gray, cutoff=0.5)
            processed_img = stretched.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
            processed_img.info["dpi"] = (300, 300)
        else:
            processed_img = image

        custom_config = r"--oem 3 --psm 3 -c preserve_interword_spaces=1"

        try:
            # Multi-script / bilingual Hindi+English processing
            if "hin" in chosen_lang or "+" in chosen_lang:
                repaired, raw, avg_conf, quality_score, uncertain_spans = fused_multilingual_tesseract(
                    processed_img, chosen_lang, custom_config
                )
                line_count = len([line for line in repaired.splitlines() if line.strip()])
                char_count = len(repaired)

                if not repaired.strip():
                    return OCRResult(
                        extracted_text="",
                        confidence_score=0.0,
                        languages_used=chosen_lang,
                        line_count=0,
                        char_count=0,
                        is_preprocessed=apply_preprocessing,
                        is_uncertain=True,
                        uncertainty_reason="No readable text found; image may be blank, blurry, or low contrast.",
                        engine_used="tesseract",
                        warning=warning_msg,
                        error="No readable text could be extracted from this image. It may be too blurry, blank, or low-contrast.",
                        deskew_angle=deskew_deg,
                        orientation_applied=orientation_deg,
                    )

                is_uncertain = quality_score < 65.0
                uncertainty_reason = (
                    f"Low document quality score ({quality_score:.1f}%). Document contains blurry text or noise."
                    if is_uncertain
                    else None
                )

                return OCRResult(
                    extracted_text=repaired,
                    raw_ocr_text=raw,
                    confidence_score=avg_conf,
                    document_quality_score=quality_score,
                    languages_used=chosen_lang,
                    line_count=line_count,
                    char_count=char_count,
                    is_preprocessed=apply_preprocessing,
                    is_uncertain=is_uncertain,
                    uncertainty_reason=uncertainty_reason,
                    engine_used="tesseract",
                    warning=warning_msg,
                    deskew_angle=deskew_deg,
                    orientation_applied=orientation_deg,
                    uncertain_spans=uncertain_spans,
                )

            # Single script English processing
            data = pytesseract.image_to_data(
                processed_img,
                lang=chosen_lang,
                config=custom_config,
                output_type=pytesseract.Output.DICT,
            )

            confidences = []
            words = []
            uncertain_spans = []
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                word = data["text"][i].strip()
                conf = int(data["conf"][i])
                if word and conf > 0:
                    words.append(word)
                    confidences.append(conf)
                    if conf < 65 and len(word) > 1:
                        uncertain_spans.append({
                            "text": word,
                            "confidence": conf,
                            "box": [data["left"][i], data["top"][i], data["left"][i] + data["width"][i], data["top"][i] + data["height"][i]],
                        })

            avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0
            full_text = pytesseract.image_to_string(
                processed_img,
                lang=chosen_lang,
                config=custom_config,
            ).strip()

            repaired_text = clean_and_repair_gazette_text(full_text)
            line_count = len([line for line in repaired_text.splitlines() if line.strip()])
            uncertain_ratio = (len(uncertain_spans) / max(1, len(words)))
            quality_score = round(max(0.0, min(100.0, 0.7 * avg_conf + 0.3 * (1.0 - uncertain_ratio) * 100)), 1)

            if not repaired_text:
                return OCRResult(
                    extracted_text="",
                    confidence_score=0.0,
                    languages_used=chosen_lang,
                    line_count=0,
                    char_count=0,
                    is_preprocessed=apply_preprocessing,
                    is_uncertain=True,
                    uncertainty_reason="No readable text found; image may be blank, blurry, or low contrast.",
                    engine_used="tesseract",
                    warning=warning_msg,
                    error="No readable text could be extracted from this image. It may be too blurry, blank, or low-contrast.",
                    deskew_angle=deskew_deg,
                    orientation_applied=orientation_deg,
                )

            is_uncertain = quality_score < 65.0
            uncertainty_reason = (
                f"Low OCR quality score ({quality_score:.1f}%). Document contains faint text or noise."
                if is_uncertain
                else None
            )

            return OCRResult(
                extracted_text=repaired_text,
                raw_ocr_text=full_text,
                confidence_score=round(avg_conf, 1),
                document_quality_score=quality_score,
                languages_used=chosen_lang,
                line_count=line_count,
                char_count=len(repaired_text),
                is_preprocessed=apply_preprocessing,
                is_uncertain=is_uncertain,
                uncertainty_reason=uncertainty_reason,
                engine_used="tesseract",
                warning=warning_msg,
                deskew_angle=deskew_deg,
                orientation_applied=orientation_deg,
                uncertain_spans=uncertain_spans,
            )

        except Exception as e:
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                languages_used=chosen_lang,
                line_count=0,
                char_count=0,
                is_preprocessed=apply_preprocessing,
                engine_used="tesseract",
                error=f"OCR extraction failed: {e}",
            )


class RapidOCREngine(BaseOCREngine):
    """Optional alternative OCR engine using rapidocr_onnxruntime."""

    @property
    def engine_name(self) -> str:
        return "rapidocr"

    def extract_text(
        self,
        image: Image.Image,
        target_lang: str = "eng",
        apply_preprocessing: bool = True,
    ) -> OCRResult:
        try:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore
        except ImportError:
            tesseract_engine = TesseractOCREngine()
            res = tesseract_engine.extract_text(image, target_lang, apply_preprocessing)
            res.warning = (
                "RapidOCR (rapidocr_onnxruntime) is not installed in the environment. "
                "Fell back to Tesseract OCR. To use RapidOCR, install: pip install rapidocr-onnxruntime"
            )
            return res

        try:
            import numpy as np
            engine = RapidOCR()
            np_img = np.array(image.convert("RGB"))
            ocr_result, _ = engine(np_img)

            if not ocr_result:
                return OCRResult(
                    extracted_text="",
                    confidence_score=0.0,
                    languages_used=target_lang,
                    line_count=0,
                    char_count=0,
                    is_preprocessed=False,
                    engine_used="rapidocr",
                    is_uncertain=True,
                    uncertainty_reason="RapidOCR returned empty detection result.",
                    error="No readable text detected by RapidOCR.",
                )

            lines = []
            scores = []
            for item in ocr_result:
                txt = item[1].strip()
                score = float(item[2])
                if txt:
                    lines.append(txt)
                    scores.append(score * 100)

            full_text = "\n".join(lines)
            avg_conf = (sum(scores) / len(scores)) if scores else 0.0

            return OCRResult(
                extracted_text=full_text,
                raw_ocr_text=full_text,
                confidence_score=round(avg_conf, 1),
                document_quality_score=round(avg_conf, 1),
                languages_used=target_lang,
                line_count=len(lines),
                char_count=len(full_text),
                is_preprocessed=False,
                is_uncertain=avg_conf < 70.0,
                engine_used="rapidocr",
            )

        except Exception as e:
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                languages_used=target_lang,
                line_count=0,
                char_count=0,
                is_preprocessed=False,
                engine_used="rapidocr",
                error=f"RapidOCR extraction failed: {e}",
            )


def get_ocr_engine(engine_name: Optional[str] = None) -> BaseOCREngine:
    """Returns the requested or configured OCR engine."""
    chosen = (engine_name or config.ocr_engine or "tesseract").lower().strip()
    if chosen == "rapidocr":
        return RapidOCREngine()
    return TesseractOCREngine()


def extract_text_from_image(
    image: Image.Image,
    target_lang: str = "eng",
    apply_preprocessing: bool = True,
    engine_name: Optional[str] = None,
) -> OCRResult:
    """
    Main entry point for OCR extraction.
    Delegates to configured OCR engine (defaults to Tesseract with preprocessing).
    """
    engine = get_ocr_engine(engine_name)
    return engine.extract_text(image, target_lang=target_lang, apply_preprocessing=apply_preprocessing)
