from typing import List
from .board import Board
from .game_state import GameState
from .data_models import Position


class PuzzleRules:
    """
    Validates logical and spatial constraints dictated by the puzzle's domain restrictions.

    Responsibility:
        Functions as a stateless evaluation engine responsible for authenticating granular 
        cellular transitions against rigid physics parameters (wall avoidance, boundaries) 
        and assessing macro-level winning conditions (Hamiltonian sequencing checks).

    Implementation Details:
        Operates entirely as a detached processor without altering object state. Strictly employs 
        a defensive, fast-fail execution methodology by aggressively chaining micro-validation 
        methods and instantaneously rejecting invalid data via immediate short-circuiting.
    """

    def isValidMove(self, board: Board, state: GameState, target: Position) -> bool:
        """
        Scrutinizes a proposed movement against real-time physical constraints and game history.

        Args:
            board: The rigid physical layout detailing physical walls and dimensional parameters.
            state: The dynamically shifting active tracking profile preserving path history.
            target: The adjacent theoretical physical focal point being queried.

        Returns:
            True if all spatial restrictions align mathematically, False if any constraint triggers.

        Implementation Details:
            Invokes an explicitly sequenced chain of defensive sub-routines. Immediately short-circuits 
            upon the very first rejection. Routines include boundary containment verifications, 
            mathematical cardinational adjacencies, barrier blockage scans, visitation intersections, 
            sequential order tracking guarantees, and finally overarching endpoint mathematical locks.
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
        Computes if a finalized navigational path completely satisfies all global success constraints.

        Args:
            board: The definitive foundational blueprint enforcing target requirements.
            path: The strictly structured historical tracking listing containing full traversals.

        Returns:
            True if the route acts as a pure chronological Hamiltonian path mapping cleanly between bounds.

        Implementation Details:
            Synchronously evaluates complex success parameters natively: validates initialization 
            at the absolute lowest numerical constraint, calculates ending bounds on the terminal target, 
            checks against complete volume metrics for pure coverage without overlaps, and validates 
            ongoing barrier avoidance alongside strict sequenced sequencing checks.
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
        Assesses if navigating into a proposed coordinate breaches sequencing targets.

        Args:
            board: The underlying grid matrix defining coordinate rules.
            state: The real-time actively monitored pathway variables.
            target: The queried terminal localization coordinate.

        Returns:
            True if stepping onto the cell validates or remains neutral, False if out of chronological sync.

        Implementation Details:
            Extracts the underlying coordinate via property scans. If sterile, returns successfully. 
            If occupied, specifically checks if the mathematical configuration rigidly matches the 
            historically awaited target integer.
        """
        waypoint = board.getWaypointAt(target)

        if waypoint is None:
            return True

        return waypoint.getOrder == state.getNextWaypointOrder

    def _coversEveryCellExactlyOnce(self, board: Board, path: List[Position]) -> bool:
        """
        Quantifies if a traversal perfectly represents a mathematically true Hamiltonian pattern.

        Args:
            board: The structured baseline retaining physical scale rules.
            path: The compiled chronology list representing complete executed pathways.

        Returns:
            True if exact volumetric coverage mapping equates perfectly without duplications.

        Implementation Details:
            Pairs a highly optimized length parity verification against baseline parameters, followed 
            strictly by enforcing a dynamic set-cast against universally sourced complete grids.
        """
        return len(path) == board.getCellCount() and set(path) == board.getAllPositions()

    def _containsOnlyValidMoves(self, board: Board, path: List[Position]) -> bool:
        """
        Interrogates a complete chronology to detect any hidden physical baseline fractures.

        Args:
            board: The structural blueprint holding barriers and boundaries.
            path: The chronologically indexed path coordinates tracked dynamically.

        Returns:
            True if zero invalid shifts or wall clipping incidents appear across the timeline.

        Implementation Details:
            Short-circuits immediately against empty sequences. Sweeps the complete list iteratively 
            checking intrinsic grid limits, then iterates pairwise offsets utilizing loop mechanics to 
            determine valid sequential cardinal movements and barrier clearances.
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
        Validates the strict sequential occurrence of milestones embedded throughout a path sequence.

        Args:
            board: The structured layout managing internal configurations.
            path: The dynamically ordered history marking traversal checkpoints.

        Returns:
            True if the sequential milestones exactly match standard increasing sorted orders.

        Implementation Details:
            Provisions a fresh matrix array, subsequently stepping over every occupied localized path entry. 
            Whenever constraints arise natively on standard queries, compiles the raw parameter values. 
            Finalizes validation securely by generating sorted internal lists matching pure blueprint data.
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
        Ensures the paramount final checkpoint is definitively entered only on the last valid move.

        Args:
            board: The spatial mapping dictionary encapsulating all requirements.
            state: The overarching traversal metadata mapping current bounds.
            target: The mathematically calculated upcoming point.

        Returns:
            True if terminal protocols operate properly, False if moving violates endpoint logic.

        Implementation Details:
            Calculates extreme parameter magnitudes dynamically. Restricts active exit attempts strictly 
            from peak variables, subsequently preventing any incoming transit queries onto terminal bounds 
            unless intrinsic active chronological lengths securely equal optimal coverage mathematics.
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
        Checks if the baseline trajectory mathematically originates upon requirement 1.

        Args:
            board: The spatial mapping blueprint tracking sequence rules.
            path: The continuous chronology tracking.

        Returns:
            True if index zero properly points directly at mathematical target 1.

        Implementation Details:
            Guards rigorously against empty datasets via null traps, invokes standard numerical lookup 
            mechanisms targeting scalar parameter 1, and matches property references strictly against 
            index zero.
        """
        if not path:
            return False

        first_waypoint = board.getWaypointByOrder(1)
        if first_waypoint is None:
            return False

        return path[0] == first_waypoint.getPosition


    def _endsAtLastWaypoint(self, board: Board, path: List[Position]) -> bool:
        """
        Determines if the ongoing trajectory successfully halts upon the maximum ordered requirement.

        Args:
            board: The centralized matrix determining milestone magnitudes.
            path: The compiled chronology indicating ongoing tracking vectors.

        Returns:
            True if the terminal index natively overlays the absolute maximum required localized target.

        Implementation Details:
            Safely denies null parameters, computationally extracts peak coordinate magnitudes across 
            underlying internal sets via functional programming structures, and rigidly binds the matching 
            property parameters securely against final chronological arrays natively.
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