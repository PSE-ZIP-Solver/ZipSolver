from enum import Enum


class SolverStatus(str, Enum):
    """Outcome of a solve attempt (Design Doc §5.5.3).

    All four values map to HTTP 200 — a non-result is a solver outcome,
    never an API error. Inherits from `str` so it serialises to a bare
    JSON string ("SOLVED") and compares directly against string literals.
    """

    SOLVED = "SOLVED"  # a valid, re-validated path was found
    UNSOLVABLE = "UNSOLVABLE"  # the DFS fallback proved no solution exists
    TIMEOUT = "TIMEOUT"  # a solver reached its fixed time limit
    FAILED = "FAILED"  # no valid path found / other solver failure
