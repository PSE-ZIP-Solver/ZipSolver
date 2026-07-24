import gymnasium as gym
import numpy as np
import pytest

from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position
from backend.rl_components.RLEnvironment import RLEnvironment


BOARD_SIZE = 6
OBSERVATION_CHANNELS = 8
OBSERVATION_SHAPE = (
    OBSERVATION_CHANNELS,
    BOARD_SIZE,
    BOARD_SIZE,
)


# ==========================================
# Setup & Fixtures
# ==========================================

@pytest.fixture
def real_board():
    """
    Provide a real 6x6 board.

    Waypoint 1 is the starting waypoint.
    Waypoint 2 is the final waypoint and is placed far away so that
    ordinary adjacent moves from the start remain valid.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 5), 2)

    return board


@pytest.fixture
def env(real_board):
    """Create an RLEnvironment using real puzzle-logic objects."""
    return RLEnvironment(real_board)


def find_valid_action(environment: RLEnvironment):
    """
    Find a move that is valid according to the complete puzzle logic.

    Returns:
        tuple[int, Position]: Action and corresponding target position.
    """
    current = environment.game.getState.getCurrentPosition

    for action in range(environment.action_space.n):
        target = environment._get_target_position(current, action)

        if environment.game.isValidNextStep(target):
            return action, target

    raise AssertionError("No valid action exists for the current test board.")


# ==========================================
# Gym API Contract & Spaces Tests
# ==========================================

def test_initialization(env):
    """Test that the action and observation spaces match the Gym API."""
    assert isinstance(env.action_space, gym.spaces.Discrete)
    assert env.action_space.n == 4

    assert isinstance(env.observation_space, gym.spaces.Box)
    assert env.observation_space.shape == OBSERVATION_SHAPE
    assert env.observation_space.dtype == np.float32
    assert env.observation_space.low.min() == 0.0
    assert env.observation_space.high.max() == 1.0

    assert env.config.size == BOARD_SIZE


def test_reset(env):
    """Test that reset returns a valid observation and info dictionary."""
    observation, info = env.reset(seed=42)

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32
    assert isinstance(info, dict)
    assert np.all((observation >= 0.0) & (observation <= 1.0))

    assert env.current_step_count == 0
    assert env.game.getState.getCurrentPosition == Position(0, 0)
    assert env.game.getState.getPath == [Position(0, 0)]

    # Channel 7 contains the next expected waypoint.
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


# ==========================================
# Action & Target Logic
# ==========================================

@pytest.mark.parametrize(
    "action, offset_x, offset_y",
    [
        (0, 0, -1),  # UP
        (1, 1, 0),   # RIGHT
        (2, 0, 1),   # DOWN
        (3, -1, 0),  # LEFT
    ],
)
def test_get_target_position(env, action, offset_x, offset_y):
    """Test mapping from an action to its target position."""
    current = Position(2, 2)

    target = env._get_target_position(current, action)

    assert target.getX == current.getX + offset_x
    assert target.getY == current.getY + offset_y


def test_invalid_action_mapping_edge_case(env):
    """Test that unsupported action numbers raise an exception."""
    current = Position(2, 2)

    with pytest.raises(ValueError, match="Invalid action: 99"):
        env._get_target_position(current, 99)


# ==========================================
# Step Logic, Terminations & Rewards
# ==========================================

def test_step_invalid_move(env):
    """Test the penalty and termination caused by an invalid move."""
    env.reset()

    # The game starts at (0, 0), so moving UP leaves the board.
    observation, reward, terminated, truncated, info = env.step(0)

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == env.config.invalid_move_penalty
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is True
    assert info.get("step_count") == 1

    # An invalid move must not modify the game state.
    assert env.game.getState.getCurrentPosition == Position(0, 0)
    assert env.game.getState.getPath == [Position(0, 0)]


def test_step_valid_move_new_cell(env):
    """Test the normal reward for entering a new empty cell."""
    env.reset()

    valid_action, target = find_valid_action(env)

    # The selected adjacent cell must be empty, not a waypoint.
    assert env.game.getBoard.getWaypointAt(target) is None

    observation, reward, terminated, truncated, info = env.step(valid_action)

    expected_reward = (
        env.config.step_penalty
        + env.config.new_cell_reward
    )

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is False
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert env.game.getState.getCurrentPosition == target
    assert target in env.game.getState.getVisitedCells


def test_step_valid_move_waypoint():
    """
    Test the reward for reaching the next expected non-final waypoint.

    Waypoint 3 is included so that waypoint 2 is not interpreted as
    the final waypoint by the endpoint rule.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    environment = RLEnvironment(board)
    environment.reset()

    # RIGHT: (0, 0) -> (1, 0), which contains waypoint 2.
    observation, reward, terminated, truncated, info = environment.step(1)

    expected_reward = (
        environment.config.step_penalty
        + environment.config.next_waypoint_reward
    )

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is False
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert environment.game.getState.getCurrentPosition == Position(1, 0)
    assert environment.game.getState.getNextWaypointOrder == 3

    # Waypoint 3 must now be marked as the next expected waypoint.
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


