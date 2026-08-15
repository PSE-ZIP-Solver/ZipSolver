"""The four SolverStatus values must survive the trip to the wire (Design Doc §5.5.3).

SolverController used to return only a success bool, so the adapter could emit nothing but
SOLVED or FAILED — UNSOLVABLE and TIMEOUT were unreachable and the frontend's handling of
them was dead code.
"""

import pytest

from backend.api.solver_dtos.SolverStatus import SolverStatus as ApiStatus
from backend.api.solver_result_adapter import to_solver_response
from backend.solving_process.solver_metrics import SolverMetrics as InternalMetrics
from backend.solving_process.solver_response import SolverResponse as InternalResponse
from backend.solving_process.solver_status import SolverStatus as InternalStatus


def _internal(status, success=False):
    return InternalResponse(
        success=success,
        path=None,
        message="",
        solverUsed="AlgorithmicSolver",
        metrics=InternalMetrics(runtimeMs=1, steps=2, attempts=1),
        status=status,
    )


@pytest.mark.parametrize(
    "internal_status, expected",
    [
        (InternalStatus.UNSOLVABLE, ApiStatus.UNSOLVABLE),
        (InternalStatus.TIMEOUT, ApiStatus.TIMEOUT),
        (InternalStatus.FAILED, ApiStatus.FAILED),
    ],
)
def test_non_result_statuses_are_preserved(internal_status, expected):
    response = to_solver_response(_internal(internal_status))
    assert response.status is expected
    assert response.success is False
    assert response.solution_path is None


def test_internal_and_api_enums_are_distinct_but_reconciled():
    """The two SolverStatus enums are different objects; matching must be by value."""
    assert InternalStatus.SOLVED is not ApiStatus.SOLVED
    assert to_solver_response(_internal(InternalStatus.SOLVED, success=True)).status is ApiStatus.SOLVED


def test_missing_status_falls_back_to_the_success_flag():
    class Legacy:
        getSuccess = False
        getPath = None
        getMessage = ""
        getSolverUsed = "AlgorithmicSolver"
        getMetrics = None

    response = to_solver_response(Legacy())
    assert response.status is ApiStatus.FAILED
    assert response.metrics.runtime_ms == 0
    assert response.metrics.attempts == 1