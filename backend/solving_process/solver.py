from abc import ABC, abstractmethod
from backend.puzzle_logic.board import Board
from solver_metrics import SolverMetrics
from solution_path import SolutionPath
from enum import Enum

class SolverStatus(Enum):
    SOLVED = "SOLVED"
    UNSOLVABLE = "UNSOLVABLE"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"

from typing import Optional  

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
    
class Solver(ABC):
    """
    Interface for puzzle solving components.
    """

    @abstractmethod
    def solve(self, board: Board) -> SolverResult:
        """
        Executes the solving algorithm for the given board.

        Args:
            board (Board): The semantic board to be solved.

        Returns:
            SolverResult: An object containing the status, path, message, and metrics.
        """
        pass