"""§8.2.1 Endpoint Integration Tests — pytest + FastAPI TestClient.

Scope: routing, request parsing into DTOs, response serialisation, HTTP status codes,
and the full request lifecycle from incoming JSON to final response object.

These tests exercise the app through HTTP. Pure schema assertions live in
``test_contract_validation.py``; call-ordering assertions live in
``test_orchestration_flow.py``.
"""

from __future__ import annotations

import pytest

from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.api.version import API_VERSION

from backend.tests.api.conftest import (
    REFERENCE_BOARD,
    VALID_BODY,
    make_path,
    make_solver_result,
    make_validation_result,
)

# ──────────────────────────────────────────────────────────────────────────────
# Route registration — the four endpoints of §3.2.1
# ──────────────────────────────────────────────────────────────────────────────


def test_all_four_documented_endpoints_are_registered(make_api):
    """§3.2.1 specifies exactly four public endpoints. Guards against a route being
    silently dropped, and against the class of regression where a provider package
    exists but was never wired to a router."""
    api, _ = make_api()
    registered = {
        (method, route.path)
        for route in api.app.routes
        if getattr(route, "methods", None)
        for method in route.methods
        if route.path.startswith("/api")
    }
    assert registered == {
        ("POST", "/api/solve"),
        ("POST", "/api/import"),
        ("GET", "/api/health"),
        ("GET", "/api/architecture"),
    }


@pytest.mark.parametrize(
    ("method", "path"),
    [("GET", "/api/solve"), ("GET", "/api/import"), ("POST", "/api/health"), ("POST", "/api/architecture")],
)
def test_wrong_http_verb_is_rejected(client, method, path):
    """Verb/path pairs outside the contract must not be silently accepted."""
    assert client.request(method, path).status_code == 405


def test_unknown_route_returns_404(client):
    assert client.get("/api/does-not-exist").status_code == 404


