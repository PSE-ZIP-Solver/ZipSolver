from abc import ABC, abstractmethod
from backend.puzzle_logic.board import Board
from .solver_result import SolverResult


class Solver(ABC):
    """
    Establishes the mandatory structural blueprint for all puzzle-solving modules.

    Responsibility:
        Enforces a strict, polymorphic interface contract that any dedicated mathematical
        or ML-based algorithm must adopt. This allows the orchestration layer to dynamically
        swap puzzle-solving strategies interchangeably without rewriting execution logic.

    Implementation Details:
        Inherits natively from Python's Abstract Base Class (ABC). Completely devoid of
        instantiable state, it utilizes abstract decorators to strictly mandate input and output
        signatures on all inheriting descendant classes.
    """

    @abstractmethod
    def solve(self, board: Board) -> SolverResult:
        """
        Executes the specialized computational algorithm against a provided puzzle topology.

        Args:
            board: The structural grid layout mapping coordinates, boundaries, and sequences.

        Returns:
            The standardized outcome envelope housing the route, status flags, and telemetry data.

        Implementation Details:
            Functions strictly as a virtual method stub. Concrete implementations extending this
            class must completely override this function, encapsulate their unique pathfinding
            logic internally, and rigidly conform to returning the standardized domain result payload.
        """
        pass
