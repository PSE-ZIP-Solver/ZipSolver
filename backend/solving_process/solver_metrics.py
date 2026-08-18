class SolverMetrics:
    """
    Encapsulates performance and resource utilization statistics for a single solving attempt.

    Responsibility:
        Acts as a standardized telemetry wrapper tracking quantitative operational data, 
        allowing the orchestration layer to monitor algorithm efficiency, benchmark execution 
        speeds, and expose processing complexity to external observers.

    Implementation Details:
        Functions as a read-only Data Transfer Object (DTO). Captures raw analytical parameters 
        during instantiation, secures them within protected attributes, and exposes them 
        strictly via property decorators to prevent mid-flight metric tampering.
    """
    def __init__(self, runtimeMs: int, steps: int, attempts: int):
        """
        Initializes the performance telemetry wrapper.

        Args:
            runtimeMs: The total elapsed execution time evaluated in milliseconds.
            steps: The overall quantity of discrete operations or localized grid checks performed.
            attempts: The cumulative tally of algorithmic backtracks or repeated engine starts.

        Implementation Details:
            Binds the provided statistical parameters directly into protected internal 
            attributes to secure the telemetry state memory.
        """
        self._runtimeMs = runtimeMs
        self._steps = steps
        self._attempts = attempts

    @property
    def getRuntimeMs(self) -> int:
        """
        Retrieves the total temporal duration consumed by the algorithmic process.

        Returns:
            The execution span measured in milliseconds.

        Implementation Details:
            Exposes immutable external access to the protected chronological tracker via a property hook.
        """
        return self._runtimeMs

    @property
    def getSteps(self) -> int:
        """
        Retrieves the sheer volume of algorithmic maneuvers evaluated during execution.

        Returns:
            The sequential operation count.

        Implementation Details:
            Exposes immutable external access to the protected steps integer via a property hook.
        """
        return self._steps

    @property
    def getAttempts(self) -> int:
        """
        Retrieves the frequency of retry operations or macro-level branch evaluations.

        Returns:
            The cumulative fallback tally.

        Implementation Details:
            Exposes immutable external access to the protected attempts integer via a property hook.
        """
        return self._attempts