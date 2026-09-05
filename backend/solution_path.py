from backend.puzzle_logic import Position
from typing import List


class SolutionPath:
    """
    A sequential container for tracking proposed puzzle navigational movements.

    Responsibility:
        Encapsulates a chronological list of spatial coordinates that make up a candidate
        solution, providing a standardized format for solvers to submit their paths for
        validation or rendering.

    Implementation Details:
        Maintains a protected internal list of coordinate objects. Access to this sequence
        is strictly limited to a read-only property to prevent unauthorized external mutations
        or state corruption during complex validation loops.
    """

    def __init__(self):
        """
        Initializes an empty trajectory sequence.

        Implementation Details:
            Instantiates a localized, protected Python list designed to accrue coordinate
            instances as the solution sequence is actively constructed.
        """
        self._positions: List[Position] = []

    def add(self, position: Position):
        """
        Appends a distinct spatial coordinate to the termination point of the trajectory.

        Args:
            position: The localized spatial coordinate finalizing the most recent execution step.

        Implementation Details:
            Directly calls the native append function on the protected internal list, pushing
            the new coordinate parameter chronologically onto the stack.
        """
        self._positions.append(position)

    @property
    def getPositions(self) -> List[Position]:
        """
        Retrieves the comprehensive chronological history of all registered spatial transitions.

        Returns:
            The unbroken sequence mapping the complete attempted trajectory.

        Implementation Details:
            Unlocks immutable exterior access to the strictly protected chronological array
            using a property decorator hook.
        """
        return self._positions
