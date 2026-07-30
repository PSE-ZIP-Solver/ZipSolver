"""Shared fixtures for the API-layer test suite (Design Doc §8.2).

The API layer declares its collaborators as structural Protocols
(``JsonInterpreterProtocol``, ``InputValidatorProtocol``, ``SolverControllerProtocol``,
``ArchitectureProviderProtocol``). Every fixture here stubs that boundary and nothing
below it, so these tests stay valid when the concrete ``JsonInterpreter`` /
``InputValidator`` / ``SolverController`` implementations land.

Nothing in this package may import from ``offline_training`` — training and inference
are separate test surfaces per §3.4.
"""

from __future__ import annotations

from typing import Any, Iterable
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.BackendAPI import BackendAPI
from backend.api.dtos.ValidationResult import ValidationError, ValidationResult
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.puzzle_logic import Board, Position
from backend.solution_path import SolutionPath

# ──────────────────────────────────────────────────────────────────────────────
# Canonical payloads
# ──────────────────────────────────────────────────────────────────────────────

#: Minimal well-formed body accepted by both POST endpoints. camelCase on the wire,
#: matching what the frontend's ``apiCalls.solvePuzzle`` actually sends.
VALID_BODY: dict[str, Any] = {
    "boardSize": 6,
    "waypoints": [[0, 0], [2, 2], [5, 5]],
    "walls": [{"neighborA": [0, 0], "neighborB": [1, 0]}],
}

#: The reference board from the design doc (§5.4.2) / ``board_configuration.json``.
#: Carries a ``solutionPath`` key that ``PuzzleRequest`` must tolerate and ignore.
REFERENCE_BOARD: dict[str, Any] = {
    "boardSize": 6,
    "waypoints": [[0, 0], [2, 2], [4, 4]],
    "walls": [{"neighborA": [0, 0], "neighborB": [1, 0]}],
    "solutionPath": [[0, 0], [0, 1], [0, 2]],
}


def make_path(coords: Iterable[tuple[int, int]]) -> SolutionPath:
    """Build a real ``SolutionPath`` from (x, y) pairs.

    Uses the production class rather than a mock on purpose: ``BackendAPI.solvePuzzle``
    reads the ``getPostions`` property (sic — see ``test_error_propagation`` for the
    spelling regression guard), so a real object keeps that coupling under test.
    """
    path = SolutionPath()
    for x, y in coords:
        path.add(Position(x, y))
    return path


def make_metrics(runtime_ms: int = 142, steps: int = 36, attempts: int = 1) -> SolverMetrics:
    return SolverMetrics(runtimeMs=runtime_ms, steps=steps, attempts=attempts)


class _InternalResult:
    """Shaped exactly like the internal solver output the adapter consumes in production:
    ``getStatus`` / ``getPath`` / ``getMessage`` / ``getMetrics`` / ``getSolverUsed``
    properties, backed by an internal ``SolverStatus`` and ``SolverMetrics``.

    Using a real object rather than a ``MagicMock`` matters here — a bare mock auto-creates
    every getter as a truthy sub-mock, which would defeat the adapter's ``getattr(..., None)``
    fallbacks and hide real bugs. This class exercises the genuine adapter path.
    """

    def __init__(self, status, path, message, solver_used, metrics):
        self._status = status
        self._path = path
        self._message = message
        self._solver_used = solver_used
        self._metrics = metrics

    @property
    def getStatus(self):
        return self._status

    @property
    def getPath(self):
        return self._path

    @property
    def getMessage(self) -> str:
        return self._message

    @property
    def getSolverUsed(self) -> str | None:
        return self._solver_used

    @property
    def getMetrics(self):
        return self._metrics


class _InternalMetrics:
    """Mirrors the internal ``SolverMetrics`` getter shape (``getRuntimeMs`` etc.)."""

    def __init__(self, runtime_ms: int, steps: int, attempts: int):
        self._runtime_ms = runtime_ms
        self._steps = steps
        self._attempts = attempts

    @property
    def getRuntimeMs(self) -> int:
        return self._runtime_ms

    @property
    def getSteps(self) -> int:
        return self._steps

    @property
    def getAttempts(self) -> int:
        return self._attempts


