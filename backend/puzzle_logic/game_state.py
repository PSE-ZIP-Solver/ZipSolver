from typing import List, Set
from .models import Position
from .board import Board


class GameState:
    """Represents the current state of a Zip puzzle game."""

    def __init__(self, startPosition: Position):
        self._currentPosition = startPosition
        self._path: List[Position] = [startPosition]
        self._visitedCells: Set[Position] = {startPosition}
        self._nextWaypointOrder = 2

    def addStep(self, position: Position):
        """Add a new position to the path and mark it as visited."""
        self._currentPosition = position
        self._path.append(position)
        self._visitedCells.add(position)

    def isVisited(self, position: Position) -> bool:
        """Return True if the position has already been visited."""
        return position in self._visitedCells

    def getUnvisitedCells(self, board: Board) -> Set[Position]:
        """Return all board positions that have not been visited yet."""
        return board.getAllPositions() - self._visitedCells

    def reset(self, startPosition: Position):
        """Reset the state to the given start position."""
        self._currentPosition = startPosition
        self._path = [startPosition]
        self._visitedCells = {startPosition}
        self._nextWaypointOrder = 2

    # NEW METHOD
    def incrementNextWaypointOrder(self):
        """Increase the next waypoint order after reaching a waypoint."""
        self._nextWaypointOrder += 1


    @property
    def getCurrentPosition(self) -> Position:
        return self._currentPosition

    @property
    def getPath(self) -> List[Position]:
        return self._path

    @property
    def getVisitedCells(self) -> Set[Position]:
        return self._visitedCells

    @property
    def getNextWaypointOrder(self) -> int:
        return self._nextWaypointOrder