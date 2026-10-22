"""
OCR and Text Extraction Pipeline for Notice2Action AI.
Integrates Tesseract OCR with adaptive image preprocessing, reading order preservation,
and multilingual (English and Hindi) support.
Supports modular OCR engine architecture (Tesseract default, RapidOCR optional adapter).
"""

from __future__ import annotations

import abc
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
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
    is_uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    engine_used: str = "tesseract"
    warning: Optional[str] = None
    error: Optional[str] = None


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

        # Process image
        processed_img = preprocess_image_for_ocr(image) if apply_preprocessing else image

        # Tesseract configuration:
        # --psm 3 (Fully automatic page segmentation with OSD)
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
                    is_uncertain=True,
                    uncertainty_reason="No readable text found; image may be blank, blurry, or low contrast.",
                    engine_used="tesseract",
                    warning=warning_msg,
                    error="No readable text could be extracted from this image. It may be too blurry, blank, or low-contrast.",
                )

            is_uncertain = avg_conf < 65.0
            uncertainty_reason = (
                f"Low OCR confidence ({avg_conf:.1f}%). Document contains faint text or noise."
                if is_uncertain
                else None
            )

            return OCRResult(
                extracted_text=full_text,
                confidence_score=round(avg_conf, 1),
                languages_used=chosen_lang,
                line_count=line_count,
                char_count=len(full_text),
                is_preprocessed=apply_preprocessing,
                is_uncertain=is_uncertain,
                uncertainty_reason=uncertainty_reason,
                engine_used="tesseract",
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
            # Graceful fallback to Tesseract
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
                # item format: [box, text, score]
                txt = item[1].strip()
                score = float(item[2])
                if txt:
                    lines.append(txt)
                    scores.append(score * 100)

            full_text = "\n".join(lines)
            avg_conf = (sum(scores) / len(scores)) if scores else 0.0

            return OCRResult(
                extracted_text=full_text,
                confidence_score=round(avg_conf, 1),
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
