"""Adapter: internal solver output → API ``SolverResponse`` DTO.

The solver layer and the API layer evolved separate representations of a solve outcome.
This module is the single translation point between them, living on the API side so the
solver package needs no knowledge of the wire contract.

It is deliberately defensive about three known seams:

1.  **Two possible inputs.** ``AlgorithmicSolver`` returns a ``SolverResult`` that carries
    a real ``getStatus`` (SOLVED / UNSOLVABLE / TIMEOUT / FAILED). ``SolverController``
    currently unwraps that into a ``SolverResponse`` that only has ``getSuccess`` (bool),
    collapsing four states into two. The adapter reads a status when one is present and
    degrades to success→SOLVED / failure→FAILED when it is not — so it is correct today
    and becomes lossless the moment ``SolverController`` preserves status.

2.  **The ``getPostions`` typo.** ``SolutionPath`` exposes the misspelled ``getPostions``;
    a future cleanup will rename it to ``getPositions``. The adapter reads whichever
    exists, so it works before and after that rename with no change here.

3.  **Metrics getter naming.** Internal ``SolverMetrics`` exposes ``getRuntimeMs`` /
    ``getSteps`` / ``getAttempts``; the API DTO wants ``runtimeMs`` / ``steps`` /
    ``attempts``. Mapped explicitly, with sane fallbacks if a field is absent.

The adapter never raises on a malformed result: a result it cannot read becomes a FAILED
response, which the API surfaces as a normal 200 outcome rather than a 500.
"""

from __future__ import annotations

from typing import Any

from backend.api.dtos.SolverResponse import SolverResponse
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus

Coordinate = tuple[int, int]

_VALID_STATUS_VALUES = {member.value for member in SolverStatus}


def _read_status(result: Any) -> SolverStatus:
    """Derive the API ``SolverStatus`` from whatever the solver layer exposes.

    Preference order:
      1. ``getStatus`` — the rich path (``SolverResult``); may be an internal enum or a str.
      2. ``getSuccess`` / ``success`` — the lossy path (``SolverResponse``): True→SOLVED,
         False→FAILED (UNSOLVABLE and TIMEOUT are indistinguishable here).
      3. Neither → FAILED.
    """
    status = getattr(result, "getStatus", None)
    if status is not None:
        # Internal SolverStatus is an Enum whose ``.value`` is the canonical string;
        # a bare string is also accepted. Anything outside the taxonomy → FAILED.
        value = getattr(status, "value", status)
        if value in _VALID_STATUS_VALUES:
            return SolverStatus(value)
        return SolverStatus.FAILED

    success = getattr(result, "getSuccess", getattr(result, "success", None))
    if success is True:
        return SolverStatus.SOLVED
    return SolverStatus.FAILED


def _read_positions(path: Any) -> list[Coordinate] | None:
    """Extract ``[(x, y), ...]`` from a ``SolutionPath``, tolerating the ``getPostions``
    spelling and its eventual ``getPositions`` rename. Returns ``None`` for a null or
    empty path so the wire contract never carries a zero-length ``solutionPath``."""
    if path is None:
        return None

    positions = getattr(path, "getPositions", None)
    if positions is None:
        positions = getattr(path, "getPostions", None)  # current (misspelled) name
    if positions is None:
        return None

    coords = [(p.getX, p.getY) for p in positions]
    return coords or None


def _read_metrics(result: Any) -> SolverMetrics:
    """Map internal ``SolverMetrics`` onto the API DTO. Missing fields fall back to zero
    (attempts to 1, since a result that exists implies at least one attempt), keeping the
    ``ge=0`` / ``ge=1`` DTO constraints satisfiable rather than 500-ing on bad metrics."""
    metrics = getattr(result, "getMetrics", None)
    if metrics is None:
        return SolverMetrics(runtimeMs=0, steps=0, attempts=1)

    runtime_ms = getattr(metrics, "getRuntimeMs", 0)
    steps = getattr(metrics, "getSteps", 0)
    attempts = getattr(metrics, "getAttempts", 1)

    return SolverMetrics(
        runtimeMs=max(0, int(runtime_ms)),
        steps=max(0, int(steps)),
        attempts=max(1, int(attempts)),
    )


def _read_message(result: Any, status: SolverStatus) -> str:
    message = getattr(result, "getMessage", None)
    if isinstance(message, str) and message:
        return message
    return {
        SolverStatus.SOLVED: "Puzzle solved.",
        SolverStatus.UNSOLVABLE: "No valid solution exists for this board.",
        SolverStatus.TIMEOUT: "The solver reached its time limit.",
        SolverStatus.FAILED: "The solver did not find a valid path.",
    }[status]


def _read_solver_used(result: Any) -> str | None:
    used = getattr(result, "getSolverUsed", getattr(result, "solver_used", None))
    return used if isinstance(used, str) and used else None


def to_solver_response(result: Any) -> SolverResponse:
    """Convert an internal solve result (``SolverResult`` or ``SolverResponse``) into the
    API ``SolverResponse`` DTO.

    ``success`` is always derived from the mapped status — never read from the result —
    so the two can never disagree on the wire. ``solutionPath`` is populated only for a
    SOLVED status, so a stray path on a non-result is never leaked.
    """
    status = _read_status(result)
    solved = status == SolverStatus.SOLVED
    path = _read_positions(getattr(result, "getPath", None)) if solved else None

    return SolverResponse(
        status=status,
        success=solved,
        solutionPath=path,
        solverUsed=_read_solver_used(result),
        message=_read_message(result, status),
        metrics=_read_metrics(result),
    )