from backend.puzzle_logic.board import Board
from backend.puzzle_logic.puzzle_rules import PuzzleRules
from backend.solution_path import SolutionPath
from backend.validation_error import ValidationError
from backend.validation_result import ValidationResult


class SolutionValidator:
    """
    Checks if a proposed solution path correctly completes the puzzle.

    Responsibility:
        Acts as the final verification tool for puzzle solutions. It ensures that a path 
        is properly structured, stays within the board boundaries, visits all required 
        cells, and follows all movement rules before marking the puzzle as solved.

    Implementation Details:
        Uses a step-by-step verification process. It first checks for basic errors (like 
        empty paths) to save time, then verifies the path length, and finally uses the 
        core rules engine to check for specific movement or logic violations.
    """
    def __init__(self):
        """
        Sets up the validator and prepares the rule-checking logic.

        Implementation Details:
            Creates a new instance of the PuzzleRules class and stores it internally 
            to be used for detailed logic checks.
        """
        self._rules = PuzzleRules()

    def _checkPathExists(self, path: SolutionPath) -> bool:
        """
        Checks if the provided path object contains any actual movement data.

        Args:
            path: The solution path object to be checked.

        Returns:
            True if the path exists and has at least one position; False otherwise.

        Implementation Details:
            Checks if the path object is null. If it exists, it retrieves the list 
            of positions and ensures the list is neither null nor empty.
        """
        if path is None:
            return False
            
        positions = path.getPositions
        if positions is None or len(positions) == 0:
            return False
            
        return True

    def _checkPathLength(self, board: Board, path: SolutionPath) -> bool:
        """
        Verifies if the path visits the exact number of cells required by the board size.

        Args:
            board: The board layout used to calculate the required number of steps.
            path: The solution path being checked.

        Returns:
            True if the number of steps in the path equals the total number of cells on the board.

        Implementation Details:
            First ensures the path is valid. It then calculates the total board area 
            (size squared) and compares it directly to the total number of positions 
            recorded in the path.
        """
        if not self._checkPathExists(path):
            return False
            
        return len(path.getPositions) == (board.getSize ** 2)

    def validate(self, board: Board, path: SolutionPath) -> ValidationResult:
        """
        Runs a complete check on a solution path to ensure it follows all puzzle rules.

        Args:
            board: The grid and ruleset for the current puzzle.
            path: The sequence of moves submitted for validation.

        Returns:
            A result object indicating whether the path is valid and listing any errors found.

        Implementation Details:
            Follows a four-step check:
            1. Confirms the path is not empty.
            2. Confirms the path visits every cell on the board.
            3. Uses the rules engine to check for invalid moves, wall collisions, 
               or missed waypoints.
            4. If no issues are found, returns a success result.
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