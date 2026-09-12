from typing import List, Set
from .data_models import Position
from .board import Board


class GameState:
    """
    Tracks and maintains the localized progression of an active Hamiltonian path attempt.

    Responsibility:
        Governs the ongoing temporal evolution of the puzzle session by carefully chronicling
        all traversed steps, archiving path histories, monitoring cell visitation statuses,
        and determining the upcoming mathematical waypoint target.

    Implementation Details:
        Employs dual internal data structures to preserve operations: an explicitly ordered list
        preserves chronological traversal histories, while an identically mapped set structure
        facilitates immediate O(1) performance lookup queries during complex movement validations.
        Operates fully isolated from rule validation logic to adhere to Separation of Concerns.
    """

    def __init__(self, startPosition: Position):
        """
        Initializes the dynamic progression tracker and stages the puzzle at a known baseline.

        Args:
            startPosition: The definitive physical coordinate marking the origination of the path.

        Implementation Details:
            Secures the active coordinate location into memory. Automatically instantiates the
            chronological list and matching internal lookup set natively populated with the original
            provided parameter. Seeds the chronological next target sequence strictly to 2.
        """
        self._currentPosition = startPosition
        self._path: List[Position] = [startPosition]
        self._visitedCells: Set[Position] = {startPosition}
        self._nextWaypointOrder = 2

    def addStep(self, position: Position):
        """
        Incorporates a newly validated spatial traversal into the chronological game state.

        Args:
            position: The localized destination coordinate finalizing the executed transition.

        Implementation Details:
            Transitions the overarching live position attribute. Sequentially appends the metric
            into the historical tracking list whilst appending it identically into the high-performance
            visitation hash set for future validation lookups.
        """
        self._currentPosition = position
        self._path.append(position)
        self._visitedCells.add(position)

    def isVisited(self, position: Position) -> bool:
        """
        Interrogates the ongoing history to verify if a coordinate has already been occupied.

        Args:
            position: The targeted spatial coordinate to query against memory banks.

        Returns:
            True if the specified localized metric was historically tracked, False otherwise.

        Implementation Details:
            Queries the underlying protected hash set of visited cells, guaranteeing rapid
            O(1) time complexity logic evaluation critical for tight loop validations.
        """
        return position in self._visitedCells

    def getUnvisitedCells(self, board: Board) -> Set[Position]:
        """
        Isolates and computes the remaining available puzzle cells untouched by the current history.

        Args:
            board: The baseline blueprint orchestrating physical boundaries and cell counts.

        Returns:
            A unique set enclosing all physical coordinates absent from current path histories.

        Implementation Details:
            Leverages high-speed Python native set mathematics. Triggers the baseline board to
            generate a full scope matrix layout and subtracts the internal protected visitation
            set, instantly yielding mathematically unpopulated boundaries.
        """
        return board.getAllPositions() - self._visitedCells

    def reset(self, startPosition: Position):
        """
        Terminates active sequence histories and forcefully returns internal tracking to a fresh start.

        Args:
            startPosition: The baseline original anchor point resolving the pristine game launch.

        Implementation Details:
            Purges active history sets and lists, entirely replacing them with identical single-element
            data structures. Fully overrides the chronological progression target constraint back to 2.
        """
        self._currentPosition = startPosition
        self._path = [startPosition]
        self._visitedCells = {startPosition}
        self._nextWaypointOrder = 2

    # NEW METHOD
    def incrementNextWaypointOrder(self):
        """
        Dynamically escalates the chronological waypoint sequence tracker to the subsequent requirement.

        Implementation Details:
            Mutates the rigidly guarded integer tracking parameter upwards by an exact magnitude of 1,
            signifying the successful traversal over a mandatory targeted puzzle sequence.
        """
        self._nextWaypointOrder += 1

    @property
    def getCurrentPosition(self) -> Position:
        """
        Retrieves the exact present coordinate actively occupying the terminal tip of the path.

        Returns:
            The localized endpoint coordinate representation.

        Implementation Details:
            Exposes immutable accessibility to the localized spatial tracker variable using
            decorator protections.
        """
        return self._currentPosition

    @property
    def getPath(self) -> List[Position]:
        """
        Reclaims the comprehensive chronological ordered sequence of movements performed thus far.

        Returns:
            A sequentially structured list of traversed coordinate milestones.

        Implementation Details:
            Reveals external access to the exact protected timeline listing managed natively
            by the internal state processor.
        """
        return self._path

    @property
    def getVisitedCells(self) -> Set[Position]:
        """
        Retrieves the high-performance hashed matrix representing globally touched grid squares.

        Returns:
            A distinct set populated with identical historically occupied variables.

        Implementation Details:
            Transmits read-access down into the encapsulated internal matrix designed for rapid evaluations.
        """
        return self._visitedCells

    @property
    def getNextWaypointOrder(self) -> int:
        """
        Extracts the strictly required mathematical chronological value needed sequentially next.

        Returns:
            The raw integer parameter expected to be intersected to maintain puzzle compliance.

        Implementation Details:
            Fetches superficial external access to the precisely tracked numerical condition variable.
        """
        return self._nextWaypointOrder
