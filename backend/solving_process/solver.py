from abc import ABC, abstractmethod
from backend.puzzle_logic.board import Board
from .solver_result import SolverResult
 
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