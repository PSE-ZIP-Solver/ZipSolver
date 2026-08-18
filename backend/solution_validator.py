from backend.puzzle_logic.board import Board
from backend.puzzle_logic.puzzle_rules import PuzzleRules
from backend.solution_path import SolutionPath
from backend.validation_error import ValidationError
from backend.validation_result import ValidationResult


class SolutionValidator:
    """
    Validates whether a candidate trajectory constitutes a mathematically correct puzzle completion.

    Responsibility:
        Serves as the definitive authentication gateway that processes unverified solver outputs. 
        It strictly verifies structural integrity, domain restrictions, spatial boundaries, and 
        chronological sequence mechanics before officially accepting a path as a victory condition.

    Implementation Details:
        Functions through a strict fast-fail cascading architecture. Instantiates an internal, 
        stateless rule-evaluation module. Defensively screens for baseline structural anomalies 
        (null arrays, incorrect volumes) to short-circuit processing before handing off intensive 
        Hamiltonian validation loops to the core rules engine.
    """
    def __init__(self):
        """
        Initializes the overarching authentication gateway and binds the necessary computational modules.

        Implementation Details:
            Generates a fresh, standalone instance of the puzzle's domain evaluation ruleset 
            and seamlessly assigns it to a strictly protected internal parameter to handle 
            deep logic queries during execution.
        """
        self._rules = PuzzleRules()

    def _checkPathExists(self, path: SolutionPath) -> bool:
        """
        Ascertains if the targeted navigational sequence actually possesses actionable coordinate data.

        Args:
            path: The localized candidate wrapper object queued for internal inspection.

        Returns:
            The determination flag confirming if the structure is allocated and actively populated.

        Implementation Details:
            Employs robust, defensive short-circuit traps. Explicitly queries the raw wrapper object 
            for null states. If valid, extracts the underlying physical tracking array via proper 
            decorator access and re-checks it natively for null existence and zero-length parity.
        """
        if path is None:
            return False
            
        positions = path.getPositions
        if positions is None or len(positions) == 0:
            return False
            
        return True

    def _checkPathLength(self, board: Board, path: SolutionPath) -> bool:
        """
        Validates if the absolute linear step count seamlessly matches the total topological volume.

        Args:
            board: The foundational spatial layout strictly determining dimensional limits.
            path: The compiled chronology list representing complete executed pathways.

        Returns:
            The verification flag proving the sequence volume satisfies baseline spatial requirements.

        Implementation Details:
            Invokes internal existence validation to securely filter null states. Extracts the raw 
            dimensional baseline via property hooks, mathematically squares the scalar to derive exact 
            cellular volume, and strictly compares it against the raw native length of the trajectory list.
        """
        if not self._checkPathExists(path):
            return False
            
        return len(path.getPositions) == (board.getSize ** 2)

    def validate(self, board: Board, path: SolutionPath) -> ValidationResult:
        """
        Orchestrates an exhaustive, multi-tiered authenticity diagnostic on a proposed puzzle solution.

        Args:
            board: The rigid physical layout dictating localized grid dimensions and waypoint mechanics.
            path: The chronologically indexed tracking map submitted for authoritative evaluation.

        Returns:
            The finalized structured response detailing the absolute operational status and specific infractions.

        Implementation Details:
            Executes a sequential, defensive validation hierarchy. Phase 1 guarantees fundamental structure, 
            short-circuiting immediately and generating specific empty-path faults if breached. Phase 2 
            mandates mathematical volumetric alignment against the board, ejecting invalid-length errors 
            upon failure. Phase 3 extracts the unboxed coordinate array and subjects it to the stateless 
            evaluation engine for intense algorithmic scrutiny, returning rule-violation records if rejected. 
            Phase 4 finalizes the operation by actively yielding a clean, error-free success payload.
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