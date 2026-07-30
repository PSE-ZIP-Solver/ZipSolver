"""Unit tests for the internal-result → API-DTO adapter (``solver_result_adapter``).

These are pure: no TestClient, no HTTP. They pin the adapter's behaviour against every
input shape it must tolerate — the rich ``SolverResult`` (with status), the lossy
``SolverResponse`` (bool only), the ``getPostions`` typo and its future rename, malformed
metrics, and ``None``.
"""

from __future__ import annotations

import pytest

from backend.api.solver_dtos.SolverStatus import SolverStatus
from backend.api.solver_result_adapter import to_solver_response
from backend.puzzle_logic import Position
from backend.solution_path import SolutionPath

pytestmark = pytest.mark.contract


def _path(*coords: tuple[int, int]) -> SolutionPath:
    p = SolutionPath()
    for x, y in coords:
        p.add(Position(x, y))
    return p


# ── Rich input: internal SolverResult with a real status ──────────────────────


class _Result:
    """Mirror of the internal ``SolverResult`` getter shape."""

    def __init__(self, status=None, path=None, message="", solver_used=None, metrics=None):
        self._status, self._path = status, path
        self._message, self._solver_used, self._metrics = message, solver_used, metrics

    @property
    def getStatus(self):
        return self._status

    @property
    def getPath(self):
        return self._path

    @property
    def getMessage(self):
        return self._message

    @property
    def getSolverUsed(self):
        return self._solver_used

    @property
    def getMetrics(self):
        return self._metrics


class _Metrics:
    def __init__(self, r, s, a):
        self._r, self._s, self._a = r, s, a

    @property
    def getRuntimeMs(self):
        return self._r

    @property
    def getSteps(self):
        return self._s

    @property
    def getAttempts(self):
        return self._a


def _internal_status(value: str):
    from backend.solving_process.solver_status import SolverStatus as InternalStatus

    return InternalStatus(value)


class TestRichResult:
    def test_solved_maps_status_and_path(self):
        r = _Result(
            status=_internal_status("SOLVED"),
            path=_path((0, 0), (0, 1), (1, 1)),
            message="A* found it",
            solver_used="AlgorithmicSolver",
            metrics=_Metrics(120, 15, 1),
        )
        dto = to_solver_response(r)
        assert dto.status == SolverStatus.SOLVED
        assert dto.success is True
        assert dto.solution_path == [(0, 0), (0, 1), (1, 1)]
        assert dto.solver_used == "AlgorithmicSolver"

    @pytest.mark.parametrize("status_value", ["UNSOLVABLE", "TIMEOUT", "FAILED"])
    def test_non_results_preserve_status_and_null_path(self, status_value):
        """The states the old code collapsed. The adapter keeps them distinct."""
        r = _Result(
            status=_internal_status(status_value),
            path=None,
            message="",
            metrics=_Metrics(80, 5, 1),
        )
        dto = to_solver_response(r)
        assert dto.status.value == status_value
        assert dto.success is False
        assert dto.solution_path is None

    def test_path_is_dropped_when_status_not_solved(self):
        """Even if a non-SOLVED result carries a path, it must not be surfaced."""
        r = _Result(
            status=_internal_status("FAILED"),
            path=_path((0, 0), (0, 1)),
            metrics=_Metrics(1, 1, 1),
        )
        assert to_solver_response(r).solution_path is None

    def test_status_outside_taxonomy_falls_back_to_failed(self):
        class _Weird:
            value = "PARTIALLY_SOLVED"

        r = _Result(status=_Weird(), metrics=_Metrics(1, 1, 1))
        assert to_solver_response(r).status == SolverStatus.FAILED


# ── Lossy input: internal SolverResponse (bool success only) ──────────────────


class _Response:
    """Mirror of the internal ``SolverResponse`` getter shape — no status."""

    def __init__(self, success, path=None, message="", solver_used=None, metrics=None):
        self._success, self._path = success, path
        self._message, self._solver_used, self._metrics = message, solver_used, metrics

    @property
    def getSuccess(self):
        return self._success

    @property
    def getPath(self):
        return self._path

    @property
    def getMessage(self):
        return self._message

    @property
    def getSolverUsed(self):
        return self._solver_used

    @property
    def getMetrics(self):
        return self._metrics


class TestLossyResponse:
    def test_success_true_becomes_solved(self):
        r = _Response(True, path=_path((0, 0)), solver_used="RLSolver", metrics=_Metrics(50, 8, 1))
        dto = to_solver_response(r)
        assert dto.status == SolverStatus.SOLVED
        assert dto.success is True
        assert dto.solver_used == "RLSolver"

    def test_success_false_becomes_failed(self):
        r = _Response(False, path=None, metrics=_Metrics(60, 3, 1))
        dto = to_solver_response(r)
        assert dto.status == SolverStatus.FAILED
        assert dto.success is False


# ── The getPostions typo and its future rename ────────────────────────────────


class TestPositionsSpelling:
    def test_reads_current_misspelled_property(self):
        """``SolutionPath.getPostions`` (sic) is what exists today."""
        r = _Result(status=_internal_status("SOLVED"), path=_path((2, 3)), metrics=_Metrics(1, 1, 1))
        assert to_solver_response(r).solution_path == [(2, 3)]

    def test_reads_renamed_property_when_it_lands(self):
        """Simulates the future ``getPositions`` rename — adapter must not need changing."""

        class _Renamed:
            def __init__(self, coords):
                self._coords = [Position(x, y) for x, y in coords]

            @property
            def getPositions(self):
                return self._coords

        r = _Result(status=_internal_status("SOLVED"), path=_Renamed([(4, 5)]), metrics=_Metrics(1, 1, 1))
        assert to_solver_response(r).solution_path == [(4, 5)]

    def test_empty_path_becomes_null_not_empty_list(self):
        r = _Result(status=_internal_status("SOLVED"), path=_path(), metrics=_Metrics(1, 1, 1))
        assert to_solver_response(r).solution_path is None


# ── Malformed / degenerate inputs never raise ─────────────────────────────────


class TestRobustness:
    def test_none_result_becomes_failed(self):
        dto = to_solver_response(None)
        assert dto.status == SolverStatus.FAILED
        assert dto.success is False
        assert dto.solution_path is None

    def test_missing_metrics_default_to_valid_zero(self):
        r = _Result(status=_internal_status("SOLVED"), path=_path((0, 0)), metrics=None)
        dto = to_solver_response(r)
        assert dto.metrics.model_dump(by_alias=True) == {"runtimeMs": 0, "steps": 0, "attempts": 1}

    def test_out_of_range_metrics_are_clamped(self):
        r = _Result(
            status=_internal_status("SOLVED"),
            path=_path((0, 0)),
            metrics=_Metrics(-9, -4, 0),
        )
        assert to_solver_response(r).metrics.model_dump(by_alias=True) == {
            "runtimeMs": 0,
            "steps": 0,
            "attempts": 1,
        }

    def test_blank_message_gets_status_appropriate_default(self):
        r = _Result(status=_internal_status("TIMEOUT"), path=None, message="", metrics=_Metrics(1, 1, 1))
        assert to_solver_response(r).message != ""

    def test_success_is_always_derived_never_trusted(self):
        """A result claiming both FAILED status and success must resolve to the status —
        ``success`` is derived from the mapped status, never read off the input."""
        r = _Result(status=_internal_status("FAILED"), path=_path((0, 0)), metrics=_Metrics(1, 1, 1))
        dto = to_solver_response(r)
        assert dto.success is False