def make_solver_result(
    *,
    status: SolverStatus = SolverStatus.SOLVED,
    path: SolutionPath | None = None,
    solver_used: str | None = "RL",
    message: str = "Solved by RL agent.",
    metrics: SolverMetrics | None = None,
):
    """Build an internal-shaped solve result for the adapter under test.

    ``status`` is given as the API ``SolverStatus`` for test readability and mapped onto an
    equal-valued internal status object, so callers keep writing ``SolverStatus.TIMEOUT``
    while the adapter still sees the internal getter shape it will meet in production.
    """
    from backend.solving_process.solver_status import SolverStatus as InternalStatus

    internal_status = InternalStatus(status.value)

    if metrics is not None:
        internal_metrics = _InternalMetrics(
            metrics.runtime_ms, metrics.steps, metrics.attempts
        )
    else:
        internal_metrics = _InternalMetrics(142, 36, 1)

    return _InternalResult(internal_status, path, message, solver_used, internal_metrics)


def make_validation_result(
    *,
    valid: bool = True,
    message: str = "Board configuration is valid.",
    errors: list[ValidationError] | None = None,
) -> ValidationResult:
    return ValidationResult(valid=valid, message=message, errors=errors or [])


# ──────────────────────────────────────────────────────────────────────────────
# Collaborator stubs
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def interpreter() -> MagicMock:
    """JsonInterpreter stub — returns a 6x6 Board for any request."""
    stub = MagicMock()
    stub.buildBoard.return_value = Board(6)
    return stub


@pytest.fixture
def input_validator() -> MagicMock:
    """InputValidator stub — accepts every board by default."""
    stub = MagicMock()
    stub.validate.return_value = make_validation_result()
    return stub


@pytest.fixture
def solver_controller() -> MagicMock:
    """SolverController stub — returns a SOLVED 3-cell path by default."""
    stub = MagicMock()
    stub.solve.return_value = make_solver_result(path=make_path([(0, 0), (0, 1), (0, 2)]))
    return stub


@pytest.fixture
def architecture_provider() -> MagicMock:
    """ArchitectureProvider stub — returns a real ArchitectureInfo built by the
    production provider, so the response shape under test is the genuine one."""
    from backend.api.architecture_provider.ArchitectureProvider import ArchitectureProvider

    stub = MagicMock()
    stub.collect.return_value = ArchitectureProvider(
        build_timestamp="2026-06-07T10:15:30+00:00"
    ).collect()
    return stub


# ──────────────────────────────────────────────────────────────────────────────
# App / client factory
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def make_api(interpreter, input_validator, solver_controller, architecture_provider):
    """Factory building a ``BackendAPI`` with any subset of collaborators overridden.

    Usage::

        def test_x(make_api, solver_controller):
            solver_controller.solve.return_value = make_solver_result(...)
            api, client = make_api()
            ...

        # or swap a collaborator wholesale
        api, client = make_api(architecture_provider=None)

    ``raise_server_exceptions=False`` lets the registered catch-all handler produce a real
    500 ``ErrorResponse`` instead of the exception propagating into the test — which is
    exactly the behaviour §8.2.4 requires us to assert.
    """

    def _factory(**overrides) -> tuple[BackendAPI, TestClient]:
        collaborators = {
            "interpreter": interpreter,
            "input_validator": input_validator,
            "solver_controller": solver_controller,
            "architecture_provider": architecture_provider,
        }
        model_loaded_provider = overrides.pop("model_loaded_provider", None)
        allowed_origins = overrides.pop("allowed_origins", None)
        collaborators.update(overrides)

        api = BackendAPI(
            collaborators["interpreter"],
            collaborators["input_validator"],
            collaborators["solver_controller"],
            collaborators["architecture_provider"],
            allowed_origins=allowed_origins,
            model_loaded_provider=model_loaded_provider,
        )
        return api, TestClient(api.app, raise_server_exceptions=False)

    return _factory


@pytest.fixture
def client(make_api) -> TestClient:
    """The common case: a fully-stubbed, all-defaults API client."""
    _, test_client = make_api()
    return test_client


@pytest.fixture
def call_recorder(interpreter, input_validator, solver_controller) -> MagicMock:
    """Parent mock recording cross-collaborator call ordering.

    ``manager.mock_calls`` yields a single ordered log across all three attached mocks,
    which is how §8.2.3 verifies the interpreter → validator → solver sequence.
    """
    manager = MagicMock()
    manager.attach_mock(interpreter, "interpreter")
    manager.attach_mock(input_validator, "input_validator")
    manager.attach_mock(solver_controller, "solver_controller")
    return manager