def test_openapi_schema_is_generated(client):
    """The OpenAPI contract is the frontend's source of truth (§3.2.1 cross-cutting)."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["version"] == API_VERSION
    assert set(schema["paths"]) >= {
        "/api/solve",
        "/api/import",
        "/api/health",
        "/api/architecture",
    }


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/solve
# ──────────────────────────────────────────────────────────────────────────────


def test_solve_returns_200_with_full_solver_response(client):
    response = client.post("/api/solve", json=VALID_BODY)
    assert response.status_code == 200

    body = response.json()
    assert body == {
        "status": "SOLVED",
        "success": True,
        "solutionPath": [[0, 0], [0, 1], [0, 2]],
        "solverUsed": "RL",
        "message": "Solved by RL agent.",
        "metrics": {"runtimeMs": 142, "steps": 36, "attempts": 1},
    }


def test_solve_parses_body_into_puzzle_request_dto(client, interpreter):
    """The interpreter must receive a parsed ``PuzzleRequest``, never a raw dict —
    this is the trust boundary in §3.2.1: no raw input reaches the core."""
    client.post("/api/solve", json=VALID_BODY)

    (request_arg,), _ = interpreter.buildBoard.call_args
    assert type(request_arg).__name__ == "PuzzleRequest"
    assert request_arg.board_size == 6
    assert request_arg.waypoints == [(0, 0), (2, 2), (5, 5)]
    assert request_arg.walls[0].neighbor_a == (0, 0)
    assert request_arg.walls[0].neighbor_b == (1, 0)


def test_solve_passes_interpreter_board_to_solver(client, interpreter, solver_controller):
    """The object handed to the solver must be the one the interpreter produced."""
    client.post("/api/solve", json=VALID_BODY)

    (board_arg,), _ = solver_controller.solve.call_args
    assert board_arg is interpreter.buildBoard.return_value


def test_solve_serialises_positions_as_xy_pairs(client, solver_controller):
    """``SolutionPath`` holds ``Position`` objects; the wire format is ``[x, y]`` pairs."""
    solver_controller.solve.return_value = make_solver_result(
        path=make_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    )

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert body["solutionPath"] == [[0, 0], [1, 0], [1, 1], [0, 1]]


@pytest.mark.parametrize(
    "status",
    [SolverStatus.UNSOLVABLE, SolverStatus.TIMEOUT, SolverStatus.FAILED],
)
def test_solve_non_results_are_200_not_4xx(client, solver_controller, status):
    """§5.5.3: UNSOLVABLE / TIMEOUT / FAILED are solver *outcomes*, not HTTP errors.
    They return 200 with a null path — never a 4xx."""
    solver_controller.solve.return_value = make_solver_result(
        status=status, path=None, solver_used="DFS", message="No solution exists."
    )

    response = client.post("/api/solve", json=VALID_BODY)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == status.value
    assert body["success"] is False
    assert body["solutionPath"] is None


def test_solve_nulls_path_when_status_not_solved_despite_path_present(
    client, solver_controller
):
    """Defence in depth: a solver that reports a non-SOLVED status while still carrying a
    candidate path must not have that path surfaced. §3.2.1 — the agent is not a
    correctness oracle."""
    solver_controller.solve.return_value = make_solver_result(
        status=SolverStatus.FAILED, path=make_path([(0, 0), (0, 1)])
    )

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert body["success"] is False
    assert body["solutionPath"] is None


def test_solve_handles_solved_status_with_null_path(client, solver_controller):
    """A SOLVED status with no path is contradictory input; the API must degrade to a
    null path rather than raising."""
    solver_controller.solve.return_value = make_solver_result(
        status=SolverStatus.SOLVED, path=None
    )

    response = client.post("/api/solve", json=VALID_BODY)
    assert response.status_code == 200
    assert response.json()["solutionPath"] is None


def test_solve_accepts_empty_walls_list(client):
    response = client.post(
        "/api/solve", json={"boardSize": 6, "waypoints": [[0, 0], [5, 5]], "walls": []}
    )
    assert response.status_code == 200


def test_solve_accepts_omitted_walls_key(client, interpreter):
    """``walls`` has a ``default_factory`` — the key is optional on the wire (§5.5.1)."""
    response = client.post("/api/solve", json={"boardSize": 6, "waypoints": [[0, 0], [5, 5]]})
    assert response.status_code == 200

    (request_arg,), _ = interpreter.buildBoard.call_args
    assert request_arg.walls == []


@pytest.mark.parametrize("board_size", [6, 7, 8])
def test_solve_accepts_every_supported_board_size(client, board_size):
    """§5.2 supports 6 | 7 | 8. Size is *not* constrained at the schema level — that is
    ``InputValidator``'s job — so all three must pass shape validation."""
    response = client.post(
        "/api/solve", json={"boardSize": board_size, "waypoints": [[0, 0]], "walls": []}
    )
    assert response.status_code == 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/import
# ──────────────────────────────────────────────────────────────────────────────


def test_import_returns_200_validation_result(client):
    response = client.post("/api/import", json=VALID_BODY)
    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "message": "Board configuration is valid.",
        "errors": [],
    }


def test_import_accepts_reference_board_configuration(client):
    """The canonical ``board_configuration.json`` (§5.4.2) carries a ``solutionPath`` key
    that ``PuzzleRequest`` does not declare. Pydantic ignores unknown fields, so the
    reference file must import cleanly — a real user workflow."""
    response = client.post("/api/import", json=REFERENCE_BOARD)
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_import_never_invokes_the_solver(client, solver_controller):
    """Import is validate-only (§2.3). The solver pipeline must stay untouched."""
    client.post("/api/import", json=VALID_BODY)
    solver_controller.solve.assert_not_called()


def test_import_propagates_validator_message(client, input_validator):
    input_validator.validate.return_value = make_validation_result(
        message="Board configuration accepted."
    )
    assert client.post("/api/import", json=VALID_BODY).json()["message"] == (
        "Board configuration accepted."
    )


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/health
# ──────────────────────────────────────────────────────────────────────────────


def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["apiVersion"] == API_VERSION


