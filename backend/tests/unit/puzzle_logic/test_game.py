import pytest

from backend.puzzle_logic.data_models import Position
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.game import Game


@pytest.fixture
def board():
    """
    Provides a fresh supported 6x6 board.

    A separate final waypoint is required because the final waypoint
    may only be entered when the complete board has been covered.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 5), 2)
    return board


@pytest.fixture
def game(board):
    """Provides a fresh Game starting at waypoint 1."""
    return Game(board)


def create_snake_path(size: int = 6):
    """
    Creates a complete snake-like path through a square board.

    The path starts at (0, 0), visits every cell exactly once,
    and only uses horizontal or vertical moves.
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
# Initialization & Properties
# ==========================================

def test_game_init_and_properties(board, game):
    """Test that a Game is initialized with board, rules, and state."""
    assert game.getBoard == board
    assert game.getRules is not None
    assert game.getState is not None
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getNextWaypointOrder == 2


def test_game_init_without_start_waypoint_raises_error():
    """Test that Game initialization fails if no waypoint with order 1 exists."""
    board = Board(6)

    with pytest.raises(ValueError):
        Game(board)


def test_game_init_with_wrong_start_waypoint_order_raises_error():
    """Test that Game initialization fails if no waypoint with order 1 exists."""
    board = Board(6)
    board.addWaypoint(Position(0, 0), 2)

    with pytest.raises(ValueError):
        Game(board)


# ==========================================
# Valid Next Step
# ==========================================

def test_is_valid_next_step_for_adjacent_cell(game):
    """Test that an adjacent, unvisited, empty cell is a valid next step."""
    assert game.isValidNextStep(Position(1, 0))


def test_is_valid_next_step_for_non_adjacent_cell(game):
    """Test that a non-adjacent cell is not a valid next step."""
    assert not game.isValidNextStep(Position(2, 0))


def test_is_valid_next_step_for_out_of_bounds_cell(game):
    """Test that a position outside the board is not a valid next step."""
    assert not game.isValidNextStep(Position(-1, 0))


def test_is_valid_next_step_blocked_by_wall(board, game):
    """Test that a step through a wall is not valid."""
    board.addWall(Position(0, 0), Position(1, 0))

    assert not game.isValidNextStep(Position(1, 0))


def test_cannot_leave_only_waypoint():
    """
    Test the endpoint rule when waypoint 1 is also the final waypoint.

    If a board has only one waypoint, the game starts on the final waypoint
    and no move away from it is permitted.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)

    game = Game(board)

    assert not game.isValidNextStep(Position(1, 0))


# ==========================================
# Step
# ==========================================

def test_step_valid_move_updates_state(game):
    """Test that a valid step updates current position, path, and visited cells."""
    target = Position(1, 0)

    result = game.step(target)

    assert result is True
    assert game.getState.getCurrentPosition == target
    assert game.getState.getPath == [Position(0, 0), target]
    assert target in game.getState.getVisitedCells


def test_step_invalid_move_does_not_update_state(game):
    """Test that an invalid step returns False and does not change the state."""
    invalid_target = Position(2, 0)

    result = game.step(invalid_target)

    assert result is False
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}


def test_step_to_visited_cell_is_invalid(game):
    """Test that stepping back to an already visited cell is invalid."""
    assert game.step(Position(1, 0))

    result = game.step(Position(0, 0))

    assert result is False
    assert game.getState.getCurrentPosition == Position(1, 0)
    assert game.getState.getPath == [
        Position(0, 0),
        Position(1, 0),
    ]


def test_step_to_next_waypoint_increments_next_waypoint_order():
    """
    Test that reaching the next non-final waypoint increments the order.

    Waypoint 3 is added so that waypoint 2 is not the final waypoint.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is True
    assert game.getState.getNextWaypointOrder == 3


def test_step_to_wrong_waypoint_order_is_invalid():
    """
    Test that entering waypoint 3 before waypoint 2 is invalid.

    A separate final waypoint is used so the failure specifically tests
    waypoint order rather than the endpoint rule.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(0, 1), 2)
    board.addWaypoint(Position(1, 0), 3)
    board.addWaypoint(Position(5, 5), 4)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is False
    assert game.getState.getNextWaypointOrder == 2
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]


def test_step_to_final_waypoint_too_early_is_invalid():
    """Test that the final waypoint cannot be entered before the last move."""
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)

    game = Game(board)

    result = game.step(Position(1, 0))

    assert result is False
    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getNextWaypointOrder == 2


# ==========================================
# Finished State
# ==========================================

def test_is_finished_initially_false(game):
    """Test that a newly started game is not finished."""
    assert not game.isFinished()


def test_is_finished_after_complete_valid_path():
    """Test that the game is finished after following a complete solution path."""
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 0), 2)
    board.addWaypoint(Position(0, 5), 3)

    game = Game(board)
    path = create_snake_path(6)

    for position in path[1:]:
        assert game.step(position)

    assert game.isFinished()


def test_is_finished_false_after_partial_path(game):
    """Test that the game is not finished after only a partial path."""
    assert game.step(Position(1, 0))
    assert game.step(Position(2, 0))

    assert not game.isFinished()


# ==========================================
# Reset
# ==========================================

def test_reset_after_steps(game):
    """Test that reset returns the game to the starting waypoint."""
    assert game.step(Position(1, 0))
    assert game.step(Position(2, 0))

    game.reset()

    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}
    assert game.getState.getNextWaypointOrder == 2


def test_reset_after_reaching_waypoint():
    """
    Test that reset also resets the next waypoint order.

    Waypoint 2 must not be the final waypoint, otherwise entering it early
    would be prohibited by the endpoint rule.
    """
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    game = Game(board)

    assert game.step(Position(1, 0))
    assert game.getState.getNextWaypointOrder == 3

    game.reset()

    assert game.getState.getCurrentPosition == Position(0, 0)
    assert game.getState.getPath == [Position(0, 0)]
    assert game.getState.getVisitedCells == {Position(0, 0)}
    assert game.getState.getNextWaypointOrder == 2