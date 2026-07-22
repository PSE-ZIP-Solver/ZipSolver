"""§8.2.4 Error Propagation and Robustness — pytest + FastAPI TestClient.

Focus: system behaviour under invalid inputs, internal service failures, and edge-case
execution flows. Asserts the §5.5.5 error taxonomy fires correctly, that every failure
returns the same envelope, and that no internal exception detail escapes to the client.

Taxonomy under test:
    400 MALFORMED_REQUEST        Pydantic shape/type failure
    422 UNSUPPORTED_BOARD_SIZE   boardSize outside {6, 7, 8}
    422 INVALID_WAYPOINTS        duplicate / out-of-bounds / missing waypoints
    422 INVALID_WALLS            non-adjacent / out-of-bounds / duplicate wall
    500 INTERNAL_ERROR           unexpected backend fault
    503 INTERNAL_ERROR           architecture inventory not configured
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from backend.api.dtos.ValidationResult import ValidationError
from backend.api.solver_dtos.SolverStatus import SolverStatus

from .conftest import VALID_BODY, make_path, make_solver_result, make_validation_result

ERROR_ENVELOPE_KEYS = {"status", "code", "message", "details", "timestamp"}
ENDPOINTS = [("POST", "/api/solve"), ("POST", "/api/import")]


def _invalid_result(code: str, field: str | None = None):
    return make_validation_result(
        valid=False,
        message=f"Board rejected: {code}.",
        errors=[ValidationError(errorCode=code, affectedField=field, message="detail")],
    )


# ──────────────────────────────────────────────────────────────────────────────
# 400 — malformed request shape
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("path", ["/api/solve", "/api/import"])
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="empty-object"),
        pytest.param({"boardSize": 6}, id="missing-waypoints"),
        pytest.param({"waypoints": [[0, 0]]}, id="missing-boardSize"),
        pytest.param({"boardSize": "six", "waypoints": [[0, 0]]}, id="boardSize-string"),
        pytest.param({"boardSize": None, "waypoints": [[0, 0]]}, id="boardSize-null"),
        pytest.param({"boardSize": 6, "waypoints": "nope"}, id="waypoints-string"),
        pytest.param({"boardSize": 6, "waypoints": [[0]]}, id="short-coordinate"),
        pytest.param({"boardSize": 6, "waypoints": [["a", "b"]]}, id="non-int-coordinate"),
        pytest.param(
            {"boardSize": 6, "waypoints": [[0, 0]], "walls": [{"neighborA": [0, 0]}]},
            id="wall-missing-neighborB",
        ),
        pytest.param(
            {"boardSize": 6, "waypoints": [[0, 0]], "walls": "not-a-list"}, id="walls-string"
        ),
    ],
)
def test_malformed_bodies_return_400_not_422(client, path, payload):
    """FastAPI defaults Pydantic shape failures to 422; §5.5.5 requires 400. This is the
    single most load-bearing override in the API layer — 422 is reserved for *semantic*
    rejection, and conflating the two makes the frontend unable to distinguish a broken
    file from a broken puzzle."""
    response = client.post(path, json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "MALFORMED_REQUEST"


@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
def test_unparseable_json_returns_400(client, method, path):
    response = client.request(
        method, path, content=b"{not valid json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["code"] == "MALFORMED_REQUEST"


@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
def test_empty_body_returns_400(client, method, path):
    assert client.request(method, path, content=b"").status_code == 400


@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
def test_non_object_json_root_returns_400(client, method, path):
    """A JSON array or scalar at the root is not a ``PuzzleRequest``."""
    assert client.request(method, path, json=[1, 2, 3]).status_code == 400
    assert client.request(method, path, json="a string").status_code == 400


def test_wrong_content_type_returns_400(client):
    response = client.post(
        "/api/solve", content=b"boardSize=6", headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 400


def test_multipart_import_returns_400(client):
    """Known frontend contract delta: ``apiCalls.importPuzzle`` posts
    ``multipart/form-data`` while the backend expects a JSON ``PuzzleRequest``. Until
    the two are reconciled the backend must reject cleanly with the documented envelope
    rather than crashing. Pins current behaviour so the fix is a deliberate change."""
    response = client.post("/api/import", files={"file": ("board.json", b"{}", "application/json")})
    assert response.status_code == 400
    assert response.json()["code"] == "MALFORMED_REQUEST"


# ──────────────────────────────────────────────────────────────────────────────
# 422 — semantic rejection
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("path", ["/api/solve", "/api/import"])
@pytest.mark.parametrize(
    "code",
    ["UNSUPPORTED_BOARD_SIZE", "INVALID_WAYPOINTS", "INVALID_WALLS"],
)
def test_validator_error_code_propagates_to_the_envelope(make_api, input_validator, path, code):
    """§8.2.4: "correct propagation of validation errors from input validation to
    API-level error responses"."""
    input_validator.validate.return_value = _invalid_result(code)
    _, client = make_api()

    response = client.post(path, json=VALID_BODY)
    assert response.status_code == 422
    assert response.json()["code"] == code


