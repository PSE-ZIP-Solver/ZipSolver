from typing import Optional

from .solver_metrics import SolverMetrics
from .solver_status import SolverStatus
from backend.solution_path import SolutionPath


class SolverResponse:
    def __init__(self, success: bool, path: Optional[SolutionPath], message: str, solverUsed: str, metrics: SolverMetrics, status: Optional[SolverStatus] = None):
        self._success = success
        self._path = path
        self._message = message
        self._solverUsed = solverUsed
        self._metrics = metrics
        # Optional and defaulted so every existing construction site keeps working. When
        # supplied it preserves the distinction the API contract requires between
        # UNSOLVABLE, TIMEOUT and FAILED, which a bare success bool cannot express.
        self._status = status if status is not None else (
            SolverStatus.SOLVED if success else SolverStatus.FAILED
        )

    @property
    def getStatus(self) -> SolverStatus:
        return self._status

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