from typing import List, Set
from .data_models import Position
from .board import Board


class GameState:
    """
    Tracks the current progress and history of moves in a puzzle game.

    Responsibility:
        Maintains the player's current position, the sequence of moves made so far, 
        the set of visited cells, and the next waypoint number that needs to be reached.

    Implementation Details:
        Stores the path as an ordered list of positions and keeps a matching set of 
        visited positions for fast lookup. Does not validate moves itself, focusing 
        purely on tracking state.
    """

    def __init__(self, startPosition: Position):
        """
        Initializes game state at the given starting position.

        Args:
            startPosition: The position where the game begins.

        Implementation Details:
            Sets the current position, initializes the path and visited set with the start 
            position, and sets the next expected waypoint order to 2.
        """
        self._currentPosition = startPosition
        self._path: List[Position] = [startPosition]
        self._visitedCells: Set[Position] = {startPosition}
        self._nextWaypointOrder = 2

    def addStep(self, position: Position):
        """
        Records a move to a new position.

        Args:
            position: The new position to add to the path.

        Returns:
            None.

        Implementation Details:
            Updates the current position to the given position, appends it to the 
            chronological path list, and inserts it into the visited cells set.
        """
        self._currentPosition = position
        self._path.append(position)
        self._visitedCells.add(position)

    def isVisited(self, position: Position) -> bool:
        """
        Checks whether a position has already been visited.

        Args:
            position: The position to check.

        Returns:
            True if the position is in the visited set; False otherwise.

        Implementation Details:
            Performs a fast set membership lookup in the internal visited cells set.
        """
        return position in self._visitedCells

    def getUnvisitedCells(self, board: Board) -> Set[Position]:
        """
        Finds all cells on the board that have not yet been visited.

        Args:
            board: The board to check against.

        Returns:
            A set of positions that have not been visited yet.

        Implementation Details:
            Queries the board for all valid cell positions and performs a set difference 
            against the visited cells set to yield all untouched positions.
        """
        return board.getAllPositions() - self._visitedCells

    def reset(self, startPosition: Position):
        """
        Resets the game state back to the starting position.

        Args:
            startPosition: The initial position to restart from.

        Returns:
            None.

        Implementation Details:
            Sets the current position to startPosition, replaces both the path list and 
            the visited set with single-element collections containing only startPosition, 
            and resets the next expected waypoint order back to 2.
        """
        self._currentPosition = startPosition
        self._path = [startPosition]
        self._visitedCells = {startPosition}
        self._nextWaypointOrder = 2

    # NEW METHOD
    def incrementNextWaypointOrder(self):
        """
        Advances the next expected waypoint number by one.

        Returns:
            None.

        Implementation Details:
            Increments the internal next waypoint order integer attribute by 1.
        """
        self._nextWaypointOrder += 1


    @property
    def getCurrentPosition(self) -> Position:
        """
        Gets the current position in the game.

        Returns:
            The most recent position reached in the path.

        Implementation Details:
            Exposes read-only access to the internal current position attribute via a property decorator.
        """
        return self._currentPosition

    @property
    def getPath(self) -> List[Position]:
        """
        Gets the full sequence of moves made so far.

        Returns:
            The list of positions representing the path taken.

        Implementation Details:
            Exposes read-only access to the internal path list via a property decorator.
        """
        return self._path

    @property
    def getVisitedCells(self) -> Set[Position]:
        """
        Gets the set of all visited cells.

        Returns:
            The set of positions that have been visited.

        Implementation Details:
            Exposes read-only access to the internal visited cells set via a property decorator.
        """
        return self._visitedCells

    @property
    def getNextWaypointOrder(self) -> int:
        """
        Gets the order number of the next waypoint that must be visited.

        Returns:
            The next expected waypoint order number.

        Implementation Details:
            Exposes read-only access to the internal next waypoint order integer via a property decorator.
        """
        return self._nextWaypointOrder