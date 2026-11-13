import os
import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from notice2action.ocr import detect_image_orientation, extract_text_from_image
from notice2action.config import config


@pytest.fixture(scope="module")
def sample_short_notice():
    """Generates a realistic 3-line public notice image that fails standard OSD."""
    img = Image.new("RGB", (1600, 500), color="white")
    d = ImageDraw.Draw(img)
    d.text((100, 100), "OFFICE OF THE DISTRICT MAGISTRATE NOTICE", fill="black")
    d.text((100, 200), "ALL CITIZENS ARE HEREBY INFORMED THAT SCHOLARSHIPS", fill="black")
    d.text((100, 300), "LAST DATE OF SUBMISSION IS 30TH NOVEMBER 2026", fill="black")
    return img


@pytest.fixture(scope="module")
def sample_hindi_notice():
    """Generates a 3-line Hindi public notice image."""
    img = Image.new("RGB", (1600, 500), color="white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("mangal.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    d.text((100, 100), "जिलाधिकारी कार्यालय अधिसूचना", font=font, fill="black")
    d.text((100, 200), "सर्वसाधारण को सूचित किया जाता है छात्रवृत्ति आवेदन", font=font, fill="black")
    d.text((100, 300), "अंतिम तिथि 30 नवंबर 2026 निर्धारित है", font=font, fill="black")
    return img


@pytest.mark.parametrize("angle", [0, 90, 180, 270])
def test_short_notice_all_four_orientations(sample_short_notice, angle):
    """Verifies that short notices (<4 lines) recover accurately from all 4 rotations."""
    rotated_input = sample_short_notice.rotate(angle, expand=True)
    corrected_img, detected_rot = detect_image_orientation(rotated_input)

    assert detected_rot == angle, f"Expected rotation {angle}, but detected {detected_rot}"
    # Verification: corrected image dimensions match original orientation (width > height)
    assert corrected_img.size[0] > corrected_img.size[1]

    # Verify downstream OCR readability
    ocr_result = extract_text_from_image(corrected_img)
    assert "DISTRICT" in ocr_result.raw_ocr_text.upper() or "NOTICE" in ocr_result.raw_ocr_text.upper()


@pytest.mark.parametrize("angle", [0, 90, 180, 270])
def test_gazette_long_document_all_four_orientations(angle):
    """Verifies that full-page real scans recover accurately from all 4 rotations."""
    fixture_path = "tests/fixtures/gazette_corrigendum_2017.jpeg"
    if not os.path.exists(fixture_path):
        pytest.skip("Gazette fixture not found")
    
    gazette_img = Image.open(fixture_path)
    rotated_input = gazette_img.rotate(angle, expand=True)
    corrected_img, detected_rot = detect_image_orientation(rotated_input)

    assert detected_rot == angle, f"Expected rotation {angle}, but detected {detected_rot}"
    # Gazette original is portrait: height > width
    assert corrected_img.size[1] > corrected_img.size[0]


@pytest.mark.parametrize("angle", [0, 90, 180, 270])
def test_synthetic_scholarship_notice_all_four_orientations(angle):
    """Verifies that synthetic multi-paragraph circular recovers accurately from all 4 rotations."""
    fixture_path = "tests/fixtures/synthetic_scholarship_notice.png"
    if not os.path.exists(fixture_path):
        pytest.skip("Synthetic scholarship notice fixture not found")

    img = Image.open(fixture_path)
    rotated_input = img.rotate(angle, expand=True)
    corrected_img, detected_rot = detect_image_orientation(rotated_input)

    assert detected_rot == angle, f"Expected rotation {angle}, but detected {detected_rot}"
    # Synthetic notice is landscape: width > height
    assert corrected_img.size[0] > corrected_img.size[1]


@pytest.mark.parametrize("angle", [0, 90, 180, 270])
def test_hindi_notice_all_four_orientations(sample_hindi_notice, angle):
    """Verifies orientation detection on Hindi Devanagari script notices."""
    rotated_input = sample_hindi_notice.rotate(angle, expand=True)
    corrected_img, detected_rot = detect_image_orientation(rotated_input)

    assert detected_rot == angle, f"Expected rotation {angle}, but detected {detected_rot}"
    assert corrected_img.size[0] > corrected_img.size[1]


def test_blank_image_no_false_rotation():
    """Verifies that blank or nearly blank images are not erroneously rotated."""
    blank = Image.new("RGB", (1200, 800), color="white")
    for angle in [0, 90, 180, 270]:
        rotated = blank.rotate(angle, expand=True)
        corrected_img, detected_rot = detect_image_orientation(rotated)
        assert detected_rot == 0, f"Blank image should not be rotated, got {detected_rot}"


def test_already_correct_orientation_preservation(sample_short_notice):
    """Verifies that an already correctly oriented document is untouched (0 degrees applied)."""
    corrected_img, detected_rot = detect_image_orientation(sample_short_notice)
    assert detected_rot == 0
    assert corrected_img.size == sample_short_notice.size


@pytest.mark.parametrize("angle", [90, 180, 270])
def test_bounding_box_alignment_across_all_rotations(angle):
    """
    Verifies that when a rotated document (90°, 180°, 270°) is corrected by detect_image_orientation,
    downstream OCR extracted word bounding boxes perfectly align with the original upright coordinates.
    """
    w, h = 1200, 400
    base_img = Image.new("RGB", (w, h), color="white")
    draw = ImageDraw.Draw(base_img)
    draw.text((100, 150), "SCHOLARSHIP", fill="black")

    # Upright baseline extraction
    base_res = extract_text_from_image(base_img)
    base_word_boxes = [b for b in (base_res.word_boxes or []) if "SCHOLARSHIP" in b["text"].upper()]
    assert len(base_word_boxes) > 0, "Base image did not detect SCHOLARSHIP"
    expected_box = base_word_boxes[0]["box"]

    # Rotate input by angle (counter-clockwise by angle in PIL)
    rotated_input = base_img.rotate(angle, expand=True)
    corrected_img, detected_rot = detect_image_orientation(rotated_input)

    assert detected_rot == angle, f"Expected detected rotation {angle}, got {detected_rot}"
    assert corrected_img.size == base_img.size, f"Corrected image size {corrected_img.size} mismatch with original {base_img.size}"

    # Extract OCR from corrected image
    corr_res = extract_text_from_image(corrected_img)
    corr_word_boxes = [b for b in (corr_res.word_boxes or []) if "SCHOLARSHIP" in b["text"].upper()]
    assert len(corr_word_boxes) > 0, f"Corrected image ({angle} deg) failed to detect SCHOLARSHIP"
    actual_box = corr_word_boxes[0]["box"]

    # Ensure box coordinate delta <= 2 pixels (tolerance for discrete raster rotation interpolation)
    for coord_idx, (exp, act) in enumerate(zip(expected_box, actual_box)):
        assert abs(exp - act) <= 2, (
            f"Rot {angle} deg: box coord {coord_idx} drifted! Expected {exp}, got {act}. "
            f"Expected full box: {expected_box}, actual full box: {actual_box}"
        )

