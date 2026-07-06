class TrainingResult:
    """
    Encapsulates the training result. 
    It consisting of the solve-count, the total number of solved boards, the average reward and the success rate. 
    """
    def __init__(self, solveCount: int, totalBoards: int, averageReward: float, successRate: float):
        """
        Creates a new training result. 
        It consisting of the solve-count, the total number of solved boards, the average reward and the success rate. 
        """
        self._solveCount = solveCount
        self._totalBoards = totalBoards
        self._averageReward = averageReward
        self._successRate = successRate

    @property
    def getSolveCount(self) -> int:
        return self._solveCount
    
    @property
    def getTotalBoards(self) -> int:
        return self._totalBoards
    
    @property
    def getAverageReward(self) -> float:
        return self._averageReward
    
    @property
    def getSuccessRate(self) -> float:
        return self._successRate