"""
Image generator and degradation transform utilities for Adversarial OCR testing.
Renders synthetic notice text onto high-resolution document canvases, supporting:
- Clean base rendering (English & Hindi Nirmala/Arial fonts)
- Orientation transformations (0, 90, 180, 270, slight skew 5-15 deg)
- Image degradation (Gaussian blur, motion blur, low res, JPEG compression, low contrast, shadows, noise, faded print)
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_PATHS = {
    "en_regular": "C:/Windows/Fonts/arial.ttf",
    "en_bold": "C:/Windows/Fonts/arialbd.ttf",
    "hi_regular": "C:/Windows/Fonts/Nirmala.ttc",
    "hi_bold": "C:/Windows/Fonts/NirmalaB.ttc" if os.path.exists("C:/Windows/Fonts/NirmalaB.ttc") else "C:/Windows/Fonts/Nirmala.ttc"
}

def render_notice_to_image(
    notice: Dict[str, Any],
    width: int = 1200,
    font_size: int = 24,
    bg_color: Tuple[int, int, int] = (255, 255, 255),
    text_color: Tuple[int, int, int] = (20, 20, 20)
) -> Image.Image:
    """Renders notice ground truth text onto a realistic document page."""
    lang = notice.get("language", "en")
    text = notice["text"]

    # Choose font
    if lang in ("hi", "bilingual"):
        font_path = FONT_PATHS["hi_regular"]
        bold_path = FONT_PATHS["hi_bold"]
    else:
        font_path = FONT_PATHS["en_regular"]
        bold_path = FONT_PATHS["en_bold"]

    try:
        font = ImageFont.truetype(font_path, font_size)
        title_font = ImageFont.truetype(bold_path, font_size + 6)
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    # Calculate required height
    lines = text.splitlines()
    line_spacing = int(font_size * 1.5)
    margin_x = 70
    margin_y = 70
    
    # Estimate total height
    content_height = len(lines) * line_spacing + 2 * margin_y + 100
    img_height = max(1400, content_height)

    img = Image.new("RGB", (width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw border or letterhead line
    draw.rectangle([margin_x - 30, margin_y - 30, width - margin_x + 30, img_height - margin_y + 30], outline=(200, 200, 200), width=2)
    draw.line([margin_x, margin_y + 110, width - margin_x, margin_y + 110], fill=(120, 120, 120), width=2)

    current_y = margin_y
    for i, line in enumerate(lines):
        line_str = line.strip()
        if not line_str:
            current_y += int(line_spacing * 0.7)
            continue

        # Header lines formatted bold / larger
        if i < 2:
            draw.text((margin_x, current_y), line_str, fill=text_color, font=title_font)
            current_y += int(line_spacing * 1.3)
        else:
            draw.text((margin_x, current_y), line_str, fill=text_color, font=font)
            current_y += line_spacing

    return img


def apply_orientation(image: Image.Image, degrees: int) -> Image.Image:
    """Rotates image by 0, 90, 180, 270 or arbitrary skew degrees."""
    if degrees == 0:
        return image
    return image.rotate(degrees, expand=True, fillcolor=(255, 255, 255))


def apply_gaussian_blur(image: Image.Image, radius: float = 2.0) -> Image.Image:
    """Applies Gaussian blur degradation."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def apply_motion_blur(image: Image.Image, size: int = 7) -> Image.Image:
    """Simulates linear motion blur in horizontal direction."""
    kernel = np.zeros((size, size))
    kernel[int((size - 1) / 2), :] = np.ones(size)
    kernel = kernel / size
    # Apply via custom Pillow Kernel filter
    kernel_flat = list(kernel.flatten())
    return image.filter(ImageFilter.Kernel((size, size), kernel_flat))


def apply_jpeg_compression(image: Image.Image, quality: int = 15) -> Image.Image:
    """Simulates severe JPEG compression artifacts."""
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return Image.open(buffer).copy()


def apply_low_resolution(image: Image.Image, scale: float = 0.35) -> Image.Image:
    """Downsamples image to simulate low-res / pixelated document scan."""
    w, h = image.size
    small = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    return small.resize((w, h), Image.Resampling.NEAREST)


