"""HTTP integration tests for the fully wired backend pipeline.

Unlike ``backend/tests/api``, these tests do not replace the interpreter, input
validator, A* solver, solution validator, architecture provider, or screenshot
extractor with mocks. Only the RL outcome is controlled where a test must exercise a
specific fallback branch deterministically.
"""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.api.BackendAPI import BackendAPI
from backend.api.architecture_provider.ArchitectureProvider import (
    ArchitectureProvider,
    rl_inference_ready,
)
from backend.api.version import API_VERSION
from backend.input_validation.input_validator import InputValidator
from backend.input_validation.json_interpreter import JsonInterpreter
from backend.input_validation.screenshot import ScreenshotExtractor
from backend.puzzle_logic import Position
from backend.solution_path import SolutionPath
from backend.solving_process.solver_controller import SolverController
from backend.solving_process.solver_metrics import SolverMetrics
from backend.solving_process.solver_result import SolverResult
from backend.solving_process.solver_status import SolverStatus


SOLVABLE_BOARD = {
    "boardSize": 6,
    "waypoints": [[0, 0], [5, 0]],
    "walls": [],
}

UNSOLVABLE_BOARD = {
    "boardSize": 6,
    "waypoints": [[0, 0], [5, 5]],
    "walls": [
        {"neighborA": [0, 0], "neighborB": [1, 0]},
        {"neighborA": [0, 0], "neighborB": [0, 1]},
    ],
}


# Independently transcribed Hamiltonian path for SOLVABLE_BOARD. It visits every
# cell exactly once, starts at waypoint 1, and reaches waypoint 2 only at the end.
VALID_RL_COORDINATES = [
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (4, 1),
    (4, 2),
    (4, 3),
    (4, 4),
    (3, 4),
    (3, 3),
    (3, 2),
    (3, 1),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (1, 4),
    (1, 3),
    (1, 2),
    (1, 1),
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (1, 5),
    (2, 5),
    (3, 5),
    (4, 5),
    (5, 5),
    (5, 4),
    (5, 3),
    (5, 2),
    (5, 1),
    (5, 0),
]


class MissingModelRLSolver:
    """Models the production failure raised when no usable artifact is available."""

    def solve(self, _board):
        raise FileNotFoundError("RL model is unavailable")


class InvalidOutputRLSolver:
    """Returns a non-adjacent path that the real SolutionValidator must reject."""

    def solve(self, _board):
        path = SolutionPath()
        path.add(Position(0, 0))
        path.add(Position(2, 0))
        return SolverResult(
            status=SolverStatus.SOLVED,
            path=path,
            message="Invalid RL candidate",
            metrics=SolverMetrics(runtimeMs=1, steps=1, attempts=1),
        )


class ValidOutputRLSolver:
    """Produces a controlled valid candidate at the real RL/controller boundary."""

    def solve(self, _board):
        path = SolutionPath()
        for x, y in VALID_RL_COORDINATES:
            path.add(Position(x, y))
        return SolverResult(
            status=SolverStatus.SOLVED,
            path=path,
            message="Valid RL candidate",
            metrics=SolverMetrics(runtimeMs=7, steps=36, attempts=1),
        )


def _make_client(rl_solver=None) -> TestClient:
    controller = SolverController(
        rl_solver=rl_solver if rl_solver is not None else MissingModelRLSolver()
    )
    api = BackendAPI(
        JsonInterpreter(),
        InputValidator(),
        controller,
        ArchitectureProvider(build_timestamp="2026-09-05T00:00:00+00:00"),
        ScreenshotExtractor(),
        model_loaded_provider=rl_inference_ready,
    )
    return TestClient(api.app, raise_server_exceptions=False)


@pytest.fixture
def real_client() -> TestClient:
    return _make_client()


