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
    """
    Orchestrates the lifecycle and fallback strategies of multiple solving engines.

    Responsibility:
        Acts as the primary traffic controller for incoming puzzle requests. It securely attempts
        high-performance Machine Learning resolution first, seamlessly degrades to an exhaustive
        algorithmic approach if the ML model fails or is unavailable, and ensures all outputs
        are rigorously mathematically validated before dispatching them.

    Implementation Details:
        Employs a defensive, fault-tolerant execution pipeline. It heavily utilizes lazy-loading
        for the Reinforcement Learning stack to prevent critical CI/CD or health-check crashes
        on systems lacking ML dependencies. Exceptions thrown by engines are swallowed and logged
        to ensure the fallback sequence remains unbroken.
    """

    def __init__(
        self, rl_solver=None, algorithmic_solver=None, solution_validator=None
    ):
        """
        Initializes the orchestration pipeline and its associated computational dependencies.

        Args:
            rl_solver: An optional pre-instantiated neural network solver for dependency injection.
            algorithmic_solver: An optional pre-instantiated deterministic engine for fallbacks.
            solution_validator: An optional pre-instantiated mathematical verification gateway.

        Implementation Details:
            Safely delays the importation and instantiation of the RL module. Configures
            standalone algorithmic and validation fallback instances natively if they are not
            explicitly provided via constructor injection.
        """
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
        """
        Safely attempts to provision the Machine Learning solver into active memory.

        Returns:
            The instantiated network engine, or None if the underlying dependencies are absent.

        Implementation Details:
            A missing RL stack is recorded once and never retried, so a torch-less deployment
            pays the import cost a single time and then goes straight to the fallback.
            Catches deep ImportErrors or registry faults and flips a protected boolean flag
            to permanently bypass subsequent instantiation attempts.
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
        """
        Triggers a resolution attempt using the Machine Learning engine.

        Args:
            board: The baseline grid configuration detailing walls and milestones.

        Returns:
            The standard outcome envelope containing the ML model's computed trajectory.

        Raises:
            RuntimeError: If execution is requested but the engine failed its resolution check.

        Implementation Details:
            Forces an internal resolution check. If successful, directly invokes the inherited
            solve interface on the active neural agent.
        """
        solver = self._resolveRlSolver()
        if solver is None:
            raise RuntimeError("No RL solver is available.")
        return solver.solve(board)

    def _runFallbackSolver(self, board: Board) -> SolverResult:
        """
        Triggers a resolution attempt using the deterministic algorithmic engine.

        Args:
            board: The baseline grid configuration detailing walls and milestones.

        Returns:
            The standard outcome envelope containing the algorithmic trajectory.

        Implementation Details:
            Directly invokes the standard solve interface upon the pre-instantiated
            computational fallback module.
        """
        return self._algorithmicSolver.solve(board)

    def _validateCandidate(
        self, board: Board, result: SolverResult
    ) -> ValidationResult:
        """
        Submits a computed trajectory against the strict domain rule evaluator.

        Args:
            board: The layout configuration acting as the mathematical truth source.
            result: The raw output envelope yielded by a solving engine.

        Returns:
            The finalized compliance structure dictating absolute success or failure.

        Raises:
            ValueError: If the solver claims success but structurally provides no coordinate array.

        Implementation Details:
            Extracts the heavily protected internal path parameter from the result envelope
            and funnels it into the stateless validation module. Ensures short-circuiting
            if empty payloads bypass earlier checks.
        """
        # Rule Enforcement: Strictly passing the protected _path attribute
        if result._path is None:
            raise ValueError("Cannot validate a result with no path")
        return self._solutionValidator.validate(board, result._path)

    def solve(self, board: Board) -> SolverResponse:
        """
        Executes the overarching cascaded solving pipeline for a given puzzle.

        Args:
            board: The structured layout dictating dimensions and topological challenges.

        Returns:
            A comprehensive, externally safe payload defining the ultimate success state,
            which engine completed it, and any derived telemetry.

        Implementation Details:
            Wraps attempts in strict Try/Except blocks to guarantee pipeline continuity.
            Evaluates the RL model first; if the status specifically resolves to SOLVED and
            subsequent mathematical validation clears, immediately returns the payload.
            If it fails, crashes, or produces invalid moves, the controller swallows the error
            and seamlessly passes the puzzle to the exhaustive Algorithmic solver.
            Finally constructs a formatted response mirroring precise API failure contracts
            (e.g., separating TIMEOUT from UNSOLVABLE).
        """
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
                        path=rl_result._path,  # Rule Enforcement: protected attributes
                        message="Successfully solved using RL Agent.",
                        solverUsed="RLSolver",
                        metrics=rl_result._metrics,
                    )
        except Exception as e:
            # Prevent RL crashes from breaking the fallback sequence
            logger.warning(
                f"RL Solver failed with exception: {e}. Attempting fallback."
            )

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
                        metrics=algo_result._metrics,
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
                status=algo_status,
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
                status=SolverStatus.FAILED,
            )

    @staticmethod
    def _message_for(status: SolverStatus) -> str:
        """
        Translates a machine-readable outcome state into a human-readable summary.

        Args:
            status: The categorical flag defining the absolute outcome.

        Returns:
            A descriptive contextual string mapped to the provided state.

        Implementation Details:
            Utilizes a standard dictionary lookup pattern coupled with a `.get()` fallback
            to ensure default context is applied to unmapped error variants.
        """
        return {
            SolverStatus.UNSOLVABLE: "No solution exists for this board.",
            SolverStatus.TIMEOUT: "The solver reached its time limit before finding a solution.",
        }.get(status, "No valid solution found by any solver.")
