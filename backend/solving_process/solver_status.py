from enum import Enum

class SolverStatus(Enum):
    """
    Enumerates the definitive completion states of a board solving execution.

    Responsibility:
        Defines a strict, type-safe vocabulary for communicating specific algorithm outcomes, 
        differentiating between a successful completion, mathematical impossibility, 
        resource exhaustion (timeout), or a systemic crash.

    Implementation Details:
        Subclasses Python's native `Enum` to guarantee immutable, singleton-like state constants 
        across the application. Values are strictly mirrored as exact string representations to 
        ensure safe, unboxed JSON serialization during external API transmissions.
    """
    SOLVED = "SOLVED"
    UNSOLVABLE = "UNSOLVABLE"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"