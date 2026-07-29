import logging
from backend.puzzle_logic.board import Board
from .solver_result import SolverResult
from .solver_response import SolverResponse
from .solver_status import SolverStatus
from backend.validation_result import ValidationResult

DFS_TIMEOUT_MS = 10000
logger = logging.getLogger(__name__)

class SolverController:
    def __init__(self, rl_solver=None, algorithmic_solver=None, solution_validator=None):
        # Lazy loading to prevent ModuleNotFoundErrors (e.g., gymnasium) during test collection
        if rl_solver is None:
            from .rl_solver import RLSolver
            self._rlSolver = RLSolver()
        else:
            self._rlSolver = rl_solver

        if algorithmic_solver is None:
            from .algorithmic_solver import AlgorithmicSolver
            self._algorithmicSolver = AlgorithmicSolver(DFS_TIMEOUT_MS)
        else:
            self._algorithmicSolver = algorithmic_solver

        if solution_validator is None:
            from backend.solution_validator import SolutionValidator
            self._solutionValidator = SolutionValidator()
        else:
            self._solutionValidator = solution_validator

    def _runRlSolver(self, board: Board) -> SolverResult:
        return self._rlSolver.solve(board)

    def _runFallbackSolver(self, board: Board) -> SolverResult:
        return self._algorithmicSolver.solve(board)

    def _validateCandidate(self, board: Board, result: SolverResult) -> ValidationResult:
        # Rule Enforcement: Strictly passing the protected _path attribute 
        return self._solutionValidator.validate(board, result._path)

    def solve(self, board: Board) -> SolverResponse:
        # --- Attempt 1: RL Solver ---
        try:
            rl_result = self._runRlSolver(board)
            
            # Rule Enforcement: Checking protected enum `_status` directly
            if rl_result._status == SolverStatus.SOLVED:
                validation = self._validateCandidate(board, rl_result)
                
                # Rule Enforcement: property without parentheses
                if validation.isValid:
                    return SolverResponse(
                        success=True,
                        path=rl_result._path, # Rule Enforcement: protected attributes
                        message="Successfully solved using RL Agent.",
                        solverUsed="RLSolver",
                        metrics=rl_result._metrics
                    )
        except Exception as e:
            # Prevent RL crashes from breaking the fallback sequence
            logger.warning(f"RL Solver failed with exception: {e}. Attempting fallback.")

        # --- Attempt 2: Algorithmic Fallback ---
        try:
            algo_result = self._runFallbackSolver(board)
            
            if algo_result._status == SolverStatus.SOLVED:
                validation = self._validateCandidate(board, algo_result)
                
                if validation.isValid:
                    return SolverResponse(
                        success=True,
                        path=algo_result._path,
                        message="Successfully solved using Algorithmic Fallback.",
                        solverUsed="AlgorithmicSolver",
                        metrics=algo_result._metrics
                    )

            # Both solvers completed, but no path was valid
            return SolverResponse(
                success=False,
                path=None,
                message="No valid solution found by any solver.",
                solverUsed="AlgorithmicSolver",
                metrics=algo_result._metrics
            )
            
        except Exception as e:
            # Fallback crashed, handle gracefully
            logger.error(f"Algorithmic Solver failed with exception: {e}.")
            return SolverResponse(
                success=False,
                path=None,
                message="Solving failed due to internal error.",
                solverUsed="AlgorithmicSolver",
                metrics=None
            )