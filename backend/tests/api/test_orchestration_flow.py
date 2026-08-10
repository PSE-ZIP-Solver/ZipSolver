"""§8.2.3 API Orchestration and Flow Consistency — pytest + FastAPI TestClient.

Focus: backend service coordination and request-pipeline integrity. These tests assert
*sequencing and gating* rather than payload shape — that collaborators run in the order
§3.2.1 mandates, that invalid input never reaches the solver, and that identical requests
produce identical response structures.

The canonical solve lifecycle under test (§3.2.1):
    1. Pydantic shape validation        → 400 on failure
    2. JsonInterpreter.buildBoard       → internal Board
    3. InputValidator.validate          → 422 on failure
    4. SolverController.solve           → 200 SolverResponse
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.api.solver_dtos.SolverStatus import SolverStatus

from backend.tests.api.conftest import (
    IMAGE_UPLOAD,
    VALID_BODY,
    make_path,
    make_solver_result,
    make_validation_result,
)
from backend.api.dtos.ValidationResult import ValidationError

# ──────────────────────────────────────────────────────────────────────────────
# Invocation order
# ──────────────────────────────────────────────────────────────────────────────


def test_solve_invokes_collaborators_in_documented_order(make_api, call_recorder):
    """interpreter → validator → solver. Any other order means either the board is
    validated before it exists, or the solver runs on unvalidated input."""
    _, client = make_api()
    client.post("/api/solve", json=VALID_BODY)

    invoked = [name for name, _, _ in call_recorder.mock_calls]
    assert invoked == [
        "interpreter.buildBoard",
        "input_validator.validate",
        "solver_controller.solve",
    ]


def test_import_runs_extract_then_build_then_validate(make_api, call_recorder, screenshot_extractor):
    """Import runs extraction, then the shared build+validate front half, and stops there —
    it must never reach the solver. The recorder captures interpreter/validator ordering;
    the extractor runs first, before either."""
    _, client = make_api()
    client.post("/api/import", files=IMAGE_UPLOAD)

    screenshot_extractor.extract_to_dict.assert_called_once()
    invoked = [name for name, _, _ in call_recorder.mock_calls]
    assert invoked == ["interpreter.buildBoard", "input_validator.validate"]


def test_validator_receives_the_board_the_interpreter_built(client, interpreter, input_validator):
    """No board substitution between the two stages."""
    client.post("/api/solve", json=VALID_BODY)

    (validated_board,), _ = input_validator.validate.call_args
    assert validated_board is interpreter.buildBoard.return_value


def test_each_collaborator_is_invoked_exactly_once_per_solve(
    client, interpreter, input_validator, solver_controller
):
    """Guards against accidental double-solving — a real cost and determinism risk."""
    client.post("/api/solve", json=VALID_BODY)

    assert interpreter.buildBoard.call_count == 1
    assert input_validator.validate.call_count == 1
    assert solver_controller.solve.call_count == 1


# ──────────────────────────────────────────────────────────────────────────────
# Gating: invalid input must never reach the solver
# ──────────────────────────────────────────────────────────────────────────────


def test_semantically_invalid_board_never_reaches_the_solver(
    make_api, input_validator, solver_controller
):
    """§8.2.3: "invalid input is blocked at the API or validation layer and never
    reaches the solver Pipeline"."""
    input_validator.validate.return_value = make_validation_result(
        valid=False,
        message="Duplicate waypoint.",
        errors=[ValidationError(errorCode="INVALID_WAYPOINTS", message="dup")],
    )
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).status_code == 422
    solver_controller.solve.assert_not_called()


def test_malformed_body_never_reaches_any_collaborator(
    client, interpreter, input_validator, solver_controller
):
    """Shape validation runs before the interpreter, so a malformed body must not even
    construct a Board."""
    assert client.post("/api/solve", json={"boardSize": "six"}).status_code == 400

    interpreter.buildBoard.assert_not_called()
    input_validator.validate.assert_not_called()
    solver_controller.solve.assert_not_called()


def test_missing_file_never_reaches_any_collaborator(
    client, interpreter, input_validator, screenshot_extractor
):
    """A POST with no file part fails shape validation before any collaborator runs — not
    the extractor, not the interpreter, not the validator."""
    assert client.post("/api/import").status_code == 400

    screenshot_extractor.extract_to_dict.assert_not_called()
    interpreter.buildBoard.assert_not_called()
    input_validator.validate.assert_not_called()


