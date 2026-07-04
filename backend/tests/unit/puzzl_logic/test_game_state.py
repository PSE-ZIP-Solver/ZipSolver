import pytest
from puzzle_logic.data_models import Position
from puzzle_logic.board import Board
from puzzle_logic.game_state import GameState


@pytest.fixture
def start_position():
    """Provides a default starting position for each test."""
    return Position(0, 0)


@pytest.fixture
def game_state(start_position):
    """Provides a fresh GameState starting at (0, 0) for each test."""
    return GameState(start_position)


@pytest.fixture
def board():
    """Provides a fresh supported 6x6 board for tests that need board positions."""
    return Board(6)


# ==========================================
# Initialization & Properties
# ==========================================

def test_game_state_init_and_properties(game_state, start_position):
    """Test that a new GameState is initialized with the correct default values."""
    assert game_state.getCurrentPosition == start_position
    assert game_state.getPath == [start_position]
    assert game_state.getVisitedCells == {start_position}
    assert game_state.getNextWaypointOrder == 2


# ==========================================
# Adding Steps
# ==========================================

def test_add_single_step(game_state):
    """Test adding one step updates current position, path, and visited cells."""
    next_position = Position(1, 0)

    game_state.addStep(next_position)

    assert game_state.getCurrentPosition == next_position
    assert game_state.getPath == [Position(0, 0), next_position]
    assert next_position in game_state.getVisitedCells
    assert len(game_state.getVisitedCells) == 2


def test_add_multiple_steps(game_state):
    """Test adding multiple steps keeps the path in the correct order."""
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
    Edge case: Adding the same position twice should add it twice to the path,
    but only once to the visited set because visitedCells is a Set.
    """
    duplicate_position = Position(1, 0)

    game_state.addStep(duplicate_position)
    game_state.addStep(duplicate_position)

    assert game_state.getCurrentPosition == duplicate_position
    assert game_state.getPath == [Position(0, 0), duplicate_position, duplicate_position]
    assert game_state.getVisitedCells == {Position(0, 0), duplicate_position}
    assert len(game_state.getVisitedCells) == 2


# ==========================================
# Visited Cells
# ==========================================

def test_is_visited(game_state):
    """Test checking whether positions have already been visited."""
    visited_position = Position(1, 0)
    unvisited_position = Position(2, 2)

    game_state.addStep(visited_position)

    assert game_state.isVisited(Position(0, 0))
    assert game_state.isVisited(visited_position)
    assert not game_state.isVisited(unvisited_position)


def test_get_unvisited_cells(board, game_state):
    """Test that getUnvisitedCells returns all board positions not yet visited."""
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
    """Test increasing the next waypoint order once."""
    assert game_state.getNextWaypointOrder == 2

    game_state.incrementNextWaypointOrder()

    assert game_state.getNextWaypointOrder == 3


def test_increment_next_waypoint_order_multiple_times(game_state):
    """Test increasing the next waypoint order multiple times."""
    game_state.incrementNextWaypointOrder()
    game_state.incrementNextWaypointOrder()
    game_state.incrementNextWaypointOrder()

    assert game_state.getNextWaypointOrder == 5


# ==========================================
# Reset
# ==========================================

def test_reset_after_steps_and_increment(game_state):
    """Test that reset clears path, visited cells, and resets waypoint order."""
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
    Edge case: GameState does not validate whether a position is inside the board.
    It only stores the given start position.
    """
    new_start = Position(5, 5)

    game_state.reset(new_start)

    assert game_state.getCurrentPosition == new_start
    assert game_state.getPath == [new_start]
    assert game_state.getVisitedCells == {new_start}
    assert game_state.getNextWaypointOrder == 2