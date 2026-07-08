class SolverMetrics:
    def __init__(self, runtimeMs: int, steps: int, attempts: int):
        self._runtimeMs = runtimeMs
        self._steps = steps
        self._attempts = attempts

    @property
    def getRuntimeMs(self) -> int:
        return self._runtimeMs

    @property
    def getSteps(self) -> int:
        return self._steps

    @property
    def getAttempts(self) -> int:
        return self._attempts