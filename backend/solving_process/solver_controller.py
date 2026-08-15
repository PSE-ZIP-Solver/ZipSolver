import logging
from backend.puzzle_logic.board import Board
from .solver_result import SolverResult
from .solver_response import SolverResponse
from .solver_metrics import SolverMetrics
from .solver_status import SolverStatus
from backend.validation_result import ValidationResult

DFS_TIMEOUT_MS = 10000
logger = logging.getLogger(__name__)

class SolverController:
    def __init__(self, rl_solver=None, algorithmic_solver=None, solution_validator=None):
        # The RL solver is resolved on first use, not here. Importing it eagerly pulls in
        # the whole learning stack (gymnasium -> stable-baselines3 -> torch), which made
        # application start-up — and therefore GET /api/health — fail outright whenever
        # those packages were absent. Deferring keeps the service bootable and degrades to
        # the algorithmic solver instead, which is what the fallback strategy is for.
        self._rlSolver = rl_solver
        self._rlSolverUnavailable = False

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

    def _resolveRlSolver(self):
        """Return the RL solver, importing it on first use.

        A missing RL stack is recorded once and never retried, so a torch-less deployment
        pays the import cost a single time and then goes straight to the fallback.
        """
        if self._rlSolver is not None:
            return self._rlSolver
        if self._rlSolverUnavailable:
            return None

        try:
            from .rl_solver import RLSolver

            self._rlSolver = RLSolver()
        except Exception as e:  # noqa: BLE001 - ImportError or model-registry failure
            logger.warning(
                f"RL solver unavailable ({e}); using the algorithmic solver only."
            )
            self._rlSolverUnavailable = True
            return None

        return self._rlSolver

    def _runRlSolver(self, board: Board) -> SolverResult:
        solver = self._resolveRlSolver()
        if solver is None:
            raise RuntimeError("No RL solver is available.")
        return solver.solve(board)

    def _runFallbackSolver(self, board: Board) -> SolverResult:
        return self._algorithmicSolver.solve(board)

    def _validateCandidate(self, board: Board, result: SolverResult) -> ValidationResult:
        # Rule Enforcement: Strictly passing the protected _path attribute 
        if result._path is None:
            raise ValueError("Cannot validate a result with no path")
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

            # Both solvers completed, but no path was valid. The algorithmic solver already
            # distinguished UNSOLVABLE from TIMEOUT from FAILED; forward that verdict
            # instead of flattening it into a bare `success=False`, which the API can only
            # render as FAILED. A SOLVED result that failed re-validation is not
            # "unsolvable" — it is a solver failure, so it is reported as FAILED.
            algo_status = algo_result._status
            if algo_status == SolverStatus.SOLVED:
                algo_status = SolverStatus.FAILED

            return SolverResponse(
                success=False,
                path=None,
                message=self._message_for(algo_status),
                solverUsed="AlgorithmicSolver",
                metrics=algo_result._metrics,
                status=algo_status
            )
            
        except Exception as e:
            # Fallback crashed, handle gracefully
            logger.error(f"Algorithmic Solver failed with exception: {e}.")
            return SolverResponse(
                success=False,
                path=None,
                message="Solving failed due to internal error.",
                solverUsed="AlgorithmicSolver",
                metrics=SolverMetrics(runtimeMs=0, steps=0, attempts=1),
                status=SolverStatus.FAILED
            )

    @staticmethod
    def _message_for(status: SolverStatus) -> str:
        return {
            SolverStatus.UNSOLVABLE: "No solution exists for this board.",
            SolverStatus.TIMEOUT: "The solver reached its time limit before finding a solution.",
        }.get(status, "No valid solution found by any solver.")