def test_unrecognised_validator_code_falls_back_to_invalid_waypoints(make_api, input_validator):
    """``InputValidator`` may emit domain codes outside the HTTP taxonomy. The handler
    must degrade to a known code rather than emitting an unmappable one that would fail
    the frontend's switch."""
    input_validator.validate.return_value = _invalid_result("SOME_INTERNAL_DOMAIN_CODE")
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).json()["code"] == "INVALID_WAYPOINTS"


def test_empty_error_list_falls_back_to_invalid_waypoints(make_api, input_validator):
    """A validator that reports invalid without populating ``errors`` must still produce
    a well-formed envelope."""
    input_validator.validate.return_value = make_validation_result(
        valid=False, message="Rejected.", errors=[]
    )
    _, client = make_api()

    response = client.post("/api/solve", json=VALID_BODY)
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_WAYPOINTS"
    assert response.json()["details"] is None


def test_validator_details_are_forwarded(make_api, input_validator):
    input_validator.validate.return_value = _invalid_result("INVALID_WALLS", field="walls")
    _, client = make_api()

    details = client.post("/api/solve", json=VALID_BODY).json()["details"]
    assert details == [
        {"errorCode": "INVALID_WALLS", "affectedField": "walls", "message": "detail"}
    ]


def test_multiple_validation_errors_are_all_forwarded(make_api, input_validator):
    input_validator.validate.return_value = make_validation_result(
        valid=False,
        message="Multiple problems.",
        errors=[
            ValidationError(errorCode="INVALID_WAYPOINTS", affectedField="waypoints", message="dup"),
            ValidationError(errorCode="INVALID_WALLS", affectedField="walls", message="diagonal"),
        ],
    )
    _, client = make_api()

    body = client.post("/api/solve", json=VALID_BODY).json()
    assert len(body["details"]) == 2
    assert body["code"] == "INVALID_WAYPOINTS"  # first error drives the envelope code


def test_validator_message_is_surfaced(make_api, input_validator):
    """The frontend's ``showErrors()`` renders this string (§7.4)."""
    input_validator.validate.return_value = make_validation_result(
        valid=False, message="Waypoint 3 lies outside the board.", errors=[]
    )
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).json()["message"] == (
        "Waypoint 3 lies outside the board."
    )


def test_blank_validator_message_gets_a_default(make_api, input_validator):
    input_validator.validate.return_value = make_validation_result(
        valid=False, message="", errors=[]
    )
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).json()["message"] != ""


# ──────────────────────────────────────────────────────────────────────────────
# 500 — internal faults, and no leakage
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "collaborator", ["interpreter", "input_validator", "solver_controller"]
)
def test_collaborator_exception_becomes_500_envelope(make_api, request, collaborator):
    """§8.2.4: solver and collaborator failures are "correctly mapped to API responses
    without exposing internal exceptions"."""
    stub = request.getfixturevalue(collaborator)
    method = {
        "interpreter": "buildBoard",
        "input_validator": "validate",
        "solver_controller": "solve",
    }[collaborator]
    getattr(stub, method).side_effect = RuntimeError("internal detail that must not leak")

    _, client = make_api()
    response = client.post("/api/solve", json=VALID_BODY)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"