def _synthetic_light_screenshot() -> bytes:
    """Create a deterministic 6x6 image consumed by the real CV pipeline.

    The two orange discs deliberately contain no digits. The extractor must retain the
    reliably detected positions, infer their row-major order, and return warnings for the
    unreadable numerals instead of failing the whole import.
    """

    image = Image.new("RGB", (600, 600), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for centre_x in (50, 550):
        radius = 36
        draw.ellipse(
            (
                centre_x - radius,
                50 - radius,
                centre_x + radius,
                50 + radius,
            ),
            fill=(242, 140, 40),
        )

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_health_and_architecture_use_real_runtime_providers(real_client):
    health = real_client.get("/api/health")
    architecture = real_client.get("/api/architecture")

    assert health.status_code == 200
    assert architecture.status_code == 200
    assert health.json()["apiVersion"] == API_VERSION
    assert architecture.json()["apiVersion"] == API_VERSION
    assert health.json()["modelLoaded"] == (
        architecture.json()["reinforcementLearning"]["model"]["loaded"]
    )
    assert {solver["name"] for solver in architecture.json()["solvers"]} == {
        "RLSolver",
        "AlgorithmicSolver",
    }


def test_solve_runs_real_parse_validation_fallback_and_solution_validation(real_client):
    response = real_client.post("/api/solve", json=SOLVABLE_BOARD)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SOLVED"
    assert body["success"] is True
    assert body["solverUsed"] == "AlgorithmicSolver"
    assert len(body["solutionPath"]) == 36
    assert body["solutionPath"][0] == [0, 0]
    assert body["solutionPath"][-1] == [5, 0]


def test_valid_rl_output_passes_real_validation_without_fallback():
    """A valid RL candidate must survive the real SolutionValidator and API adapter.

    This complements the invalid-output fallback test below: together they prove that
    the controller accepts the RL branch only when its candidate is actually valid.
    """

    client = _make_client(ValidOutputRLSolver())

    response = client.post("/api/solve", json=SOLVABLE_BOARD)

    assert response.status_code == 200
    assert response.json() == {
        "status": "SOLVED",
        "success": True,
        "solutionPath": [list(position) for position in VALID_RL_COORDINATES],
        "solverUsed": "RLSolver",
        "message": "Successfully solved using RL Agent.",
        "metrics": {"runtimeMs": 7, "steps": 36, "attempts": 1},
    }


def test_invalid_rl_output_activates_real_a_star_fallback():
    client = _make_client(InvalidOutputRLSolver())

    response = client.post("/api/solve", json=SOLVABLE_BOARD)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SOLVED"
    assert body["solverUsed"] == "AlgorithmicSolver"
    assert len(body["solutionPath"]) == 36


def test_real_rl_solver_missing_model_activates_real_a_star_fallback(
    monkeypatch, tmp_path
):
    """Exercise the production missing-model path instead of simulating its exception."""

    from backend.solving_process import rl_solver as rl_solver_module

    monkeypatch.setitem(
        rl_solver_module.MODEL_PATHS,
        6,
        tmp_path / "missing-6x6-agent.zip",
    )
    client = _make_client(rl_solver_module.RLSolver())

    response = client.post("/api/solve", json=SOLVABLE_BOARD)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SOLVED"
    assert body["success"] is True
    assert body["solverUsed"] == "AlgorithmicSolver"
    assert len(body["solutionPath"]) == 36


def test_real_pipeline_reports_unsolvable_as_http_200(real_client):
    response = real_client.post("/api/solve", json=UNSOLVABLE_BOARD)

    assert response.status_code == 200
    assert response.json() == {
        "status": "UNSOLVABLE",
        "success": False,
        "solutionPath": None,
        "solverUsed": "AlgorithmicSolver",
        "message": "No solution exists for this board.",
        "metrics": {"runtimeMs": 0, "steps": 1, "attempts": 1},
    }


def test_real_pipeline_rejects_invalid_board_before_solving(real_client):
    response = real_client.post(
        "/api/solve",
        json={"boardSize": 5, "waypoints": [[0, 0], [4, 4]], "walls": []},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "UNSUPPORTED_BOARD_SIZE"
    assert body["details"][0]["affectedField"] == "boardSize"


def test_repeated_solve_requests_do_not_leak_state(real_client):
    first = real_client.post("/api/solve", json=SOLVABLE_BOARD).json()
    second = real_client.post("/api/solve", json=SOLVABLE_BOARD).json()

    for field in ("status", "success", "solutionPath", "solverUsed", "message"):
        assert second[field] == first[field]
    assert second["metrics"]["steps"] == first["metrics"]["steps"]
    assert second["metrics"]["attempts"] == first["metrics"]["attempts"]


def test_import_runs_real_image_parse_and_validation_pipeline(real_client):
    response = real_client.post(
        "/api/import",
        files={
            "file": (
                "synthetic-light.png",
                _synthetic_light_screenshot(),
                "image/png",
            )
        },
        data={"board_size": "6"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["board"] == {
        "boardSize": 6,
        "waypoints": [[0, 0], [5, 0]],
        "walls": [],
    }
    assert {warning["code"] for warning in body["warnings"]} == {
        "WAYPOINT_NUMBER_UNREADABLE"
    }


def test_import_rejects_unreadable_image_through_real_pipeline(real_client):
    response = real_client.post(
        "/api/import",
        files={"file": ("broken.png", b"not-an-image", "image/png")},
        data={"board_size": "6"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "MALFORMED_REQUEST"
