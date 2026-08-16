"""Regression coverage for the API hardening pass.

Every test here pins a defect that was live in the dev branch and is now fixed. They are
grouped by the guarantee they protect rather than by endpoint, because several of the
fixes cut across both POST routes.
"""

from __future__ import annotations

import json

import pytest

from backend.api.BackendAPI import (
    ALLOWED_UPLOAD_CONTENT_TYPES,
    MAX_JSON_BODY_BYTES,
    MAX_UPLOAD_BODY_BYTES,
)
from backend.api.dtos.ErrorResponse import ErrorCode
from backend.input_validation.errors import BoardParseError, DuplicateWallError
from backend.input_validation.json_interpreter import JsonInterpreter

from .conftest import IMAGE_UPLOAD, VALID_BODY


# ──────────────────────────────────────────────────────────────────────────────
# Duplicate walls — Board's wall set is lossy, so the rule is only checkable
# against the ordered payload list (see input_validation/errors.py).
# ──────────────────────────────────────────────────────────────────────────────


class TestDuplicateWalls:
    def test_interpreter_rejects_a_repeated_wall(self):
        payload = {
            "boardSize": 6,
            "waypoints": [[0, 0], [5, 5]],
            "walls": [
                {"neighborA": [0, 0], "neighborB": [1, 0]},
                {"neighborA": [0, 0], "neighborB": [1, 0]},
            ],
        }
        with pytest.raises(DuplicateWallError):
            JsonInterpreter.buildBoard(payload)

    def test_reversed_cell_order_is_still_the_same_wall(self):
        """{A,B} and {B,A} are one wall (§5.2). Declaring both is a duplicate."""
        payload = {
            "boardSize": 6,
            "waypoints": [[0, 0], [5, 5]],
            "walls": [
                {"neighborA": [0, 0], "neighborB": [1, 0]},
                {"neighborA": [1, 0], "neighborB": [0, 0]},
            ],
        }
        with pytest.raises(DuplicateWallError):
            JsonInterpreter.buildBoard(payload)

    def test_distinct_walls_are_accepted(self):
        payload = {
            "boardSize": 6,
            "waypoints": [[0, 0], [5, 5]],
            "walls": [
                {"neighborA": [0, 0], "neighborB": [1, 0]},
                {"neighborA": [0, 0], "neighborB": [0, 1]},
            ],
        }
        assert len(JsonInterpreter.buildBoard(payload).getWalls) == 2

    def test_duplicate_wall_error_carries_the_semantic_taxonomy_code(self):
        """It is 422 INVALID_WALLS, not 400: the payload is well-formed, the board is not."""
        error = DuplicateWallError("dup")
        assert error.code == "INVALID_WALLS"
        assert error.http_status == 422
        assert error.affected_field == "walls"
        assert isinstance(error, BoardParseError)
        assert isinstance(error, ValueError)  # legacy callers still catch ValueError

    def test_solve_surfaces_a_duplicate_wall_as_422_invalid_walls(self, make_api):
        """The headline regression: this previously returned 200 with the duplicate
        silently swallowed by Board's wall set."""
        _, client = make_api(interpreter=JsonInterpreter())

        response = client.post(
            "/api/solve",
            json={
                "boardSize": 6,
                "waypoints": [[0, 0], [5, 5]],
                "walls": [
                    {"neighborA": [0, 0], "neighborB": [1, 0]},
                    {"neighborA": [1, 0], "neighborB": [0, 0]},
                ],
            },
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == ErrorCode.INVALID_WALLS.value
        assert body["details"][0]["affectedField"] == "walls"

    def test_a_duplicate_wall_never_reaches_the_solver(self, make_api, solver_controller):
        _, client = make_api(interpreter=JsonInterpreter())

        client.post(
            "/api/solve",
            json={
                "boardSize": 6,
                "waypoints": [[0, 0], [5, 5]],
                "walls": [
                    {"neighborA": [0, 0], "neighborB": [1, 0]},
                    {"neighborA": [0, 0], "neighborB": [1, 0]},
                ],
            },
        )

        solver_controller.solve.assert_not_called()


# ──────────────────────────────────────────────────────────────────────────────
# Payload limits — §3.2.1 "payload limits & content negotiation"
# ──────────────────────────────────────────────────────────────────────────────


class TestPayloadLimits:
    def test_oversized_json_body_is_refused_with_413(self, make_api):
        _, client = make_api()

        oversized = json.dumps(
            {
                "boardSize": 6,
                "waypoints": [[0, 0], [5, 5]],
                "walls": [],
                "padding": "x" * (MAX_JSON_BODY_BYTES + 1024),
            }
        )

        response = client.post(
            "/api/solve",
            content=oversized,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 413
        assert response.json()["code"] == ErrorCode.PAYLOAD_TOO_LARGE.value

    def test_oversized_body_never_reaches_the_interpreter(self, make_api, interpreter):
        """The point of the middleware: refuse before parsing, not after."""
        _, client = make_api()

        client.post(
            "/api/solve",
            content=json.dumps({"padding": "x" * (MAX_JSON_BODY_BYTES + 1024)}),
            headers={"Content-Type": "application/json"},
        )

        interpreter.buildBoard.assert_not_called()

    def test_a_normal_board_is_far_below_the_limit(self, make_api):
        _, client = make_api()
        assert len(json.dumps(VALID_BODY)) < MAX_JSON_BODY_BYTES
        assert client.post("/api/solve", json=VALID_BODY).status_code == 200

    def test_import_gets_a_larger_ceiling_than_json(self):
        """Screenshots are legitimately bigger than board JSON."""
        assert MAX_UPLOAD_BODY_BYTES > MAX_JSON_BODY_BYTES

    def test_import_refuses_an_oversized_upload(self, make_api):
        _, client = make_api()

        response = client.post(
            "/api/import",
            files={
                "file": (
                    "huge.png",
                    b"\x00" * (MAX_UPLOAD_BODY_BYTES + 1),
                    "image/png",
                )
            },
            data={"board_size": "6"},
        )

        assert response.status_code == 413
        assert response.json()["code"] == ErrorCode.PAYLOAD_TOO_LARGE.value


# ──────────────────────────────────────────────────────────────────────────────
# Upload content negotiation
# ──────────────────────────────────────────────────────────────────────────────


class TestUploadContentType:
    @pytest.mark.parametrize(
        "content_type", ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    )
    def test_supported_image_types_are_accepted(self, content_type, make_api):
        _, client = make_api()
        response = client.post(
            "/api/import",
            files={"file": ("board", b"bytes", content_type)},
            data={"board_size": "6"},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "content_type", ["text/plain", "application/pdf", "application/json", ""]
    )
    def test_non_image_uploads_are_rejected_at_the_boundary(
        self, content_type, make_api, screenshot_extractor
    ):
        _, client = make_api()

        response = client.post(
            "/api/import",
            files={"file": ("board.txt", b"not an image", content_type or None)},
            data={"board_size": "6"},
        )

        assert response.status_code == 400
        assert response.json()["code"] == ErrorCode.MALFORMED_REQUEST.value
        # Rejected before any decode work is attempted.
        screenshot_extractor.extract_to_dict.assert_not_called()

    def test_charset_parameter_does_not_defeat_the_check(self, make_api):
        """Browsers may append parameters; only the media type is significant."""
        _, client = make_api()
        response = client.post(
            "/api/import",
            files={"file": ("board.png", b"bytes", "image/png; charset=binary")},
            data={"board_size": "6"},
        )
        assert response.status_code == 200

    def test_allowed_types_are_what_the_pipeline_can_decode(self):
        assert "image/png" in ALLOWED_UPLOAD_CONTENT_TYPES
        assert "image/gif" not in ALLOWED_UPLOAD_CONTENT_TYPES


# ──────────────────────────────────────────────────────────────────────────────
# CORS — both spellings of the Vite dev origin
# ──────────────────────────────────────────────────────────────────────────────


class TestDefaultCorsOrigins:
    @pytest.mark.parametrize(
        "origin", ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    def test_both_loopback_spellings_are_allowed_by_default(self, origin, make_api):
        """Browsers treat these as distinct origins; allowing only one produced CORS
        failures that presented as backend outages."""
        _, client = make_api()

        response = client.post("/api/solve", json=VALID_BODY, headers={"Origin": origin})

        assert response.headers["access-control-allow-origin"] == origin

    def test_an_unknown_origin_is_not_granted_access(self, make_api):
        _, client = make_api()
        response = client.post(
            "/api/solve", json=VALID_BODY, headers={"Origin": "https://evil.example"}
        )
        assert "access-control-allow-origin" not in response.headers


# ──────────────────────────────────────────────────────────────────────────────
# Health readiness — modelLoaded must mean "the RL solver could serve this"
# ──────────────────────────────────────────────────────────────────────────────


class TestModelReadiness:
    def test_readiness_requires_both_an_artifact_and_a_runtime(self, monkeypatch):
        from backend.api.architecture_provider import ArchitectureProvider as module

        monkeypatch.setattr(module, "available_model_sizes", lambda: [6])
        monkeypatch.setattr(module, "rl_runtime_available", lambda: False)
        assert module.rl_inference_ready() is False

        monkeypatch.setattr(module, "available_model_sizes", lambda: [])
        monkeypatch.setattr(module, "rl_runtime_available", lambda: True)
        assert module.rl_inference_ready() is False

        monkeypatch.setattr(module, "available_model_sizes", lambda: [6])
        monkeypatch.setattr(module, "rl_runtime_available", lambda: True)
        assert module.rl_inference_ready() is True

    def test_runtime_probe_does_not_import_the_rl_stack(self, monkeypatch):
        """find_spec, not import: answering the question must not cost the torch import."""
        import sys

        from backend.api.architecture_provider.ArchitectureProvider import (
            rl_runtime_available,
        )

        before = set(sys.modules)
        rl_runtime_available()
        newly_imported = set(sys.modules) - before

        assert not {m for m in newly_imported if m.split(".")[0] == "torch"}

    def test_architecture_model_status_matches_the_health_probe(self, monkeypatch):
        """The two endpoints share one helper and therefore cannot disagree."""
        from backend.api.architecture_provider import ArchitectureProvider as module

        monkeypatch.setattr(module, "available_model_sizes", lambda: [6])
        monkeypatch.setattr(module, "rl_runtime_available", lambda: False)

        info = module.ArchitectureProvider().collect()

        assert info.reinforcement_learning.model.loaded is False
        assert info.reinforcement_learning.model.loaded == module.rl_inference_ready()


# ──────────────────────────────────────────────────────────────────────────────
# Layering — the domain must not depend on the API package
# ──────────────────────────────────────────────────────────────────────────────


class TestLayering:
    def test_input_validation_does_not_import_the_api_package(self):
        source = (
            __import__("pathlib")
            .Path(__file__)
            .resolve()
            .parents[2]
            / "input_validation"
            / "input_validator.py"
        ).read_text()
        assert "backend.api" not in source

    def test_the_re_export_is_the_same_object(self):
        """Both import paths must resolve to one class, or isinstance checks and the
        generated OpenAPI schema would diverge."""
        from backend.api.dtos.ValidationResult import ValidationResult as viaApi
        from backend.input_validation.validation_dtos import ValidationResult as viaDomain

        assert viaApi is viaDomain


# ──────────────────────────────────────────────────────────────────────────────
# Import smoke — the endpoint the new frontend button calls
# ──────────────────────────────────────────────────────────────────────────────


def test_import_returns_the_board_alongside_its_validation_outcome(make_api):
    _, client = make_api()
    response = client.post("/api/import", files=IMAGE_UPLOAD, data={"board_size": "6"})

    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"board", "valid", "message", "errors", "warnings"}