@pytest.mark.parametrize(
    "exception",
    [
        RuntimeError("db password is hunter2"),
        ValueError("/home/ammar/models/zip-dqn.zip not found"),
        KeyError("SECRET_TOKEN"),
        AttributeError("'NoneType' object has no attribute 'getPostions'"),
        MemoryError(),
    ],
)
def test_internal_exception_details_never_reach_the_client(make_api, solver_controller, exception):
    """No stack traces, file paths, credentials, or internal attribute names may cross
    the boundary — the API is the trust boundary in both directions."""
    solver_controller.solve.side_effect = exception
    _, client = make_api()

    raw = client.post("/api/solve", json=VALID_BODY).text
    assert raw.count("Traceback") == 0
    for leaked in ("hunter2", "/home/", "SECRET_TOKEN", "getPostions", "NoneType"):
        assert leaked not in raw


def test_500_message_is_generic(make_api, solver_controller):
    solver_controller.solve.side_effect = RuntimeError("very specific internal failure")
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).json()["message"] == (
        "An unexpected backend error occurred."
    )


def test_architecture_provider_failure_becomes_500(make_api, architecture_provider):
    architecture_provider.collect.side_effect = RuntimeError("inventory failed")
    _, client = make_api()

    response = client.get("/api/architecture")
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"


def test_health_provider_failure_becomes_500(make_api):
    """Even the liveness probe must fail structurally rather than crashing the worker."""

    def explode() -> bool:
        raise RuntimeError("model registry unreachable")

    _, client = make_api(model_loaded_provider=explode)

    response = client.get("/api/health")
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"


def test_service_recovers_after_an_internal_error(make_api, solver_controller):
    """A 500 must not poison subsequent requests."""
    solver_controller.solve.side_effect = RuntimeError("transient")
    _, client = make_api()
    assert client.post("/api/solve", json=VALID_BODY).status_code == 500

    solver_controller.solve.side_effect = None
    solver_controller.solve.return_value = make_solver_result(path=make_path([(0, 0)]))
    assert client.post("/api/solve", json=VALID_BODY).status_code == 200


# ──────────────────────────────────────────────────────────────────────────────
# Envelope uniformity — §8.2.4 "uniform error formatting across all Endpoints"
# ──────────────────────────────────────────────────────────────────────────────


def _all_error_responses(client, make_api, input_validator, solver_controller):
    """Yield one response per reachable error class."""
    yield client.post("/api/solve", json={"boardSize": "six"})  # 400
    yield client.post("/api/import", json={})  # 400

    input_validator.validate.return_value = _invalid_result("INVALID_WAYPOINTS")
    _, semantic_client = make_api()
    yield semantic_client.post("/api/solve", json=VALID_BODY)  # 422
    yield semantic_client.post("/api/import", json=VALID_BODY)  # 422

    solver_controller.solve.side_effect = RuntimeError("boom")
    _, failing_client = make_api()
    yield failing_client.post("/api/solve", json=VALID_BODY)  # 500

    _, unconfigured_client = make_api(architecture_provider=None)
    yield unconfigured_client.get("/api/architecture")  # 503


def test_every_error_uses_the_same_envelope(
    client, make_api, input_validator, solver_controller
):
    for response in _all_error_responses(client, make_api, input_validator, solver_controller):
        body = response.json()
        assert set(body) == ERROR_ENVELOPE_KEYS, response.status_code
        assert body["status"] == response.status_code
        assert isinstance(body["message"], str) and body["message"]
        assert body["details"] is None or isinstance(body["details"], list)


def test_every_error_carries_a_parseable_utc_timestamp(
    client, make_api, input_validator, solver_controller
):
    for response in _all_error_responses(client, make_api, input_validator, solver_controller):
        timestamp = response.json()["timestamp"]
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None, f"{timestamp} is not timezone-aware"


def test_every_error_code_is_in_the_documented_taxonomy(
    client, make_api, input_validator, solver_controller
):
    from backend.api.dtos.ErrorResponse import ErrorCode

    taxonomy = {member.value for member in ErrorCode}
    for response in _all_error_responses(client, make_api, input_validator, solver_controller):
        assert response.json()["code"] in taxonomy


