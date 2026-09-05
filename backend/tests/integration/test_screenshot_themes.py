"""Real user screenshots: exact numbered waypoints and walls in both themes.

Expected boards were transcribed from the images, using backend [x, y]
coordinates. These are development regression fixtures, not an independent
accuracy evaluation corpus. No computer vision components are mocked.
"""

import json
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageFont

from backend.api.BackendAPI import BackendAPI
from backend.input_validation.input_validator import InputValidator
from backend.input_validation.json_interpreter import JsonInterpreter
from backend.input_validation.screenshot import ScreenshotExtractor
from backend.solving_process.solver_controller import SolverController

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "screenshots"
EXPECTED = json.loads((FIXTURES / "expected_boards.json").read_text())


class _MissingModelRLSolver:
    """Keep the client deterministic if a solve route is exercised accidentally."""

    def solve(self, _board):
        raise FileNotFoundError("RL model is unavailable")


def _make_client() -> TestClient:
    """Build the real screenshot-import pipeline without importing another test."""

    api = BackendAPI(
        JsonInterpreter(),
        InputValidator(),
        SolverController(rl_solver=_MissingModelRLSolver()),
        screenshot_extractor=ScreenshotExtractor(),
    )
    return TestClient(api.app, raise_server_exceptions=False)


def assert_board(actual, expected):
    assert actual["boardSize"] == expected["boardSize"]
    assert actual["waypoints"] == expected["waypoints"]

    def edges(board):
        return {
            tuple(sorted((tuple(w["neighborA"]), tuple(w["neighborB"]))))
            for w in board["walls"]
        }

    assert edges(actual) == edges(expected)
    assert len(actual["walls"]) == len(expected["walls"])


@pytest.mark.parametrize("size", ["6x6", "8x8"])
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("via_http", [False, True], ids=["extractor", "http"])
def test_real_screenshot_preserves_number_order_and_every_wall(size, theme, via_http):
    expected = EXPECTED[size]
    payload = (FIXTURES / f"{size}-{theme}.png").read_bytes()
    if via_http:
        with _make_client() as client:
            response = client.post(
                "/api/import",
                files={"file": (f"{size}-{theme}.png", payload, "image/png")},
                data={"board_size": str(expected["boardSize"])},
            )
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["valid"] is True
        assert result["warnings"] == []
        actual = result["board"]
    else:
        actual = ScreenshotExtractor().extract_to_dict(payload, expected["boardSize"])
        assert actual["_warnings"] == []
    assert_board(actual, expected)


def test_alternating_sizes_and_themes_do_not_reuse_previous_detection():
    extractor = ScreenshotExtractor()
    for size, theme in [
        ("6x6", "dark"),
        ("8x8", "light"),
        ("8x8", "dark"),
        ("6x6", "light"),
    ]:
        expected = EXPECTED[size]
        actual = extractor.extract_to_dict(
            (FIXTURES / f"{size}-{theme}.png").read_bytes(), expected["boardSize"]
        )
        assert actual["_warnings"] == []
        assert_board(actual, expected)


@pytest.mark.parametrize("name", ["6x6-light", "6x6-dark", "8x8-light", "8x8-dark"])
def test_templates_work_without_system_fonts_and_outside_repo(
    name, monkeypatch, tmp_path
):
    def no_fonts(*args, **kwargs):
        raise OSError("System fonts are unavailable")

    monkeypatch.setattr(ImageFont, "truetype", no_fonts)
    monkeypatch.chdir(tmp_path)
    expected = EXPECTED[name[:3]]
    actual = ScreenshotExtractor().extract_to_dict(
        (FIXTURES / f"{name}.png").read_bytes(), expected["boardSize"]
    )
    assert actual["_warnings"] == []
    assert_board(actual, expected)


@pytest.mark.parametrize("background", ["#2f2419", "#fff9f1"], ids=["dark", "light"])
def test_plain_theme_coloured_image_is_not_a_board(background):
    output = BytesIO()
    Image.new("RGB", (600, 600), background).save(output, format="PNG")
    with _make_client() as client:
        response = client.post(
            "/api/import",
            files={"file": ("blank.png", output.getvalue(), "image/png")},
            data={"board_size": "6"},
        )
    assert response.status_code == 422
    assert response.json()["code"] == "NO_BOARD_DETECTED"
