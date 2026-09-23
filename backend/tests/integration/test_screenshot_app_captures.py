"""Real image regression checks for full-page ZipSolver captures.

Board size is explicitly supplied, as in the app's import flow. Expected
waypoint order and walls are manually transcribed; no CV code is mocked.
Derived images test robustness, not independent real-world accuracy.
"""
import json
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageFilter, ImageOps

from backend.input_validation.screenshot import ScreenshotExtractor

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "screenshots"
APP_DATA = json.loads((FIXTURES / "app_expected_boards.json").read_text(encoding="utf-8"))
LEGACY_EXPECTED = json.loads((FIXTURES / "expected_boards.json").read_text(encoding="utf-8"))
LEGACY_MANIFEST = json.loads((FIXTURES / "evaluation_manifest.json").read_text(encoding="utf-8"))
VARIANTS = ["original", "scale75", "scale125", "jpeg65", "blur08", "pad40", "crop12"]


def _variant(payload: bytes, name: str) -> bytes:
    if name == "original":
        return payload
    with Image.open(BytesIO(payload)) as opened:
        image = opened.convert("RGB")
    if name in {"scale75", "scale125"}:
        scale = 0.75 if name == "scale75" else 1.25
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    elif name == "blur08":
        image = image.filter(ImageFilter.GaussianBlur(0.8))
    elif name == "pad40":
        image = ImageOps.expand(image, border=40, fill=(100, 100, 100))
    elif name == "crop12":
        image = image.crop((12, 12, image.width - 12, image.height - 12))
    output = BytesIO()
    if name == "jpeg65":
        image.save(output, format="JPEG", quality=65, optimize=True)
    else:
        image.save(output, format="PNG")
    return output.getvalue()


def _walls(board):
    return {
        tuple(sorted((tuple(wall["neighborA"]), tuple(wall["neighborB"]))))
        for wall in board["walls"]
    }


def _assert_exact(actual, expected):
    assert actual["boardSize"] == expected["boardSize"]
    assert actual["waypoints"] == expected["waypoints"], "Waypoint positions or order differ"
    assert _walls(actual) == _walls(expected), "Missing or extra walls"
    assert len(actual["walls"]) == len(_walls(actual)), "Duplicate walls"
    assert not actual.get("_warnings"), actual.get("_warnings")


@pytest.fixture(scope="module")
def extractor():
    # Reuse one instance across sizes/themes to exercise cached detector state.
    return ScreenshotExtractor()


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("case", APP_DATA["cases"], ids=lambda case: case["file"])
def test_app_capture(extractor, case, variant):
    path = FIXTURES / "app_captures" / case["file"]
    assert path.is_file(), f"Missing fixture: copy the original uploaded PNG to {path}"
    expected = APP_DATA["boards"][case["board"]]
    actual = extractor.extract_to_dict(_variant(path.read_bytes(), variant), expected["boardSize"])
    _assert_exact(actual, expected)


# Keep the established evaluator's exact transformations/backgrounds, including
# all five old failing cases. This imports only its payload helpers, not its
# scoring logic: correctness is asserted independently above.
@pytest.mark.parametrize(
    "case",
    [
        {**base, **variant, "case_id": f"{base['id']}--{variant['id']}"}
        for base in LEGACY_MANIFEST["baseCases"]
        for variant in LEGACY_MANIFEST["variants"]
    ],
    ids=lambda case: case["case_id"],
)
def test_existing_evaluator_image(extractor, case):
    from scripts.evaluate_screenshot_import import _payload

    if case.get("transformation", {}).get("type") == "pad":
        case = {**case, "transformation": {**case["transformation"], "rgb": case["backgroundRgb"]}}
    _, payload, _ = _payload(case, FIXTURES)
    expected = LEGACY_EXPECTED[case["expectedBoardKey"]]
    _assert_exact(extractor.extract_to_dict(payload, expected["boardSize"]), expected)
