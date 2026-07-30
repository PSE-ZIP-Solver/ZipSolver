import logging
import os
from struct import pack

from backend.puzzle_logic.board import Board
from .solver_result import SolverResult
from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics
from .rl_solver import RLSolver
from .algorithmic_solver import AlgorithmicSolver
from backend.solution_validator import SolutionValidator
from backend.validation_result import ValidationResult

logger = logging.getLogger(__name__)

DFS_TIMEOUT_MS = 10000

# Wire identifiers surfaced to the frontend. Deliberately not the class names — the
# frontend's SolverStatus union expects these short forms.
SOLVER_RL = "RL"
SOLVER_ALGORITHMIC = "DFS"


class SolverController:
    """Orchestrates the RL-first, algorithmic-fallback solving strategy.

    Returns a single rich ``SolverResult`` so the distinction between UNSOLVABLE,
    TIMEOUT, and FAILED survives all the way to the API. (The previous version collapsed
    every unsuccessful run into a boolean, which meant the frontend could only ever
    display a generic failure regardless of cause.)

    Every candidate path is re-validated against ``SolutionValidator`` before being
    accepted — neither solver is trusted as a correctness oracle.
    """

    def __init__(self, model_path: str = "agent.zip"):
        self._model_path = model_path
        self._rlSolver = RLSolver(model_path)
        self._algorithmicSolver = AlgorithmicSolver(DFS_TIMEOUT_MS)
        self._solutionValidator = SolutionValidator()
        self._rl_available: bool | None = None

    # ── RL availability ─────────────────────────────────────────────────────

    def _isRlAvailable(self) -> bool:
        """Whether a trained model artifact exists on disk.

        Checked once and cached. Without this guard every request paid for a failed
        model load and dumped a stack trace before falling back. When the offline
        training pipeline produces an artifact at ``model_path``, RL activates with no
        code change here — that is the intended integration point for the trainer.
        """
        if self._rl_available is None:
            candidates = (self._model_path, f"{self._model_path}.zip")
            self._rl_available = any(os.path.exists(p) for p in candidates)
            if not self._rl_available:
                logger.info(
                    "No RL model artifact found at %r; using the algorithmic solver only.",
                    self._model_path,
                )
        return self._rl_available

    # ── Attempts ────────────────────────────────────────────────────────────

    def _runRlSolver(self, board: Board) -> SolverResult:
        """Starts the RL-based solver for the given board."""
        return self._rlSolver.solve(board)

    def _runFallbackSolver(self, board: Board) -> SolverResult:
        """Starts the algorithmic fallback solver."""
        return self._algorithmicSolver.solve(board)

    def _validateCandidate(self, board: Board, result: SolverResult) -> ValidationResult:
        path = result.getPath
        if path is None:
            raise ValueError("Cannot validate a result with no path.")
        """Validates a candidate solution returned by a solver."""
        return self._solutionValidator.validate(board, path)

    # ── Orchestration ───────────────────────────────────────────────────────

    def solve(self, board: Board) -> SolverResult:
        runtime_ms = 0
        steps = 0
        attempts = 0

        def totals() -> SolverMetrics:
            # attempts is clamped to at least 1: a result exists, so something ran.
            return SolverMetrics(
                runtimeMs=runtime_ms, steps=steps, attempts=max(1, attempts)
            )

        # --- Attempt 1: RL solver (skipped entirely when no artifact is present) ---
        if self._isRlAvailable():
            attempts += 1
            rl_result = self._runRlSolver(board)
            runtime_ms += rl_result.getMetrics.getRuntimeMs
            steps += rl_result.getMetrics.getSteps

            if rl_result.hasSolution() and self._validateCandidate(board, rl_result).isValid:
                return SolverResult(
                    status=SolverStatus.SOLVED,
                    path=rl_result.getPath,
                    message="Successfully solved using the RL agent.",
                    metrics=totals(),
                    solverUsed=SOLVER_RL,
                )
            if rl_result.hasSolution():
                logger.warning("RL agent returned a path that failed validation; falling back.")

        # --- Attempt 2: algorithmic fallback ---
        attempts += 1
        algo_result = self._runFallbackSolver(board)
        runtime_ms += algo_result.getMetrics.getRuntimeMs
        steps += algo_result.getMetrics.getSteps

        if algo_result.hasSolution():
            if self._validateCandidate(board, algo_result).isValid:
                return SolverResult(
                    status=SolverStatus.SOLVED,
                    path=algo_result.getPath,
                    message="Successfully solved using the algorithmic fallback.",
                    metrics=totals(),
                    solverUsed=SOLVER_ALGORITHMIC,
                )
            # A path that fails validation is a solver defect, not a puzzle outcome.
            logger.error("Algorithmic solver produced a path that failed validation.")
            return SolverResult(
                status=SolverStatus.FAILED,
                path=None,
                message="The solver produced a path that failed validation.",
                metrics=totals(),
                solverUsed=SOLVER_ALGORITHMIC,
            )

        # --- Neither solver produced a valid path ---
        # The algorithmic solver's status is authoritative: an exhausted search proves
        # UNSOLVABLE, whereas a timeout only means "not determined within the budget".
        return SolverResult(
            status=algo_result.getStatus,
            path=None,
            message=algo_result.getMessage,
            metrics=totals(),
            solverUsed=SOLVER_ALGORITHMIC,
        )