def test_step_final_waypoint_too_early_is_invalid():
    """
    Test the endpoint rule.

    The final waypoint cannot be entered before all board cells
    have been covered.
    """
    board = Board(BOARD_SIZE)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)

    environment = RLEnvironment(board)
    environment.reset()

    # RIGHT would enter the final waypoint immediately.
    observation, reward, terminated, truncated, info = environment.step(1)

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == environment.config.invalid_move_penalty
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is True
    assert info.get("step_count") == 1

    assert environment.game.getState.getCurrentPosition == Position(0, 0)
    assert environment.game.getState.getNextWaypointOrder == 2


def test_step_valid_move_finished(env, monkeypatch):
    """
    Test the completion reward and termination flag.

    Only the completion check is replaced because manually following
    a complete 36-cell path is outside the purpose of this unit test.
    """
    env.reset()

    valid_action, target = find_valid_action(env)

    monkeypatch.setattr(env.game, "isFinished", lambda: True)

    observation, reward, terminated, truncated, info = env.step(valid_action)

    expected_reward = (
        env.config.step_penalty
        + env.config.completion_reward
    )

    assert observation.shape == OBSERVATION_SHAPE
    assert reward == expected_reward
    assert terminated is True
    assert truncated is False

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is True

    assert env.game.getState.getCurrentPosition == target


def test_step_truncation_edge_case(env):
    """Test that reaching the configured step limit sets truncated."""
    env.reset()

    valid_action, target = find_valid_action(env)

    # The first valid move reaches the configured limit.
    env.config.max_steps = 1

    observation, reward, terminated, truncated, info = env.step(valid_action)

    assert observation.shape == OBSERVATION_SHAPE
    assert terminated is False
    assert truncated is True

    assert info.get("invalid_move") is False
    assert info.get("step_count") == 1
    assert info.get("is_finished") is False

    assert env.game.getState.getCurrentPosition == target


# ==========================================
# Observation Tensor Compilation
# ==========================================

def test_get_observation_zero_waypoints_edge_case(env):
    """Test that a board without waypoints does not cause division by zero."""
    env.reset()

    env.game.getBoard._waypoints.clear()

    observation = env._get_observation()

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32

    # Channel 2 contains normalized waypoint orders.
    assert np.all(observation[2] == 0.0)

    # Channel 7 contains the next expected waypoint.
    assert np.all(observation[7] == 0.0)


def test_get_observation_channels(env):
    """Test that all eight observation channels represent the board state."""
    env.reset()

    board = env.game.getBoard
    state = env.game.getState

    current = state.getCurrentPosition
    x = current.getX
    y = current.getY

    # Surround the current position with walls wherever the neighboring
    # cell lies inside the board.
    if y > 0:
        board.addWall(current, Position(x, y - 1))

    if x < board.getSize - 1:
        board.addWall(current, Position(x + 1, y))

    if y < board.getSize - 1:
        board.addWall(current, Position(x, y + 1))

    if x > 0:
        board.addWall(current, Position(x - 1, y))

    observation = env._get_observation()

    assert observation.shape == OBSERVATION_SHAPE
    assert observation.dtype == np.float32

    # Channel 0: current position
    assert observation[0, x, y] == 1.0
    assert np.sum(observation[0]) == 1.0

    # Channel 1: visited cells
    assert observation[1, x, y] == 1.0
    assert np.sum(observation[1]) == 1.0

    # Channel 2: waypoint values normalized by waypoint order
    assert observation[2, 0, 0] == pytest.approx(0.5)
    assert observation[2, 5, 5] == pytest.approx(1.0)

    # Channel 3: wall or boundary above
    assert observation[3, x, y] == 1.0

    # Channel 4: wall or boundary to the right
    assert observation[4, x, y] == 1.0

    # Channel 5: wall or boundary below
    assert observation[5, x, y] == 1.0

    # Channel 6: wall or boundary to the left
    assert observation[6, x, y] == 1.0

    # Channel 7: next expected waypoint
    assert observation[7, 5, 5] == 1.0
    assert np.sum(observation[7]) == 1.0


def test_observation_is_contained_in_observation_space(env):
    """Test that the generated observation satisfies the declared Gym space."""
    observation, _ = env.reset()

    assert env.observation_space.contains(observation)


# ==========================================
# Rendering Tests
# ==========================================

def test_render_ansi_mode(env):
    """Test rendering the environment as a string."""
    env.reset()

    output = env.render(mode="ansi")

    assert isinstance(output, str)
    assert "@" in output


def test_render_human_mode(env, capsys):
    """Test rendering the environment to standard output."""
    env.reset()

    result = env.render(mode="human")

    assert result is None

    captured = capsys.readouterr()
    assert "@" in captured.out


def test_render_invalid_mode(env):
    """Test that unsupported render modes raise an exception."""
    env.reset()

    with pytest.raises(ValueError, match="Unsupported render mode"):
        env.render(mode="unsupported_mode")