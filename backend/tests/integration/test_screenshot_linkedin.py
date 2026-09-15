"""LinkedIn import: real CV, exact manually transcribed boards and API uploads.

Twelve captures represent eleven distinct boards. Derivatives are correlated
robustness checks, not an independent accuracy sample. A board-size hint is
supplied, as in the frontend. No screenshot detector is mocked.
"""
import json
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from backend.api.BackendAPI import BackendAPI
from backend.input_validation.input_validator import InputValidator
from backend.input_validation.json_interpreter import JsonInterpreter
from backend.input_validation.screenshot import ScreenshotExtractor
from backend.input_validation.screenshot.screenshot_errors import NoBoardDetectedError
from backend.solving_process.solver_controller import SolverController

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "screenshots"
DATA = json.loads((FIXTURES / "linkedin_expected_boards.json").read_text(encoding="utf-8"))
VARIANTS = ["original", "scale75", "scale125", "jpeg65", "blur08", "pad40", "crop12"]


def _encode(image, fmt="PNG", **options):
    stream = BytesIO()
    image.save(stream, format=fmt, **options)
    return stream.getvalue()


def _payload(case, variant):
    path = FIXTURES / "linkedin_captures" / case["file"]
    assert path.is_file(), f"Missing fixture: copy the supplied screenshot to {path}"
    raw = path.read_bytes()
    if variant == "original":
        return raw
    with Image.open(BytesIO(raw)) as opened:
        image = opened.convert("RGB")
    if variant in {"scale75", "scale125"}:
        scale = 0.75 if variant == "scale75" else 1.25
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    elif variant == "jpeg65":
        return _encode(image, "JPEG", quality=65, optimize=True)
    elif variant == "blur08":
        image = image.filter(ImageFilter.GaussianBlur(0.8))
    elif variant == "pad40":
        image = ImageOps.expand(image, border=40, fill=(240, 240, 240))
    elif variant == "crop12":
        image = image.crop((12, 12, image.width - 12, image.height - 12))
    return _encode(image)


def _assert_board(actual, expected):
    assert actual["boardSize"] == expected["boardSize"]
    assert actual["waypoints"] == expected["waypoints"], "Waypoint positions/order differ"
    def edges(board):
        return {tuple(sorted((tuple(w["neighborA"]), tuple(w["neighborB"])))) for w in board["walls"]}
    assert edges(actual) == edges(expected), "Missing or extra walls"
    assert len(actual["walls"]) == len(expected["walls"])


@pytest.fixture(scope="module")
def extractor():
    return ScreenshotExtractor()


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda c: c["board"])
@pytest.mark.parametrize("variant", VARIANTS)
def test_linkedin_capture(extractor, case, variant):
    expected = DATA["boards"][case["board"]]
    actual = extractor.extract_to_dict(_payload(case, variant), expected["boardSize"])
    _assert_board(actual, expected)
    assert actual["_warnings"] == []


class _UnusedRLSolver:
    def solve(self, _board):
        raise AssertionError("Screenshot import must not invoke a puzzle solver")


@pytest.fixture(scope="module")
def client():
    api = BackendAPI(
        JsonInterpreter(), InputValidator(),
        SolverController(rl_solver=_UnusedRLSolver()),
        screenshot_extractor=ScreenshotExtractor(),
    )
    with TestClient(api.app, raise_server_exceptions=False) as client:
        yield client


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda c: c["board"])
def test_linkedin_import_endpoint(client, case):
    expected = DATA["boards"][case["board"]]
    mime = "image/jpeg" if case["file"].endswith(".jpeg") else "image/png"
    response = client.post(
        "/api/import", files={"file": (case["file"], _payload(case, "original"), mime)},
        data={"board_size": str(expected["boardSize"])},
    )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["valid"] is True, result
    assert result["warnings"] == []
    _assert_board(result["board"], expected)


def test_markers_without_grid_are_rejected(extractor):
    image = Image.new("RGB", (600, 600), "white")
    draw = ImageDraw.Draw(image)
    for x, digit in [(150, "1"), (450, "2")]:
        draw.ellipse((x-30, 270, x+30, 330), fill="black")
        draw.text((x-3, 294), digit, fill="white")
    with pytest.raises(NoBoardDetectedError):
        extractor.extract_to_dict(_encode(image), 6)


def test_switching_between_app_and_linkedin_resets_detection(extractor):
    expected_app = json.loads((FIXTURES / "expected_boards.json").read_text(encoding="utf-8"))
    for name in ["6x6-light", "8x8-dark"]:
        for _ in range(2):
            app = expected_app[name[:3]]
            _assert_board(extractor.extract_to_dict((FIXTURES / f"{name}.png").read_bytes(), app["boardSize"]), app)
            case = DATA["cases"][1]
            expected = DATA["boards"][case["board"]]
            _assert_board(extractor.extract_to_dict(_payload(case, "original"), expected["boardSize"]), expected)
