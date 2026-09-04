from typing import List
from .board import Board
from .game_state import GameState
from .data_models import Position


class PuzzleRules:
    """
    Enforces the rules and movement constraints of the puzzle.

    Responsibility:
        Serves as the rule-checking engine. It determines whether individual moves are 
        allowed (checking boundaries, walls, unvisited cells, and waypoint order) and 
        verifies whether a full path solves the puzzle.

    Implementation Details:
        Operates statelessly without modifying game data. Validates moves and complete 
        solutions by checking conditions sequentially and returning False as soon as any 
        rule is violated.
    """

    def isValidMove(self, board: Board, state: GameState, target: Position) -> bool:
        """
        Checks if moving to the target position is a valid next step.

        Args:
            board: The puzzle board containing grid boundaries and walls.
            state: The current game state tracking the path and visited cells.
            target: The position the player wants to move to.

        Returns:
            True if the move obeys all game rules; False otherwise.

        Implementation Details:
            Performs checks in order:
            1. Target is within board boundaries.
            2. Target is adjacent to the current position.
            3. No wall blocks the move between current position and target.
            4. Target has not already been visited.
            5. Target does not violate waypoint visit order.
            6. Target satisfies the endpoint rule (final waypoint entered only on the last move).
        """
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

        # NEW: the highest waypoint must be the endpoint
        if not self._preservesEndpointRule(board, state, target):
            return False

        return True

    def isCompleteSolution(self, board: Board, path: List[Position]) -> bool:
        """
        Checks whether a complete path successfully solves the puzzle.

        Args:
            board: The puzzle board defining the rules and layout.
            path: The sequence of positions representing the full path.

        Returns:
            True if the path satisfies all winning conditions; False otherwise.

        Implementation Details:
            Verifies all conditions for a solved puzzle:
            1. Starts at waypoint 1.
            2. Ends at the highest-numbered waypoint.
            3. Visits every cell on the board exactly once.
            4. Contains only valid, connected moves with no wall collisions.
            5. Visits all waypoints in ascending order.
        """
        return (
            self._startsAtFirstWaypoint(board, path)
            and self._endsAtLastWaypoint(board, path)
            and self._coversEveryCellExactlyOnce(board, path)
            and self._containsOnlyValidMoves(board, path)
            and self._visitsWaypointsInCorrectOrder(board, path)
        )


    # PRIVATE METHODS:
    def _preservesWaypointOrder(self, board: Board, state: GameState, target: Position) -> bool:
        """
        Checks if moving to the target cell follows waypoint ordering rules.

        Args:
            board: The puzzle board containing waypoint locations.
            state: The current game state tracking the next expected waypoint order.
            target: The position being moved into.

        Returns:
            True if the move is allowed; False if it visits a waypoint out of order.

        Implementation Details:
            Queries the board for a waypoint at the target position. If none exists, 
            allows the move (returns True). If a waypoint is present, checks whether its order 
            strictly equals the next expected waypoint order from the game state.
        """
        waypoint = board.getWaypointAt(target)

        if waypoint is None:
            return True

        return waypoint.getOrder == state.getNextWaypointOrder

    def _coversEveryCellExactlyOnce(self, board: Board, path: List[Position]) -> bool:
        """
        Checks if the path visits every cell on the board exactly once.

        Args:
            board: The puzzle board to compare against.
            path: The path of visited positions.

        Returns:
            True if every board cell is visited exactly once; False otherwise.

        Implementation Details:
            Follows a two-step verification:
            1. Confirms the path length matches the total number of cells on the board.
            2. Converts the path to a set and verifies it contains all board positions, 
               ensuring full coverage with no repeated cells.
        """
        return len(path) == board.getCellCount() and set(path) == board.getAllPositions()

    def _containsOnlyValidMoves(self, board: Board, path: List[Position]) -> bool:
        """
        Verifies that every step in the path is continuous and avoids walls.

        Args:
            board: The puzzle board with boundaries and walls.
            path: The list of positions to verify.

        Returns:
            True if all consecutive steps are adjacent and not blocked by walls; False otherwise.

        Implementation Details:
            Follows a three-step continuity check:
            1. Verifies the path is not empty or null.
            2. Checks that every position in the path lies inside the board boundaries.
            3. Iterates over consecutive pairs of positions to ensure each move is cardinally 
               adjacent and has no wall between them.
        """
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
        """
        Verifies that all waypoints are visited in ascending numerical order along the path.

        Args:
            board: The puzzle board containing waypoints.
            path: The path to check.

        Returns:
            True if waypoints are visited in strictly ascending order; False otherwise.

        Implementation Details:
            Follows a three-step waypoint ordering check:
            1. Scans the path to collect the order numbers of all waypoints visited.
            2. Retrieves and sorts all waypoint orders configured on the board.
            3. Compares the two sequences to verify waypoints are visited in strictly ascending order.
        """
        waypoint_orders = []

        for pos in path:
            waypoint = board.getWaypointAt(pos)
            
            if waypoint is not None:
                waypoint_orders.append(waypoint.getOrder)

        expected_orders = sorted([wp.getOrder for wp in board.getWaypoints])

        return expected_orders == waypoint_orders
    
    # NEW METHOD
    def _preservesEndpointRule(self, board: Board, state: GameState, target: Position) -> bool:
        """
        Ensures the final waypoint is only entered as the very last move of the puzzle.

        Args:
            board: The puzzle board containing waypoints.
            state: The current game state.
            target: The position to move to.

        Returns:
            True if moving to or from the final waypoint is allowed; False otherwise.

        Implementation Details:
            Enforces endpoint constraints through two rules:
            1. If currently standing on the final waypoint, prevents moving away from it.
            2. If attempting to step onto the final waypoint, only permits the move if it would
               visit the last remaining cell on the board (path length + 1 equals total cell count).
        """
        waypoints = board.getWaypoints
        if not waypoints:
            return True

        last_order = max(wp.getOrder for wp in waypoints)

        current = state.getCurrentPosition
        current_waypoint = board.getWaypointAt(current)
        target_waypoint = board.getWaypointAt(target)

        # If we are already on the final waypoint, we may not move away from it.
        if current_waypoint is not None and current_waypoint.getOrder == last_order:
            return False

        # We may only enter the final waypoint if this move completes the whole board.
        if target_waypoint is not None and target_waypoint.getOrder == last_order:
            return len(state.getPath) + 1 == board.getCellCount()

        return True
    
    def _startsAtFirstWaypoint(self, board: Board, path: List[Position]) -> bool:
        """
        Checks if the path begins at waypoint 1.

        Args:
            board: The puzzle board to look up waypoint 1.
            path: The solution path to check.

        Returns:
            True if the first position in the path matches waypoint 1; False otherwise.

        Implementation Details:
            Verifies the path is not empty, retrieves waypoint 1 from the board, and 
            confirms that the first position in the path (index 0) matches its location.
        """
        if not path:
            return False

        first_waypoint = board.getWaypointByOrder(1)
        if first_waypoint is None:
            return False

        return path[0] == first_waypoint.getPosition


    def _endsAtLastWaypoint(self, board: Board, path: List[Position]) -> bool:
        """
        Checks if the path ends at the highest-numbered waypoint.

        Args:
            board: The puzzle board containing waypoints.
            path: The solution path to check.

        Returns:
            True if the last position in the path matches the final waypoint; False otherwise.

        Implementation Details:
            Verifies the path is not empty, finds the waypoint with the highest order number 
            on the board, and confirms that the last position in the path (index -1) matches its location.
        """
        if not path:
            return False

        waypoints = board.getWaypoints
        if not waypoints:
            return False

        last_order = max(wp.getOrder for wp in waypoints)
        last_waypoint = board.getWaypointByOrder(last_order)

        if last_waypoint is None:
            return False

        return path[-1] == last_waypoint.getPosition