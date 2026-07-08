from backend.puzzle_logic.board import Board
from backend.puzzle_logic.puzzle_rules import PuzzleRules
from backend.solution_path import SolutionPath
from backend.validation_error import ValidationError
from backend.validation_result import ValidationResult


class SolutionValidator:
    """
    Validates whether a given SolutionPath is a correct and complete solution
    for the provided Board, using the configured PuzzleRules.
    """
    def __init__(self):
        self._rules = PuzzleRules()

    def _checkPathExists(self, path: SolutionPath) -> bool:
        """
        Checks if the provided solution path exists and is not empty.

        Args:
            path (SolutionPath): The path to check.

        Returns:
            bool: True if the path exists and contains positions, False otherwise.
        """
        if path is None:
            return False
            
        positions = path.getPositions
        if positions is None or len(positions) == 0:
            return False
            
        return True

    def _checkPathLength(self, board: Board, path: SolutionPath) -> bool:
        """
        Checks if the length of the path matches the expected requirements of the board.

        Args:
            board (Board): The board to check against.
            path (SolutionPath): The path to check.

        Returns:
            bool: True if the length is valid, False otherwise.
        """
        if not self._checkPathExists(path):
            return False
            
        return len(path.getPositions) == board.getCellCount()

    def validate(self, board: Board, path: SolutionPath) -> ValidationResult:
        """
        Validates the candidate solution path against the board's rules.

        Args:
            board (Board): The semantic board being solved.
            path (SolutionPath): The candidate solution path to validate.

        Returns:
            ValidationResult: The structured result containing validity status, message, and any errors.
        """
        errors = []

        # 1. Check if the path exists and has entries
        if not self._checkPathExists(path):
            errors.append(
                ValidationError(
                    errorCode="PATH_EMPTY", 
                    message="The solution path is missing or contains no positions.", 
                    affectedField="path"
                )
            )
            return ValidationResult(valid=False, message="Validation Failed: Path is empty.", errors=errors)

        # 2. Check if the path covers the exact number of required cells (Hamiltonian path requirement)
        if not self._checkPathLength(board, path):
            errors.append(
                ValidationError(
                    errorCode="INVALID_LENGTH", 
                    message=f"Path length ({len(path.getPositions)}) does not match the board's cell count ({board.getCellCount()}).", 
                    affectedField="path"
                )
            )
            return ValidationResult(valid=False, message="Validation Failed: Incorrect path length.", errors=errors)

        # 3. Use PuzzleRules to rigorously verify rules (adjacency, walls, waypoints, unique visits)
        # Note: We pass path.getPositions because isCompleteSolution expects a List[Position]
        if not self._rules.isCompleteSolution(board, path.getPositions):
            errors.append(
                ValidationError(
                    errorCode="RULE_VIOLATION", 
                    message="The path violates one or more core puzzle rules (e.g. invalid moves, walls crossed, waypoints missed/out of order).", 
                    affectedField="path"
                )
            )
            return ValidationResult(valid=False, message="Validation Failed: Puzzle rules violated.", errors=errors)

        # 4. If all checks pass, return a successful ValidationResult
        return ValidationResult(valid=True, message="Solution is fully valid.", errors=[])