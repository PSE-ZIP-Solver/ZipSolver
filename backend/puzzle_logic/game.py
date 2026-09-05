from .board import Board
from .game_state import GameState
from .puzzle_rules import PuzzleRules
from .data_models import Position


class Game:
    """
    Orchestrates the high-level operational lifecycle between spatial layout, rules, and game state.

    Responsibility:
        Serves as the primary behavioral facade directing internal mathematical configurations.
        It gracefully encapsulates setup logic, coordinates movement validations by piping data
        through rule engines, and cleanly mutates state without exposing underlying component intricacies.

    Implementation Details:
        Maintains persistent composition dependencies linking a static `Board` blueprint, a dynamic
        `GameState` tracker, and a stateless `PuzzleRules` validator. Instantiation enforces severe
        defensive fast-failing measures to guarantee the environment is logically playable out-of-the-box.
    """

    def __init__(self, board: Board):
        """
        Initializes a fresh localized playing session using parsed board schematics.

        Args:
            board: The foundational grid topology retaining waypoints and bounding matrices.

        Raises:
            ValueError: If the requested configuration completely lacks a foundational starting
                requirement at sequential sequence order 1.

        Implementation Details:
            Stores native layout data directly and seamlessly instantiates standalone evaluation modules.
            Actively scans internal property constraints explicitly mapping to integer 1, instantly
            invoking a fast-fail exception state upon failures to strictly preserve computational integrity
            before generating tracked states.
        """
        self._board = board
        self._rules = PuzzleRules()

        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None:
            raise ValueError("Board has no starting Waypoint with order 1.")

        self._state = GameState(startWaypoint.getPosition)

    def isValidNextStep(self, target: Position) -> bool:
        """
        Assesses via internal routing if engaging onto a localized coordinate satisfies mechanics.

        Args:
            target: The desired adjacent grid space awaiting verification checks.

        Returns:
            True if all spatial algorithms natively compute clear passages securely.

        Implementation Details:
            Delegates functional authority straight into the managed stateless rule engines, parsing in
            both local internal parameters and targeted vectors strictly to bypass local tracking scopes.
        """
        return self._rules.isValidMove(self._board, self._state, target)

    def step(self, target: Position) -> bool:
        """
        Formally attempts to transition into a new localized parameter and lock it sequentially.

        Args:
            target: The actively requested localized index pending transition locks.

        Returns:
            True if physical and algorithmic shifts were successfully integrated, False on rejection.

        Implementation Details:
            Activates immediate fast-fail checking gates routing into rules modules first. Pending
            clean clearances, initiates strict internal mutations inserting arrays into chronology matrices.
            Queries spatial boundaries mapping to upcoming sequenced demands, proactively updating parameters
            if exact overlaps form successfully.
        """

        if not self.isValidNextStep(target):
            return False

        self._state.addStep(target)

        # if new cell contains next waypoint -> update game state
        waypoint = self._board.getWaypointAt(target)
        if (
            waypoint is not None
            and waypoint.getOrder == self._state.getNextWaypointOrder
        ):
            self._state.incrementNextWaypointOrder()

        return True

    def isFinished(self) -> bool:
        """
        Polls internal matrices to determine if overarching Hamiltonian conditions are presently met.

        Returns:
            True if terminal evaluations verify entirely complete conditions smoothly.

        Implementation Details:
            Passes complete dynamic internal logs scaling dynamically through stateless functional evaluators
            to evaluate peak sequential completeness.
        """
        return self._rules.isCompleteSolution(self._board, self._state.getPath)

    def reset(self):
        """
        Wipes active progression vectors seamlessly restoring tracking environments back to zero.

        Raises:
            ValueError: If during re-evaluation parameters entirely fail identifying chronological order 1.

        Implementation Details:
            Defensively queries origin constraints scanning strictly for baseline scalar value 1. Throws
            system exceptions automatically if missing, else overrides internal memory instances mapping
            direct origins directly over historic paths mathematically.
        """
        startWaypoint = self._board.getWaypointByOrder(1)

        if startWaypoint is None:
            raise ValueError("Board has no starting waypoint with order 1.")

        self._state.reset(startWaypoint.getPosition)

    @property
    def getBoard(self) -> Board:
        """
        Retrieves the rigid baseline spatial blueprint.

        Returns:
            The configured foundational module handling physical limits and bounds.

        Implementation Details:
            Allows highly restricted superficial exposure to the structurally instantiated base via decorators.
        """
        return self._board

    @property
    def getRules(self) -> PuzzleRules:
        """
        Retrieves the stateless computational evaluator configured for restrictions.

        Returns:
            The centralized ruleset checking processor.

        Implementation Details:
            Opens encapsulated local properties referencing the internal structural logic component.
        """
        return self._rules

    @property
    def getState(self) -> GameState:
        """
        Returns the constantly evolving active memory map handling localized puzzle progress.

        Returns:
            The specific tracker object holding chronological and physical vectors.

        Implementation Details:
            Facilitates direct retrieval via property hooks of the dynamically changing tracking variable.
        """
        return self._state
