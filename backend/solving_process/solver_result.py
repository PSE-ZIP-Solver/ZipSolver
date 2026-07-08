from typing import Optional

from solver import SolverStatus
from solver_metrics import SolverMetrics
from solution_path import SolutionPath  


class SolverResult:
    def __init__(self, status: SolverStatus, path: Optional[SolutionPath], message: str, metrics: SolverMetrics):
        self._status = status
        self._path = path
        self._message = message
        self._metrics = metrics

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

    def hasSolution(self) -> bool:
        """Returns whether the result contains a solution path."""
        return self._path is not None