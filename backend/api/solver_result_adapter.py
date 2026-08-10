"""Adapter: internal solver output -> the API SolverResponse DTO.

The solver package returns a ``SolverResponse`` exposing getter properties
(``getSuccess``, ``getPath``, ``getMessage``, ``getSolverUsed``, ``getMetrics``). The API
layer wants a flat, serialisable shape with an explicit ``SolverStatus``. This adapter
bridges the two and lives in the API package so the solver code is never touched.

Known limitation — status collapse: the controller reports only a success bool, so
UNSOLVABLE and TIMEOUT are indistinguishable here (both are "not success"). We map
success -> SOLVED and failure -> FAILED. Preserving the distinct non-result statuses
would require the controller to surface them; that is a solver-side change, out of scope.
"""

from __future__ import annotations

from typing import Any

from backend.api.dtos.SolverResponse import SolverResponse
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus


def _get(obj: Any, *names: str, default: Any = None) -> Any:
    """Return the first present attribute among ``names``.

    Tolerates both property getters (getSuccess) and plain attributes (success/status), so
    the adapter survives minor naming differences between branches without edits.
    """
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            return value
    return default


def _coerce_metrics(raw: Any) -> SolverMetrics:
    """Map onto SolverMetrics.

    Passes values through as-is (only normalising getter/attribute names). It deliberately
    does NOT clamp: SolverMetrics enforces its own constraints (e.g. attempts >= 1), and a
    solver emitting an out-of-range metric is a contract violation that should surface as a
    500, not be silently repaired into a valid-looking 200.
    """
    if isinstance(raw, SolverMetrics):
        return raw
    runtime = _get(raw, "runtimeMs", "runtime_ms", "getRuntimeMs", default=0)
    steps = _get(raw, "steps", "getSteps", default=0)
    attempts = _get(raw, "attempts", "getAttempts", default=1)
    return SolverMetrics(runtimeMs=runtime, steps=steps, attempts=attempts)


def to_solver_response(result: Any) -> SolverResponse:
    """Convert an internal solver result into the API SolverResponse DTO.

    Accepts either a result already carrying an explicit ``status`` (post-adapter shape)
    or the real ``SolverResponse`` with getters. A None result is a solver contract
    violation, not a valid outcome — it is allowed to raise (AttributeError) so the API's
    unhandled-exception handler turns it into a structured 500, rather than being silently
    masked as a well-formed FAILED 200.
    """
    if result is None:
        # Contract violation: surface as a 500 via the API's unhandled-exception handler.
        raise ValueError("Solver controller returned None instead of a result.")

    # Prefer an explicit status if the object already has one; otherwise derive it from
    # the success bool (the controller-collapse case).
    status = _get(result, "status", "getStatus")
    if status is not None:
        # Status is authoritative — derive success from it so the two can't disagree.
        success = status == SolverStatus.SOLVED
    else:
        success = bool(_get(result, "success", "getSuccess", default=False))
        status = SolverStatus.SOLVED if success else SolverStatus.FAILED

    path_obj = _get(result, "path", "getPath")
    solution_path = None
    if success and path_obj is not None:
        positions = _get(path_obj, "getPositions", "positions", default=None)
        if positions is not None:
            solution_path = [(p.getX, p.getY) for p in positions]

    return SolverResponse(
        status=status,
        success=bool(success),
        solutionPath=solution_path,
        solverUsed=_get(result, "solver_used", "getSolverUsed"),
        message=_get(result, "message", "getMessage", default="") or "",
        metrics=_coerce_metrics(_get(result, "metrics", "getMetrics")),
    )