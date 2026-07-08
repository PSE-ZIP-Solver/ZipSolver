from backend.puzzle_logic.board import Board
from solver_result import SolverResult
from solver_response import SolverResponse
from rl_solver import RLSolver
from algorithmic_solver import AlgorithmicSolver
from backend.solution_validator import SolutionValidator
from backend.validation_result import ValidationResult


class SolverController:
    def __init__(self):
        self._rlSolver = RLSolver()
        self._algorithmicSolver = AlgorithmicSolver()
        self._solutionValidator = SolutionValidator()

    def _runRlSolver(self, board: Board) -> SolverResult:
        """
        Starts the RL-based solver for the given board.
        """
        return self._rlSolver.solve(board)

    def _runFallbackSolver(self, board: Board) -> SolverResult:
        """
        Starts the algorithmic Fallback solver.
        """
        return self._algorithmicSolver.solve(board)

    def _validateCandidate(self, board: Board, result: SolverResult) -> ValidationResult:
        """
        Validates a candidate solution returned by a solver.
        """
        # We only pass the path to the validator if we assume it validates paths directly.
        # Based on typical implementations, SolutionValidator accepts the board and the path.
        return self._solutionValidator.validate(board, result.getPath)

    def solve(self, board: Board) -> SolverResponse:
        """
        Runs the solving process, orchestrates solvers and validation, 
        and returns the final response.
        """
        # --- Attempt 1: RL Solver ---
        rl_result = self._runRlSolver(board)

        if rl_result.hasSolution():
            validation = self._validateCandidate(board, rl_result)
            
            if validation.isValid:
                return SolverResponse(
                    success=True,
                    path=rl_result.getPath,
                    message="Successfully solved using RL Agent.",
                    solverUsed="RLSolver",
                    metrics=rl_result.getMetrics
                )

        # --- Attempt 2: Algorithmic Fallback ---
        algo_result = self._runFallbackSolver(board)

        if algo_result.hasSolution():
            validation = self._validateCandidate(board, algo_result)
            
            if validation.isValid:
                return SolverResponse(
                    success=True,
                    path=algo_result.getPath,
                    message="Successfully solved using Algorithmic Fallback.",
                    solverUsed="AlgorithmicSolver",
                    metrics=algo_result.getMetrics
                )

        # --- Both Solvers Failed ---
        return SolverResponse(
            success=False,
            path=None,
            message="No valid solution found by any solver.",
            solverUsed="AlgorithmicSolver",  # Last solver attempted
            metrics=algo_result.getMetrics
        )