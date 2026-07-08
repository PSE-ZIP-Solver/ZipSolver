from enum import Enum

class SolverStatus(Enum):
    SOLVED = "SOLVED"
    UNSOLVABLE = "UNSOLVABLE"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    