from typing import Optional

from .solver_status import SolverStatus
from .solver_metrics import SolverMetrics
from backend.solution_path import SolutionPath


class SolverResult:
    """
    Represents the immediate, localized outcome yielded by a specific solver algorithm.

    Responsibility:
        Consolidates the mathematical solution trajectory, execution telemetry, and terminal
        status into a single, cohesive payload. It serves as the standard internal handoff
        structure between the raw algorithmic engines and the higher-level orchestration layer.

    Implementation Details:
        Employs strict state encapsulation holding heterogenous domain models. The physical
        trajectory attribute is treated as inherently optional to gracefully support failure
        states (e.g., timeouts or unsolvable grids) without triggering null-reference exceptions downstream.
    """

    def __init__(
        self,
        status: SolverStatus,
        path: Optional[SolutionPath],
        message: str,
        metrics: SolverMetrics,
    ):
        """
        Constructs the formalized solver output package.

        Args:
            status: The categorical flag defining the absolute outcome of the run.
            path: The computed sequence of coordinates traversing the grid, if successfully derived.
            message: A human-readable contextual summary describing the execution result.
            metrics: The compiled performance telemetry object tracking resource utilization.

        Implementation Details:
            Maps the varied execution variables and domain models directly into protected
            internal parameters, firmly sealing the output state.
        """
        self._status = status
        self._path = path
        self._message = message
        self._metrics = metrics

    @property
    def getStatus(self) -> SolverStatus:
        """
        Retrieves the definitive operational outcome of the algorithmic run.

        Returns:
            The explicitly typed state constant defining the end condition.

        Implementation Details:
            Provides controlled read-access to the encapsulated Enum attribute.
        """
        return self._status

    @property
    def getPath(self) -> Optional[SolutionPath]:
        """
        Retrieves the calculated navigation trajectory, provided the algorithm found one.

        Returns:
            The chronological coordinate sequence, or an empty null state if the puzzle thwarted the engine.

        Implementation Details:
            Provides controlled read-access to the encapsulated trajectory wrapper object.
        """
        return self._path

    @property
    def getMessage(self) -> str:
        """
        Retrieves the contextual descriptive text clarifying the result.

        Returns:
            The human-readable summary detailing the final algorithmic conclusion.

        Implementation Details:
            Provides controlled read-access to the encapsulated string message attribute.
        """
        return self._message

    @property
    def getMetrics(self) -> SolverMetrics:
        """
        Retrieves the localized telemetry block summarizing resource expenditures.

        Returns:
            The structured object detailing timestamps and step counts.

        Implementation Details:
            Provides controlled read-access to the encapsulated telemetry parameter.
        """
        return self._metrics

    def hasSolution(self) -> bool:
        """
        Evaluates immediately if the execution yielded a tangible, playable output.

        Returns:
            True if the process formally completed and structurally contains a non-empty trajectory map.

        Implementation Details:
            Synthesizes a quick binary validation by cross-referencing the explicit success state
            enum against the physical presence of the trajectory wrapper object, protecting callers
            from complex conditional checks.
        """
        return self._status == SolverStatus.SOLVED and self._path is not None
