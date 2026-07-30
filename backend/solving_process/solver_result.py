from typing import Optional

from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath


class SolverResult:
    """Outcome of a single solve attempt, or of the whole orchestrated run.

    ``solverUsed`` is optional so the individual solvers can keep constructing this with
    four arguments; ``SolverController`` sets it when it reports which strategy produced
    the answer. The value is the *wire* identifier ("RL" / "DFS"), not the class name —
    the API surfaces it directly to the frontend.
    """

    def __init__(
        self,
        status: SolverStatus,
        path: Optional[SolutionPath],
        message: str,
        metrics: SolverMetrics,
        solverUsed: Optional[str] = None,
    ):
        self._status = status
        self._path = path
        self._message = message
        self._metrics = metrics
        self._solverUsed = solverUsed

    @property
    def getStatus(self) -> SolverStatus:
        return self._status

    @property
    def getPath(self) -> Optional[SolutionPath]:
        return self._path

    @property
    def getMessage(self) -> str:
        return self._message

    @property
    def getMetrics(self) -> SolverMetrics:
        return self._metrics

    @property
    def getSolverUsed(self) -> Optional[str]:
        return self._solverUsed

    def hasSolution(self) -> bool:
        """Returns whether the result contains a solution path."""
        return self._path is not None