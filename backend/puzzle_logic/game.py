from .board import Board
from .game_state import GameState
from .puzzle_rules import PuzzleRules
from .data_models import Position

class Game:
    """
    Manages the game session, coordinating the board, rules, and player progress.

    Responsibility:
        Acts as the main interface for playing a puzzle. It handles starting a game, 
        checking whether moves are valid, applying moves to advance the game state, 
        and determining when the puzzle is solved.

    Implementation Details:
        Brings together a Board, GameState, and PuzzleRules instance. Initializes the game 
        at waypoint 1, validates each step using the rules engine before updating the state, 
        and advances waypoint progress as milestones are reached.
    """

    def __init__(self, board: Board):
        """
        Starts a new game on the provided board.

        Args:
            board: The board layout to play on.

        Raises:
            ValueError: If the board does not contain a starting waypoint (order 1).

        Implementation Details:
            Stores the board, creates a PuzzleRules instance, locates waypoint 1, 
            and initializes GameState at that starting position.
        """
        self._board = board
        self._rules = PuzzleRules()

        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None:
            raise ValueError("Board has no starting Waypoint with order 1.")

        self._state = GameState(startWaypoint.getPosition)

    def isValidNextStep(self, target: Position) -> bool:
        """
        Checks whether moving to the target position is allowed.

        Args:
            target: The position to check.

        Returns:
            True if the move is valid according to puzzle rules; False otherwise.

        Implementation Details:
            Delegates the check to the PuzzleRules engine using the current board and game state.
        """
        return self._rules.isValidMove(self._board, self._state, target)
    

    def step(self, target: Position) -> bool:
        """
        Attempts to move to the target position.

        Args:
            target: The destination position to move to.

        Returns:
            True if the move was valid and applied; False if the move was rejected.

        Implementation Details:
            Follows a four-step sequence:
            1. Validates the candidate move using isValidNextStep.
            2. If valid, appends the position to GameState via addStep.
            3. Checks if the target cell contains the next expected waypoint, and if so,
               advances the waypoint counter via incrementNextWaypointOrder.
            4. Returns True if the move was accepted, or False if rejected.
        """

        if not self.isValidNextStep(target):
            return  False
        
        self._state.addStep(target)

        # if new cell contains next waypoint -> update game state
        waypoint = self._board.getWaypointAt(target)
        if waypoint is not None and waypoint.getOrder == self._state.getNextWaypointOrder:
            self._state.incrementNextWaypointOrder()

        return True
    
    def isFinished(self) -> bool:
        """
        Checks whether the puzzle has been solved.

        Returns:
            True if the current path forms a complete and valid solution; False otherwise.

        Implementation Details:
            Delegates to PuzzleRules.isCompleteSolution passing the board and the recorded 
            path from GameState.
        """
        return self._rules.isCompleteSolution(self._board, self._state.getPath)
    
    def reset(self):
        """
        Resets the game back to the starting position.

        Raises:
            ValueError: If the board lacks a starting waypoint (order 1).

        Returns:
            None.

        Implementation Details:
            Locates waypoint 1 on the board (raising ValueError if missing) and resets 
            the GameState to that origin position.
        """
        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None: 
            raise ValueError("Board has no starting waypoint with order 1.")    

        self._state.reset(startWaypoint.getPosition)

    @property
    def getBoard(self) -> Board:
        """
        Gets the board used in this game.

        Returns:
            The board instance.

        Implementation Details:
            Exposes read-only access to the internal board instance via a property decorator.
        """
        return self._board
    
    @property
    def getRules(self) -> PuzzleRules:
        """
        Gets the rules engine used for this game.

        Returns:
            The PuzzleRules instance.

        Implementation Details:
            Exposes read-only access to the internal rules engine instance via a property decorator.
        """
        return self._rules
    
    @property
    def getState(self) -> GameState:
        """
        Gets the current game state tracking progress and path history.

        Returns:
            The GameState instance.

        Implementation Details:
            Exposes read-only access to the internal game state instance via a property decorator.
        """
        return self._state