def test_health_omits_model_state_when_no_provider_injected(client):
    """Absent an RL status provider, ``modelLoaded`` is null rather than a guessed
    boolean — the API must not assert a model state it cannot observe."""
    assert client.get("/api/health").json()["modelLoaded"] is None


@pytest.mark.parametrize("loaded", [True, False])
def test_health_reports_injected_model_state(make_api, loaded):
    _, client = make_api(model_loaded_provider=lambda: loaded)
    assert client.get("/api/health").json()["modelLoaded"] is loaded


def test_health_does_not_touch_validation_or_solver_pipeline(
    client, interpreter, input_validator, solver_controller
):
    """§3.2.1: health is a cheap in-process probe. It must remain answerable when the
    downstream collaborators are degraded or absent."""
    client.get("/api/health")

    interpreter.buildBoard.assert_not_called()
    input_validator.validate.assert_not_called()
    solver_controller.solve.assert_not_called()


def test_health_stays_green_when_all_collaborators_raise(make_api):
    from unittest.mock import MagicMock

    exploding = MagicMock()
    exploding.buildBoard.side_effect = RuntimeError("down")
    exploding.validate.side_effect = RuntimeError("down")
    exploding.solve.side_effect = RuntimeError("down")

    _, client = make_api(
        interpreter=exploding, input_validator=exploding, solver_controller=exploding
    )
    assert client.get("/api/health").status_code == 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/architecture
# ──────────────────────────────────────────────────────────────────────────────


def test_architecture_returns_200_inventory(client):
    response = client.get("/api/architecture")
    assert response.status_code == 200

    body = response.json()
    assert body["apiVersion"] == API_VERSION
    assert set(body) == {
        "apiVersion",
        "buildTimestamp",
        "runtime",
        "validation",
        "numerical",
        "reinforcementLearning",
        "solvers",
        "backendComponents",
        "frontend",
    }


def test_architecture_delegates_to_provider(client, architecture_provider):
    client.get("/api/architecture")
    architecture_provider.collect.assert_called_once_with()


def test_architecture_reports_both_registered_solvers(client):
    solvers = {entry["name"]: entry for entry in client.get("/api/architecture").json()["solvers"]}
    assert set(solvers) == {"RLSolver", "AlgorithmicSolver"}
    assert solvers["RLSolver"]["default"] is True
    assert solvers["AlgorithmicSolver"]["default"] is False


def test_architecture_leaks_no_paths_or_secrets(client):
    """§5.5.6 / trust boundary: names and versions only. No file paths, no secrets, no
    environment variables may cross this endpoint."""
    raw = client.get("/api/architecture").text.lower()
    for forbidden in ("/home/", "c:\\", "password", "secret", "token", "api_key", ".zip", ".pth"):
        assert forbidden not in raw


def test_architecture_does_not_touch_solver_pipeline(
    client, interpreter, input_validator, solver_controller
):
    client.get("/api/architecture")

    interpreter.buildBoard.assert_not_called()
    input_validator.validate.assert_not_called()
    solver_controller.solve.assert_not_called()


def test_architecture_unconfigured_returns_503_not_404(make_api):
    """A missing provider means "not configured on this instance" (503), which is
    distinct from "route does not exist" (404). The frontend's advanced mode relies on
    that distinction for feature detection."""
    _, client = make_api(architecture_provider=None)

    response = client.get("/api/architecture")
    assert response.status_code == 503
    assert response.json()["code"] == "INTERNAL_ERROR"


# ──────────────────────────────────────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────────────────────────────────────


def test_cors_allows_configured_origin(client):
    response = client.options(
        "/api/solve",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_default_origin_is_the_vite_dev_server(client):
    """Default must match the frontend's dev server so local development works with no
    extra configuration."""
    response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_origin_list_is_overridable(make_api):
    _, client = make_api(allowed_origins=["https://zipsolver.example"])

    response = client.get("/api/health", headers={"Origin": "https://zipsolver.example"})
    assert response.headers.get("access-control-allow-origin") == "https://zipsolver.example"