def test_invalid_import_returns_200_with_errors_and_board(make_api, input_validator):
    """§7.1.1 revised for screenshot import: a board that extracts but fails semantic
    validation returns 200 with ``valid: False``, the errors, and the board itself — so
    the frontend can show what was read and let the user fix it rather than silently
    discarding the import. (Contrast /api/solve, where a semantic failure is a 422.)"""
    input_validator.validate.return_value = make_validation_result(
        valid=False,
        message="Wall between non-adjacent cells.",
        errors=[ValidationError(errorCode="INVALID_WALLS", affectedField="walls", message="x")],
    )
    _, client = make_api()

    response = client.post("/api/import", files=IMAGE_UPLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["board"] is not None
    assert [e["errorCode"] for e in body["errors"]] == ["INVALID_WALLS"]


# ──────────────────────────────────────────────────────────────────────────────
# Solver outcome pass-through
# ──────────────────────────────────────────────────────────────────────────────


def test_api_reports_solver_used_without_overriding_it(client, solver_controller):
    """Solver selection and fallback are ``SolverController``'s decisions (§3.2.5); the
    API reports the outcome and must not second-guess which solver ran."""
    solver_controller.solve.return_value = make_solver_result(
        solver_used="DFS",
        message="Solved by DFS fallback.",
        path=make_path([(0, 0), (0, 1)]),
    )

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert body["solverUsed"] == "DFS"
    assert body["message"] == "Solved by DFS fallback."


@pytest.mark.parametrize(
    ("status", "expected_success"),
    [
        (SolverStatus.SOLVED, True),
        (SolverStatus.UNSOLVABLE, False),
        (SolverStatus.TIMEOUT, False),
        (SolverStatus.FAILED, False),
    ],
)
def test_success_flag_is_derived_from_status(
    client, solver_controller, status, expected_success
):
    """§5.5.2: ``success`` is a convenience flag equal to ``status == SOLVED``. It must
    be derived, never taken from the solver, so the two can never disagree."""
    solver_controller.solve.return_value = make_solver_result(
        status=status, path=make_path([(0, 0)])
    )

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert body["success"] is expected_success


def test_metrics_are_passed_through_unmodified(client, solver_controller):
    """Metrics are measurements; the API is not permitted to adjust them."""
    from backend.api.solver_dtos.SolverMetrics import SolverMetrics

    solver_controller.solve.return_value = make_solver_result(
        metrics=SolverMetrics(runtimeMs=4999, steps=0, attempts=3), path=make_path([(0, 0)])
    )

    assert client.post("/api/solve", json=VALID_BODY).json()["metrics"] == {
        "runtimeMs": 4999,
        "steps": 0,
        "attempts": 3,
    }


def test_timeout_outcome_preserves_its_runtime_metric(client, solver_controller):
    """A TIMEOUT still reports the time actually spent — the frontend surfaces it."""
    from backend.api.solver_dtos.SolverMetrics import SolverMetrics

    solver_controller.solve.return_value = make_solver_result(
        status=SolverStatus.TIMEOUT,
        path=None,
        solver_used="DFS",
        message="Solver reached its time limit.",
        metrics=SolverMetrics(runtimeMs=5000, steps=0, attempts=1),
    )

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert body["status"] == "TIMEOUT"
    assert body["metrics"]["runtimeMs"] == 5000
    assert body["solutionPath"] is None


# ──────────────────────────────────────────────────────────────────────────────
# Determinism and statelessness
# ──────────────────────────────────────────────────────────────────────────────


def test_identical_requests_produce_identical_responses(client):
    """§8.2.3: "deterministic response structure for identical requests under
    controlled conditions"."""
    first = client.post("/api/solve", json=VALID_BODY).json()
    second = client.post("/api/solve", json=VALID_BODY).json()
    assert first == second


def test_response_key_set_is_stable_across_outcomes(client, solver_controller):
    """The frontend destructures a fixed shape; keys must not appear and disappear with
    the outcome."""
    expected_keys = {"status", "success", "solutionPath", "solverUsed", "message", "metrics"}

    for status in SolverStatus:
        solver_controller.solve.return_value = make_solver_result(
            status=status, path=make_path([(0, 0)]) if status is SolverStatus.SOLVED else None
        )
        assert set(client.post("/api/solve", json=VALID_BODY).json()) == expected_keys


def test_requests_are_stateless(client, solver_controller):
    """§3.2.1: no session or user state is held. A failing request must not leave the
    service in a degraded state for the next one."""
    solver_controller.solve.return_value = make_solver_result(
        status=SolverStatus.FAILED, path=None
    )
    assert client.post("/api/solve", json=VALID_BODY).json()["success"] is False

    solver_controller.solve.return_value = make_solver_result(path=make_path([(0, 0)]))
    assert client.post("/api/solve", json=VALID_BODY).json()["success"] is True


def test_solve_and_import_do_not_share_state(client, interpreter, input_validator):
    """Both endpoints run interpreter.buildBoard + input_validator.validate; the shared
    path must not carry state between calls."""
    client.post("/api/import", files=IMAGE_UPLOAD)
    client.post("/api/solve", json=VALID_BODY)

    assert interpreter.buildBoard.call_count == 2
    assert input_validator.validate.call_count == 2


def test_concurrent_style_interleaving_is_isolated(make_api):
    """Two clients over the same app instance must not observe each other's results."""
    from backend.api.solver_dtos.SolverMetrics import SolverMetrics

    api, client_a = make_api()
    from fastapi.testclient import TestClient

    client_b = TestClient(api.app, raise_server_exceptions=False)

    api._solver_controller.solve.return_value = make_solver_result(
        metrics=SolverMetrics(runtimeMs=1, steps=1, attempts=1), path=make_path([(0, 0)])
    )
    body_a = client_a.post("/api/solve", json=VALID_BODY).json()
    body_b = client_b.post("/api/solve", json=VALID_BODY).json()
    assert body_a == body_b


# ──────────────────────────────────────────────────────────────────────────────
# Read-only endpoints stay outside the pipeline
# ──────────────────────────────────────────────────────────────────────────────


def test_health_and_architecture_bypass_the_request_pipeline(make_api, call_recorder):
    """Neither diagnostic endpoint may enter the validate/solve pipeline — otherwise a
    liveness probe could be blocked by a degraded solver."""
    _, client = make_api()
    client.get("/api/health")
    client.get("/api/architecture")

    assert call_recorder.mock_calls == []


def test_architecture_is_read_only_across_repeated_calls(client, architecture_provider):
    """Repeated polling by the frontend's advanced mode must be side-effect free."""
    first = client.get("/api/architecture").json()
    second = client.get("/api/architecture").json()

    assert first == second
    assert architecture_provider.collect.call_count == 2


if __name__ == "__main__":
    # Running this file directly (e.g. VS Code's "Run Python File" button) would
    # otherwise define the test functions and exit without executing anything.
    # Delegate to pytest so the play button behaves as expected.
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))