def test_error_responses_are_json(client):
    response = client.post("/api/solve", json={"boardSize": "six"})
    assert response.headers["content-type"].startswith("application/json")


# ──────────────────────────────────────────────────────────────────────────────
# Robustness against partially-invalid and edge-case payloads
# ──────────────────────────────────────────────────────────────────────────────


def test_solver_returning_none_becomes_500_not_a_crash(make_api, solver_controller):
    """A collaborator violating its own contract must still produce a structured error."""
    solver_controller.solve.return_value = None
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).status_code == 500


def test_validator_returning_wrong_type_becomes_500(make_api, input_validator):
    input_validator.validate.return_value = "not a ValidationResult"
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).status_code == 500


def test_metrics_violating_constraints_become_500(make_api, solver_controller):
    """``SolverMetrics`` enforces ``attempts >= 1``. A solver emitting 0 breaks the
    response contract and must surface as an internal error, not a malformed 200."""
    bad_metrics = MagicMock()
    bad_metrics.runtime_ms = -5
    bad_metrics.steps = -1
    bad_metrics.attempts = 0

    solver_controller.solve.return_value = make_solver_result(
        path=make_path([(0, 0)]), metrics=bad_metrics
    )
    _, client = make_api()

    assert client.post("/api/solve", json=VALID_BODY).status_code == 500


def test_very_large_payload_is_handled_structurally(client, input_validator):
    """A 64x64 board is out of range but structurally valid; it must reach the semantic
    validator and be rejected there, never crash the parser."""
    input_validator.validate.return_value = _invalid_result("UNSUPPORTED_BOARD_SIZE")

    response = client.post(
        "/api/solve",
        json={
            "boardSize": 64,
            "waypoints": [[r, c] for r in range(64) for c in range(64)],
            "walls": [],
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "UNSUPPORTED_BOARD_SIZE"


def test_empty_waypoints_list_passes_shape_and_is_rejected_semantically(
    client, input_validator
):
    """§5.2 requires k >= 2 waypoints, but that is a semantic rule — an empty list is
    structurally valid and must produce 422, not 400."""
    input_validator.validate.return_value = _invalid_result("INVALID_WAYPOINTS")

    response = client.post("/api/solve", json={"boardSize": 6, "waypoints": [], "walls": []})
    assert response.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# Known-defect regression guards
# ──────────────────────────────────────────────────────────────────────────────


def test_solution_path_property_is_still_misspelled():
    """``SolutionPath`` exposes ``getPostions`` (sic), and ``BackendAPI.solvePuzzle``
    reads that exact name. ``SolutionValidator`` meanwhile calls ``getPositions`` and
    fails at runtime.

    This test documents the defect and will fail the moment the property is renamed —
    at which point ``BackendAPI.solvePuzzle`` must be updated in the same commit.
    Delete this test as part of that fix.
    """
    from backend.solution_path import SolutionPath

    path = SolutionPath()
    assert hasattr(path, "getPostions"), "spelling fixed — update BackendAPI.solvePuzzle"
    assert not hasattr(path, "getPositions"), (
        "getPositions now exists — reconcile BackendAPI.solvePuzzle and delete this guard"
    )


def test_solver_status_non_results_are_never_http_errors(client, solver_controller):
    """Belt-and-braces on the single most misunderstood rule in the contract (§5.5.5):
    UNSOLVABLE / TIMEOUT / FAILED are 200 outcomes. Some frontend sequence diagrams show
    422 for UNSOLVABLE; the backend contract is 200 and this test is the tiebreaker."""
    for status in (SolverStatus.UNSOLVABLE, SolverStatus.TIMEOUT, SolverStatus.FAILED):
        solver_controller.solve.return_value = make_solver_result(status=status, path=None)

        response = client.post("/api/solve", json=VALID_BODY)
        assert response.status_code == 200, f"{status.value} must not be an HTTP error"
        assert set(response.json()) != ERROR_ENVELOPE_KEYS