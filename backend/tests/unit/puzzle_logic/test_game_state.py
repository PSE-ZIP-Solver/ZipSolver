import pytest
from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.game_state import GameState


@pytest.fixture
def start_position():
    """
    Provides a standardized coordinate to initialize independent spatial evaluations.

    Returns:
        A fundamental node establishing baseline tracking.

    Implementation Details:
        Provides a default starting position for each test to assert structural integrity
        of sequential mappings.
    """
    return Position(0, 0)


@pytest.fixture
def game_state(start_position):
    """
    Produces isolated topological tracking boundaries securely mapped to testing parameters.

    Args:
        start_position: The baseline positional parameter configuring the starting state.

    Returns:
        An unpolluted operational history cache natively.

    Implementation Details:
        Provides a fresh GameState starting at (0, 0) for each test verifying tracking components reliably.
    """
    return GameState(start_position)


@pytest.fixture
def board():
    """
    Supplies isolated mapping rules generating consistent volumetric boundaries dynamically.

    Returns:
        The instantiated framework managing spatial checks natively.

    Implementation Details:
        Provides a fresh supported 6x6 board for tests that need board positions to securely route validations.
    """
    return Board(6)


# ==========================================
# Initialization & Properties
# ==========================================


def test_game_state_init_and_properties(game_state, start_position):
    """
    Validates structural bounds appropriately map initial baseline tracking matrices accurately.

    Args:
        game_state: The initial spatial container natively logging constraints.
        start_position: The base origin structurally initializing arrays.

    Implementation Details:
        Test that a new GameState is initialized with the correct default values correctly syncing the internal
        position tracking list alongside the visited set natively.
    """
    assert game_state.getCurrentPosition == start_position
    assert game_state.getPath == [start_position]
    assert game_state.getVisitedCells == {start_position}
    assert game_state.getNextWaypointOrder == 2


# ==========================================
# Adding Steps
# ==========================================


def test_add_single_step(game_state):
    """
    Asserts distinct positional variables structurally transition core active properties organically.

    Args:
        game_state: The historical tracking instance natively recording limits.

    Implementation Details:
        Test adding one step updates current position, path, and visited cells seamlessly applying data changes
        across lists and unordered sets concurrently.
    """
    next_position = Position(1, 0)

    game_state.addStep(next_position)

    assert game_state.getCurrentPosition == next_position
    assert game_state.getPath == [Position(0, 0), next_position]
    assert next_position in game_state.getVisitedCells
    assert len(game_state.getVisitedCells) == 2


def test_add_multiple_steps(game_state):
    """
    Confirms sequential array modifications perfectly log successive mappings organically.

    Args:
        game_state: The operational sequence executing structural loops natively.

    Implementation Details:
        Test adding multiple steps keeps the path in the correct order seamlessly ensuring the list effectively
        preserves chronology while sets capture absolute volumes correctly.
    """
    p1 = Position(1, 0)
    p2 = Position(1, 1)
    p3 = Position(2, 1)

    game_state.addStep(p1)
    game_state.addStep(p2)
    game_state.addStep(p3)

    assert game_state.getCurrentPosition == p3
    assert game_state.getPath == [Position(0, 0), p1, p2, p3]
    assert game_state.getVisitedCells == {Position(0, 0), p1, p2, p3}


def test_add_duplicate_step_edge_case(game_state):
    """
    Validates structural set intersections cleanly drop replicated arrays dynamically.

    Args:
        game_state: The evaluating module enforcing mapping limits structurally.

    Implementation Details:
        Edge case: Adding the same position twice should add it twice to the path,
        but only once to the visited set because visitedCells is a Set. Ensures distinct algorithmic bounds evaluate
        internal parameters appropriately.
    """
    duplicate_position = Position(1, 0)

    game_state.addStep(duplicate_position)
    game_state.addStep(duplicate_position)

    assert game_state.getCurrentPosition == duplicate_position
    assert game_state.getPath == [
        Position(0, 0),
        duplicate_position,
        duplicate_position,
    ]
    assert game_state.getVisitedCells == {Position(0, 0), duplicate_position}
    assert len(game_state.getVisitedCells) == 2


