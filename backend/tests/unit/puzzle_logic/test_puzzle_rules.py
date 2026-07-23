import pytest

from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.game_state import GameState
from backend.puzzle_logic.puzzle_rules import PuzzleRules


@pytest.fixture
def rules():
    """Provides a fresh PuzzleRules instance for each test."""
    return PuzzleRules()


@pytest.fixture
def board():
    """Provides a fresh supported 6x6 board for each test."""
    return Board(6)


@pytest.fixture
def start_position():
    """Provides a default start position."""
    return Position(0, 0)


@pytest.fixture
def game_state(start_position):
    """Provides a fresh GameState starting at (0, 0)."""
    return GameState(start_position)


def create_snake_path(size: int = 6):
    """
    Creates a complete snake-like path through a square board.

    Example for 6x6:
    Row 0: left to right
    Row 1: right to left
    Row 2: left to right
    ...
    """
    path = []

    for y in range(size):
        if y % 2 == 0:
            for x in range(size):
                path.append(Position(x, y))
        else:
            for x in reversed(range(size)):
                path.append(Position(x, y))

    return path


# ==========================================
# Valid Move Checks
# ==========================================

def test_valid_move_to_empty_adjacent_cell(board, game_state, rules):
    """Test that moving to an adjacent, unvisited, empty cell is valid."""
    target = Position(1, 0)

    assert rules.isValidMove(board, game_state, target)


def test_invalid_move_outside_board(board, game_state, rules):
    """Test that moving outside the board is invalid."""
    target = Position(-1, 0)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_not_adjacent(board, game_state, rules):
    """Test that moving to a non-adjacent cell is invalid."""
    target = Position(2, 0)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_through_wall(board, game_state, rules):
    """Test that moving through a wall is invalid."""
    target = Position(1, 0)

    board.addWall(Position(0, 0), target)

    assert not rules.isValidMove(board, game_state, target)


def test_invalid_move_to_visited_cell(board, game_state, rules):
    """Test that moving to an already visited cell is invalid."""
    first_step = Position(1, 0)
    game_state.addStep(first_step)

    target = Position(0, 0)

    assert not rules.isValidMove(board, game_state, target)


# ==========================================
# Waypoint Order Checks
# ==========================================

def test_valid_move_to_next_waypoint(board, game_state, rules):
    """Test that moving to the next expected non-final waypoint is valid."""
    start = Position(0, 0)
    target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(target, 2)
    board.addWaypoint(final_waypoint, 3)

    assert rules.isValidMove(board, game_state, target)


def test_invalid_move_to_wrong_waypoint_order(board, game_state, rules):
    """
    Test that entering waypoint 3 before waypoint 2 is invalid.

    Waypoint 3 is deliberately not the final waypoint, ensuring that
    this test checks waypoint order rather than the endpoint rule.
    """
    start = Position(0, 0)
    expected_waypoint = Position(0, 1)
    wrong_target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(expected_waypoint, 2)
    board.addWaypoint(wrong_target, 3)
    board.addWaypoint(final_waypoint, 4)

    assert not rules.isValidMove(board, game_state, wrong_target)


def test_valid_move_to_waypoint_after_increment(board, game_state, rules):
    """
    Test that a later non-final waypoint becomes valid after
    incrementing nextWaypointOrder.
    """
    start = Position(0, 0)
    previous_waypoint = Position(2, 0)
    target = Position(1, 0)
    final_waypoint = Position(5, 5)

    board.addWaypoint(start, 1)
    board.addWaypoint(previous_waypoint, 2)
    board.addWaypoint(target, 3)
    board.addWaypoint(final_waypoint, 4)

    game_state.incrementNextWaypointOrder()

    assert rules.isValidMove(board, game_state, target)


# ==========================================
# Endpoint Rule Checks
# ==========================================

def test_invalid_move_to_final_waypoint_too_early(
    board,
    game_state,
    rules,
):
    """Test that the final waypoint cannot be entered too early."""
    start = Position(0, 0)
    final_waypoint = Position(1, 0)

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    assert not rules.isValidMove(
        board,
        game_state,
        final_waypoint,
    )


def test_invalid_move_away_from_final_waypoint(board, rules):
    """Test that moving away from the final waypoint is invalid."""
    start = Position(5, 5)
    final_waypoint = Position(0, 0)
    target = Position(1, 0)

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    state = GameState(final_waypoint)

    assert not rules.isValidMove(board, state, target)


def test_valid_move_to_final_waypoint_as_last_cell(board, rules):
    """Test that the final waypoint is valid if it completes the board."""
    path = create_snake_path(6)

    start = path[0]
    final_waypoint = path[-1]

    board.addWaypoint(start, 1)
    board.addWaypoint(final_waypoint, 2)

    state = GameState(start)

    for position in path[1:-1]:
        state.addStep(position)

    assert state.getCurrentPosition == path[-2]
    assert rules.isValidMove(board, state, final_waypoint)


def test_invalid_move_when_current_waypoint_is_only_waypoint(board, rules):
    """
    Test that a single waypoint is both the first and final waypoint.

    Moving away from it therefore violates the endpoint rule.
    """
    start_and_final = Position(0, 0)
    target = Position(1, 0)

    board.addWaypoint(start_and_final, 1)

    state = GameState(start_and_final)

    assert not rules.isValidMove(board, state, target)


# ==========================================
# Complete Solution Checks
# ==========================================

def test_complete_solution_valid_snake_path(board, rules):
    """Test that a full valid snake path is accepted."""
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert rules.isCompleteSolution(board, path)


def test_complete_solution_without_waypoints_is_invalid(board, rules):
    """Test that a board without waypoints has no valid complete solution."""
    path = create_snake_path(6)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_missing_cell(board, rules):
    """Test that a path missing one cell is not a complete solution."""
    path = create_snake_path(6)
    incomplete_path = path[:-1]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, incomplete_path)


def test_complete_solution_duplicate_cell_edge_case(board, rules):
    """Test that a path containing a duplicate cell is invalid."""
    path = create_snake_path(6)

    # Duplicate an internal cell while keeping the start and endpoint unchanged.
    path[10] = path[9]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_with_wall_between_path_cells(board, rules):
    """Test that a wall blocking the path makes the solution invalid."""
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    board.addWall(Position(0, 0), Position(1, 0))

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_wrong_waypoint_order(board, rules):
    """Test that visiting waypoints in the wrong order is invalid."""
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(0, 5), 2)
    board.addWaypoint(Position(5, 0), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_empty_path(board, rules):
    """Test that an empty path is not a complete solution."""
    assert not rules.isCompleteSolution(board, [])


def test_complete_solution_with_out_of_bounds_position(board, rules):
    """Test that an out-of-bounds position makes the path invalid."""
    path = create_snake_path(6)
    path[10] = Position(99, 99)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_with_non_adjacent_jump(board, rules):
    """
    Test that a path containing a non-adjacent jump is invalid.

    Swapping two positions preserves the set of covered cells while
    introducing an invalid movement.
    """
    path = create_snake_path(6)

    path[1], path[2] = path[2], path[1]

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_must_start_at_first_waypoint(board, rules):
    """Test that the path must start at waypoint 1."""
    path = create_snake_path(6)

    board.addWaypoint(Position(1, 0), 1)
    board.addWaypoint(Position(0, 5), 2)

    assert not rules.isCompleteSolution(board, path)


def test_complete_solution_must_end_at_last_waypoint(board, rules):
    """Test that the path must end at the highest waypoint."""
    path = create_snake_path(6)

    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)

    assert not rules.isCompleteSolution(board, path)