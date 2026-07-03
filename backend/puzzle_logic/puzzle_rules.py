from typing import List
from .board import Board
from .game_state import GameState
from .data_models import Position


class PuzzleRules:
    """Checks whether moves and solution paths satisfy the Zip puzzle rules."""

    def isValidMove(self, board: Board, state: GameState, target: Position) -> bool:
        """Return True if the target position is a valid next move."""
        current = state.getCurrentPosition

        if not board.isInside(target):
            return False

        if not board.areAdjacent(current, target):
            return False

        if board.hasWallBetween(current, target):
            return False

        if state.isVisited(target):
            return False

        if not self._preservesWaypointOrder(board, state, target):
            return False

        return True

    def isCompleteSolution(self, board: Board, path: List[Position]) -> bool:
        """Return True if the path is a complete valid solution."""
        return (
            self._coversEveryCellExactlyOnce(board, path)
            and self._containsOnlyValidMoves(board, path)
            and self._visitsWaypointsInCorrectOrder(board, path)
        )


    # PRIVATE METHODS:
    def _preservesWaypointOrder(self, board: Board, state: GameState, target: Position) -> bool:
        waypoint = board.getWaypointAt(target)

        if waypoint is None:
            return True

        return waypoint.getOrder == state.getNextWaypointOrder

    def _coversEveryCellExactlyOnce(self, board: Board, path: List[Position]) -> bool:

        return len(path) == board.getCellCount() and set(path) == board.getAllPositions()

    def _containsOnlyValidMoves(self, board: Board, path: List[Position]) -> bool:
        #Path empty or None
        if not path:
            return False
        
        #path inside Grid
        for pos in path: 
            if not board.isInside(pos):
                return False
        
        #path is continuous and has no walls between
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]

            if not board.areAdjacent(current, next_pos):
                return False
            
            if board.hasWallBetween(current, next_pos):
                return False

        return True

    # NEW METHODE
    def _visitsWaypointsInCorrectOrder(self, board: Board, path: List[Position]) -> bool:
        waypoint_orders = []

        for pos in path:
            waypoint = board.getWaypointAt(pos)
            
            if waypoint is not None:
                waypoint_orders.append(waypoint.getOrder)

        expected_orders = sorted([wp.getOrder for wp in board.getWaypoints])

        return expected_orders == waypoint_orders
