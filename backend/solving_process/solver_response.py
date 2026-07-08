from typing import Optional

from solver_metrics import SolverMetrics
from solution_path import SolutionPath


class SolverResponse:
    def __init__(self, success: bool, path: Optional[SolutionPath], message: str, solverUsed: str, metrics: SolverMetrics):
        self._success = success
        self._path = path
        self._message = message
        self._solverUsed = solverUsed
        self._metrics = metrics

    @property
    def getSuccess(self) -> bool:
        return self._success

    @property
    def getPath(self) -> Optional[SolutionPath]:
        return self._path

    @property
    def getMessage(self) -> str:
        return self._message

    @property
    def getSolverUsed(self) -> str:
        return self._solverUsed

    @property
    def getMetrics(self) -> SolverMetrics:
        return self._metrics