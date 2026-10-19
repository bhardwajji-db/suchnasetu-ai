"""
OCR and Text Extraction Pipeline for Notice2Action AI.
Integrates Tesseract OCR with adaptive image preprocessing, reading order preservation,
and multilingual (English and Hindi) support.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
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
    warning: Optional[str] = None
    error: Optional[str] = None


def get_available_tesseract_languages() -> List[str]:
    """Returns the list of installed language packs in Tesseract."""
    if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
        return []
    try:
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
        langs = pytesseract.get_languages(config="")
        return langs
    except Exception:
        return ["eng"]


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Applies adaptive image preprocessing to improve OCR accuracy on posters/notices:
    1. Converts to grayscale
    2. Rescales if image is too low-resolution (DPI enhancement)
    3. Auto-contrast stretch
    4. Subtle sharpening
    """
    # 1. Grayscale
    gray = image.convert("L")

    # 2. Rescale low-res images (if width < 1200, scale up 1.5x)
    w, h = gray.size
    if w < 1200:
        new_w = int(w * 1.5)
        new_h = int(h * 1.5)
        gray = gray.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 3. Autocontrast
    stretched = ImageOps.autocontrast(gray, cutoff=1)

    # 4. Sharpen slightly to define font edges
    sharpened = stretched.filter(ImageFilter.SHARPEN)

    return sharpened


def extract_text_from_image(
    image: Image.Image,
    target_lang: str = "eng",
    apply_preprocessing: bool = True,
) -> OCRResult:
    """
    Runs Tesseract OCR on an uploaded notice image.
    Supports English ('eng') and Hindi ('hin') if installed.
    Preserves reading order and calculates overall confidence score.
    """
    if not config.tesseract_cmd or not Path(config.tesseract_cmd).is_file():
        return OCRResult(
            extracted_text="",
            confidence_score=0.0,
            languages_used=target_lang,
            line_count=0,
            char_count=0,
            is_preprocessed=False,
            error=(
                f"Tesseract OCR executable not found at '{config.tesseract_cmd}'. "
                "Please install Tesseract or check TESSERACT_CMD in .env."
            ),
        )

    pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd

    # Validate requested language against installed languages
    available_langs = get_available_tesseract_languages()
    chosen_lang = target_lang
    warning_msg = None

    if "hin" in target_lang and "hin" not in available_langs:
        chosen_lang = "eng"
        warning_msg = (
            "Hindi OCR language pack ('hin.traineddata') is not installed in Tesseract. "
            "Falling back to English OCR ('eng'). To enable Hindi OCR, place 'hin.traineddata' in tessdata."
        )

    # Process image
    processed_img = preprocess_image_for_ocr(image) if apply_preprocessing else image

    # Tesseract configuration:
    # --psm 3 (Fully automatic page segmentation with OSD) or --psm 6 (Uniform block of text)
    custom_config = r"--oem 3 --psm 3"

    try:
        # Extract detailed data including confidence scores
        data = pytesseract.image_to_data(
            processed_img,
            lang=chosen_lang,
            config=custom_config,
            output_type=pytesseract.Output.DICT,
        )

        confidences = []
        words = []
        n_boxes = len(data["text"])
        for i in range(n_boxes):
            word = data["text"][i].strip()
            conf = int(data["conf"][i])
            if word and conf > 0:
                words.append(word)
                confidences.append(conf)

        avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0

        # Extract full string preserving layout
        full_text = pytesseract.image_to_string(
            processed_img,
            lang=chosen_lang,
            config=custom_config,
        ).strip()

        line_count = len([line for line in full_text.splitlines() if line.strip()])

        if not full_text:
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                languages_used=chosen_lang,
                line_count=0,
                char_count=0,
                is_preprocessed=apply_preprocessing,
                warning=warning_msg,
                error="No readable text could be extracted from this image. It may be too blurry, blank, or low-contrast.",
            )

        return OCRResult(
            extracted_text=full_text,
            confidence_score=round(avg_conf, 1),
            languages_used=chosen_lang,
            line_count=line_count,
            char_count=len(full_text),
            is_preprocessed=apply_preprocessing,
            warning=warning_msg,
        )

    except Exception as e:
        return OCRResult(
            extracted_text="",
            confidence_score=0.0,
            languages_used=chosen_lang,
            line_count=0,
            char_count=0,
            is_preprocessed=apply_preprocessing,
            error=f"OCR extraction failed: {e}",
        )