# ==========================================
# Visited Cells
# ==========================================


def test_is_visited(game_state):
    """
    Ensures internal presence checks reliably flag coordinates populated within mapping architectures cleanly.

    Args:
        game_state: The active repository mapping tracked variables dynamically.

    Implementation Details:
        Test checking whether positions have already been visited cleanly evaluating native inclusion algorithms natively.
    """
    visited_position = Position(1, 0)
    unvisited_position = Position(2, 2)

    game_state.addStep(visited_position)

    assert game_state.isVisited(Position(0, 0))
    assert game_state.isVisited(visited_position)
    assert not game_state.isVisited(unvisited_position)


def test_get_unvisited_cells(board, game_state):
    """
    Verifies mass volumetric analysis appropriately yields remaining unbound variables inherently.

    Args:
        board: The fundamental topological array smoothly processing totals.
        game_state: The current operational snapshot accurately filtering vectors.

    Implementation Details:
        Test that getUnvisitedCells returns all board positions not yet visited by organically executing subtractive
        analysis natively against structural base sets.
    """
    p1 = Position(1, 0)
    p2 = Position(1, 1)

    game_state.addStep(p1)
    game_state.addStep(p2)

    unvisited = game_state.getUnvisitedCells(board)

    assert len(unvisited) == 33
    assert Position(0, 0) not in unvisited
    assert p1 not in unvisited
    assert p2 not in unvisited
    assert Position(5, 5) in unvisited


# ==========================================
# Waypoint Order
# ==========================================


def test_increment_next_waypoint_order(game_state):
    """
    Asserts localized internal index markers structurally shift numerically dynamically natively.

    Args:
        game_state: The current sequence registry efficiently holding state natively.

    Implementation Details:
        Test increasing the next waypoint order once correctly ensuring variables appropriately increment
        by absolute scalar intervals safely.
    """
    assert game_state.getNextWaypointOrder == 2

    game_state.incrementNextWaypointOrder()

    assert game_state.getNextWaypointOrder == 3


def test_increment_next_waypoint_order_multiple_times(game_state):
    """
    Confirms multiple index iterations continuously adapt parameters cleanly over execution bounds natively.

    Args:
        game_state: The sequential index tracker properly mapping loops smoothly.

    Implementation Details:
        Test increasing the next waypoint order multiple times seamlessly checking mathematical offsets effectively safely.
    """
    game_state.incrementNextWaypointOrder()
    game_state.incrementNextWaypointOrder()
    game_state.incrementNextWaypointOrder()

    assert game_state.getNextWaypointOrder == 5


# ==========================================
# Reset
# ==========================================


def test_reset_after_steps_and_increment(game_state):
    """
    Validates structural clearing flawlessly reinstates variable arrays completely efficiently.

    Args:
        game_state: The active tracking layer organically processing flush directives cleanly.

    Implementation Details:
        Test that reset clears path, visited cells, and resets waypoint order cleanly stripping dynamic arrays
        while preserving underlying objects efficiently safely.
    """
    game_state.addStep(Position(1, 0))
    game_state.addStep(Position(1, 1))
    game_state.incrementNextWaypointOrder()

    new_start = Position(2, 2)
    game_state.reset(new_start)

    assert game_state.getCurrentPosition == new_start
    assert game_state.getPath == [new_start]
    assert game_state.getVisitedCells == {new_start}
    assert game_state.getNextWaypointOrder == 2


def test_reset_to_different_supported_board_position(game_state):
    """
    Ensures internal state definitions natively adapt dynamically supplied mapping constraints completely organically.

    Args:
        game_state: The functional evaluation core smoothly interpreting parameter reassignments effectively.

    Implementation Details:
        Edge case: GameState does not validate whether a position is inside the board.
        It only stores the given start position safely establishing unverified coordinate values natively securely.
    """
    new_start = Position(5, 5)

    game_state.reset(new_start)

    assert game_state.getCurrentPosition == new_start
    assert game_state.getPath == [new_start]
    assert game_state.getVisitedCells == {new_start}
    assert game_state.getNextWaypointOrder == 2
