from .board import Board
from .game_state import GameState
from .puzzle_rules import PuzzleRules
from .data_models import Position

class Game:
    """Coordinates the board, current game state, and puzzle rules."""

    def __init__(self, board: Board):
        """Create a game for the given board and start at waypoint 1."""
        self._board = board
        self._rules = PuzzleRules()

        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None:
            raise ValueError("Board has no starting Waypoint with order 1.")

        self._state = GameState(startWaypoint.getPosition)

    def isValidNextStep(self, target: Position) -> bool:
        """Return True if the target position is a valid next step."""
        return self._rules.isValidMove(self._board, self._state, target)
    

    def step(self, target: Position) -> bool:
        """Apply a move if it is valid and return whether it succeeded."""

        if not self.isValidNextStep(target):
            return  False
        
        self._state.addStep(target)

        # if new cell contains next waypoint -> update game state
        waypoint = self._board.getWaypointAt(target)
        if waypoint is not None and waypoint.getOrder == self._state.getNextWaypointOrder:
            self._state.incrementNextWaypointOrder()

        return True
    
    def isFinished(self) -> bool:
        """Return True if the current path is a complete valid solution."""
        return self._rules.isCompleteSolution(self._board, self._state.getPath)
    
    def reset(self):
        """Reset the game to the starting waypoint."""
        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None: 
            raise ValueError("Board has no starting waypoint with order 1.")    

        self._state.reset(startWaypoint.getPosition)

    @property
    def getBoard(self) -> Board:
        return self._board
    
    @property
    def getRules(self) -> PuzzleRules:
        return self._rules
    
    @property
    def getState(self) -> GameState:
        return self._state
    
        


