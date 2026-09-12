from typing import Optional

from .solver_metrics import SolverMetrics
from .solver_status import SolverStatus
from backend.solution_path import SolutionPath


class SolverResponse:
    """
    Defines the finalized, comprehensive payload dispatched by the orchestration layer.

    Responsibility:
        Wraps internal solver results with additional macro-level orchestration context
        (e.g., which specific engine was deployed) to fulfill strict external API contracts.
        It bridges legacy boolean success indicators with modern, high-granularity status enums.

    Implementation Details:
        Acts as a read-only data boundary. Preserves critical backward compatibility with
        older API integrations by injecting dynamic constructor logic that artificially
        derives an appropriate enum state if the caller only furnishes a legacy binary success flag.
    """

    def __init__(
        self,
        success: bool,
        path: Optional[SolutionPath],
        message: str,
        solverUsed: str,
        metrics: SolverMetrics,
        status: Optional[SolverStatus] = None,
    ):
        """
        Initializes the comprehensive external transmission payload.

        Args:
            success: The legacy binary flag indicating an overall triumphant execution.
            path: The calculated coordinate sequence, if definitively solved.
            message: A human-readable contextual string clarifying the system's outcome.
            solverUsed: The exact identifier or name of the underlying computational engine deployed.
            metrics: The compiled performance telemetry object assessing efficiency.
            status: The explicit categorical outcome state, offering deeper context than a boolean.

        Implementation Details:
            Secures all parameters inside protected fields. Actively intercepts the status
            parameter to deploy fallback logic; if missing, it dynamically casts the legacy success
            boolean into a modern success/failure enum to prevent architectural fractures downstream.
        """
        self._success = success
        self._path = path
        self._message = message
        self._solverUsed = solverUsed
        self._metrics = metrics
        # Optional and defaulted so every existing construction site keeps working. When
        # supplied it preserves the distinction the API contract requires between
        # UNSOLVABLE, TIMEOUT and FAILED, which a bare success bool cannot express.
        self._status = (
            status
            if status is not None
            else (SolverStatus.SOLVED if success else SolverStatus.FAILED)
        )

    @property
    def getStatus(self) -> SolverStatus:
        """
        Retrieves the highly specific categorical status of the overall request.

        Returns:
            The robust enum representation defining the exact failure or success condition.

        Implementation Details:
            Unlocks read-only interaction with the dynamically evaluated state attribute.
        """
        return self._status

    @property
    def getSuccess(self) -> bool:
        """
        Retrieves the simplified legacy binary indicator of the execution.

        Returns:
            True if the engine succeeded unconditionally, False otherwise.

        Implementation Details:
            Unlocks read-only interaction with the underlying binary success flag.
        """
        return self._success

    @property
    def getPath(self) -> Optional[SolutionPath]:
        """
        Retrieves the mathematical trajectory proposed by the engine.

        Returns:
            The complete route mapping, or a null omission if the puzzle defeated the engine.

        Implementation Details:
            Unlocks read-only interaction with the encapsulated spatial trajectory map.
        """
        return self._path

    @property
    def getMessage(self) -> str:
        """
        Retrieves the external-facing summary string defining the request lifecycle.

        Returns:
            The human-readable contextual notification.

        Implementation Details:
            Unlocks read-only interaction with the textual message attribute.
        """
        return self._message

    @property
    def getSolverUsed(self) -> str:
        """
        Retrieves the system identifier of the specific algorithmic module that attempted the puzzle.

        Returns:
            The nominal string tag representing the engine (e.g., 'Backtracking', 'ML_Model').

        Implementation Details:
            Unlocks read-only interaction with the protected identifier attribute.
        """
        return self._solverUsed

    @property
    def getMetrics(self) -> SolverMetrics:
        """
        Retrieves the finalized telemetry block for external monitoring and benchmarking.

        Returns:
            The structured resource usage object.

        Implementation Details:
            Unlocks read-only interaction with the encapsulated metrics block.
        """
        return self._metrics