def apply_low_contrast(image: Image.Image, factor: float = 0.35) -> Image.Image:
    """Reduces contrast to simulate washed-out photocopying."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def apply_faded_print(image: Image.Image, brightness: float = 1.6, contrast: float = 0.4) -> Image.Image:
    """Simulates faint / toner-starved printer output."""
    b_enhancer = ImageEnhance.Brightness(image)
    bright = b_enhancer.enhance(brightness)
    c_enhancer = ImageEnhance.Contrast(bright)
    return c_enhancer.enhance(contrast)


def apply_gaussian_noise(image: Image.Image, sigma: float = 25.0) -> Image.Image:
    """Adds high-frequency additive sensor noise."""
    arr = np.array(image, dtype=np.float32)
    noise = np.random.normal(0, sigma, arr.shape)
    noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)


def apply_shadow_gradient(image: Image.Image) -> Image.Image:
    """Applies an uneven lighting / shadow gradient across the document."""
    w, h = image.size
    # Create horizontal shadow gradient (dark on left, bright on right)
    gradient = np.tile(np.linspace(0.4, 1.0, w), (h, 1))
    arr = np.array(image, dtype=np.float32)
    for c in range(3):
        arr[:, :, c] = arr[:, :, c] * gradient
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def generate_variations_for_notice(
    notice: Dict[str, Any],
    output_dir: Path
) -> List[Dict[str, Any]]:
    """
    Generates pristine and stressed variations for a single notice.
    Returns metadata list for all generated variations.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    base_img = render_notice_to_image(notice)
    notice_id = notice["id"]

    variations = []

    # 1. Pristine baseline (0 deg)
    p_path = output_dir / f"{notice_id}_clean.png"
    base_img.save(p_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_clean",
        "variation_type": "CLEAN_BASELINE",
        "image_path": str(p_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": False
    })

    # 2. 90-degree clockwise rotation
    rot90_img = apply_orientation(base_img, 90)
    rot90_path = output_dir / f"{notice_id}_rot90.png"
    rot90_img.save(rot90_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_rot90",
        "variation_type": "ORIENTATION_90",
        "image_path": str(rot90_path),
        "expected_rotation": 90,
        "is_adversarial_degradation": False
    })

    # 3. 180-degree upside down rotation
    rot180_img = apply_orientation(base_img, 180)
    rot180_path = output_dir / f"{notice_id}_rot180.png"
    rot180_img.save(rot180_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_rot180",
        "variation_type": "ORIENTATION_180",
        "image_path": str(rot180_path),
        "expected_rotation": 180,
        "is_adversarial_degradation": False
    })

    # 4. 270-degree counter-clockwise rotation
    rot270_img = apply_orientation(base_img, 270)
    rot270_path = output_dir / f"{notice_id}_rot270.png"
    rot270_img.save(rot270_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_rot270",
        "variation_type": "ORIENTATION_270",
        "image_path": str(rot270_path),
        "expected_rotation": 270,
        "is_adversarial_degradation": False
    })

    # 5. Skewed / tilted (7 degrees)
    skew_img = apply_orientation(base_img, 7)
    skew_path = output_dir / f"{notice_id}_skew7.png"
    skew_img.save(skew_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_skew7",
        "variation_type": "SKEW_7DEG",
        "image_path": str(skew_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    # 6. Gaussian blur degradation
    blur_img = apply_gaussian_blur(base_img, radius=1.8)
    blur_path = output_dir / f"{notice_id}_blur.png"
    blur_img.save(blur_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_blur",
        "variation_type": "DEGRADATION_GAUSSIAN_BLUR",
        "image_path": str(blur_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    # 7. Low resolution / pixelated
    lowres_img = apply_low_resolution(base_img, scale=0.4)
    lowres_path = output_dir / f"{notice_id}_lowres.png"
    lowres_img.save(lowres_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_lowres",
        "variation_type": "DEGRADATION_LOW_RES",
        "image_path": str(lowres_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    # 8. Severe JPEG compression
    jpeg_img = apply_jpeg_compression(base_img, quality=12)
    jpeg_path = output_dir / f"{notice_id}_jpeg.jpg"
    jpeg_img.save(jpeg_path, format="JPEG")
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_jpeg",
        "variation_type": "DEGRADATION_JPEG_COMPRESSION",
        "image_path": str(jpeg_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    # 9. Low contrast / faded
    faded_img = apply_faded_print(base_img)
    faded_path = output_dir / f"{notice_id}_faded.png"
    faded_img.save(faded_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_faded",
        "variation_type": "DEGRADATION_FADED_PRINT",
        "image_path": str(faded_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    # 10. Shadow & lighting gradient
    shadow_img = apply_shadow_gradient(base_img)
    shadow_path = output_dir / f"{notice_id}_shadow.png"
    shadow_img.save(shadow_path)
    variations.append({
        "notice_id": notice_id,
        "variant_id": f"{notice_id}_shadow",
        "variation_type": "DEGRADATION_SHADOW_GRADIENT",
        "image_path": str(shadow_path),
        "expected_rotation": 0,
        "is_adversarial_degradation": True
    })

    return variations
