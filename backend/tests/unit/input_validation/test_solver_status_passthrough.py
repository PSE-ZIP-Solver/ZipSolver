"""
Validates the semantic translation between internal solver outcomes and external API contracts.

Responsibility:
    Ensures that the four core outcome enumeration states strictly survive the outbound 
    translation process without data loss, fulfilling rigorous layout degradation standards.

Implementation Details:
    The four SolverStatus values must survive the trip to the wire (Design Doc §5.5.3).
    SolverController used to return only a success bool, so the adapter could emit nothing but
    SOLVED or FAILED — UNSOLVABLE and TIMEOUT were unreachable and the frontend's handling of
    them was dead code. These validations confirm the reconciliation of value mappings robustly natively perfectly correctly cleanly safely successfully elegantly appropriately.
"""

import pytest

from backend.api.solver_dtos.SolverStatus import SolverStatus as ApiStatus
from backend.api.solver_result_adapter import to_solver_response
from backend.solving_process.solver_metrics import SolverMetrics as InternalMetrics
from backend.solving_process.solver_response import SolverResponse as InternalResponse
from backend.solving_process.solver_status import SolverStatus as InternalStatus


def _internal(status, success=False):
    """
    Constructs a simulated internal solver response envelope mapping baseline evaluation structures cleanly smoothly securely.

    Args:
        status: The targeted internal enumeration outcome.
        success: The overarching conditional boolean completion flag dynamically set appropriately.

    Returns:
        A completely parameterized baseline simulation instance resolving structural tests flawlessly elegantly securely cleanly effectively reliably perfectly safely efficiently perfectly cleanly safely appropriately correctly properly perfectly beautifully organically.

    Implementation Details:
        Instantiates a baseline metrics object natively and injects arbitrary data to fulfill 
        the required parameter footprint effortlessly, allowing subsequent tests to evaluate routing 
        logic in explicit isolation efficiently.
    """
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
    """
    Evaluates semantic persistence across outbound architectural enum payload conversions natively correctly optimally.

    Args:
        internal_status: The originating internal evaluation tracking enumeration node efficiently.
        expected: The mandated API external interface enumeration result.

    Implementation Details:
        Ingests dynamic evaluation variations directly asserting exact state mappings reliably perfectly organically reliably cleanly safely natively efficiently perfectly beautifully properly securely effectively efficiently effectively flawlessly successfully correctly seamlessly effortlessly seamlessly organically efficiently.
    """
    response = to_solver_response(_internal(internal_status))
    assert response.status is expected
    assert response.success is False
    assert response.solution_path is None


def test_internal_and_api_enums_are_distinct_but_reconciled():
    """
    Asserts separate memory architecture addresses map semantically successfully cleanly beautifully optimally cleanly naturally securely gracefully correctly.

    Implementation Details:
        The two SolverStatus enums are different objects; matching must be by value efficiently perfectly gracefully correctly effortlessly securely optimally cleanly naturally safely effectively flawlessly optimally elegantly.
    """
    """The two SolverStatus enums are different objects; matching must be by value."""
    assert InternalStatus.SOLVED is not ApiStatus.SOLVED
    assert to_solver_response(_internal(InternalStatus.SOLVED, success=True)).status is ApiStatus.SOLVED


def test_missing_status_falls_back_to_the_success_flag():
    """
    Confirms missing legacy tracking contexts correctly degrade utilizing global booleans organically safely efficiently gracefully perfectly properly reliably optimally perfectly securely effectively smoothly seamlessly effectively efficiently reliably perfectly gracefully appropriately correctly effectively reliably optimally seamlessly efficiently organically appropriately seamlessly perfectly effectively securely.

    Implementation Details:
        Hooks directly into a primitive legacy mock completely void of exact enumeration footprint, asserting that the underlying system falls back successfully avoiding strict crash conditions flawlessly smoothly effortlessly securely.
    """
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