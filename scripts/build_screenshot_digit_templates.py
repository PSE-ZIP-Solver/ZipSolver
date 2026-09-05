"""Regenerate the portable screenshot OCR masks; not required to run the app.

From the repository root on Linux, with DejaVu fonts installed:
    uv run python scripts/build_screenshot_digit_templates.py

Sources: Pillow's bundled Aileron font, DejaVu Sans Bold, DejaVu Sans Regular.
Only rasterized digits 0..9 are stored; no screenshot pixels or font files.
The templates are rendered from fonts, independently of the regression images.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.input_validation.screenshot.waypoint_detector import WaypointDetector


def main():
    fonts = [
        ImageFont.load_default(size=80),
        ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80),
        ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80),
    ]
    detector = WaypointDetector()
    templates = {}
    for digit in range(10):
        variants = []
        for font in fonts:
            image = Image.new("L", (120, 140), 0)
            draw = ImageDraw.Draw(image)
            text = str(digit)
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            draw.text(((120 - right + left) / 2 - left, (140 - bottom + top) / 2 - top),
                      text, fill=255, font=font)
            pixels = np.array(image)
            ys, xs = np.where(pixels > 0)
            glyph = pixels[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            variants.append(detector._normalise_glyph(glyph))
        templates[str(digit)] = np.stack(variants).astype(np.uint8)
    destination = (Path(__file__).resolve().parents[1] / "backend" / "input_validation"
                   / "screenshot" / "digit_templates.npz")
    np.savez_compressed(destination, **templates)
    print(destination)


if __name__ == "__main__":
    main()
