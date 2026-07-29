import sys
import pytest
from unittest import mock
import numpy as np

# DO NOT import gymnasium globally
# DO NOT import rl_environment globally
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position


def get_protected_or_prop(obj, protected_name, prop_name):
    """Helper: Strict Encapsulation check to safely access protected fields/props for assertions."""
    if hasattr(obj, protected_name): val = getattr(obj, protected_name)
    else: val = getattr(obj, prop_name)
    return val() if callable(val) else val


@pytest.fixture(autouse=True)
def mock_ml_dependencies():
    """ 
    Safely mock heavy ML dependency 'gymnasium' directly inside sys.modules. 
    Prevents CI/CD Pytest Collection crashes (ModuleNotFoundError).
    """
    mock_gym = mock.MagicMock()

    class MockEnv:
        def __init__(self, *args, **kwargs): pass
        def reset(self, seed=None): pass

    class MockDiscrete:
        def __init__(self, n): self.n = n

    class MockBox:
        def __init__(self, low, high, shape, dtype):
            self.low = np.full(shape, low, dtype=dtype)
            self.high = np.full(shape, high, dtype=dtype)
            self.shape = shape
            self.dtype = dtype

    mock_gym.Env = MockEnv
    mock_gym.spaces.Discrete = MockDiscrete
    mock_gym.spaces.Box = MockBox

    with mock.patch.dict(sys.modules, {'gymnasium': mock_gym}):
        yield mock_gym


@pytest.fixture
def real_board():
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(5, 5), 2)
    return board


@pytest.fixture
def env(real_board):
    # LAZY LOAD Target environment logic AFTER mock_ml_dependencies has intercepted imports
    from backend.rl_components.rl_environment import RLEnvironment
    return RLEnvironment(real_board)


def find_valid_action(environment):
    state = get_protected_or_prop(environment.game, "_state", "getState")
    current = get_protected_or_prop(state, "_current_position", "getCurrentPosition")

    for action in range(environment.action_space.n):
        try:
            target = environment._get_target_position(current, action)
        except ValueError:
            continue

        is_valid = get_protected_or_prop(environment.game, "_isValidNextStep", "isValidNextStep")
        valid = is_valid(target) if callable(is_valid) else is_valid
        if valid:
            return action, target

    raise AssertionError("No valid action exists for the current test board.")


# ==========================================
# Core & Assertion Tests
# ==========================================

def test_initialization(env, mock_ml_dependencies):
    assert isinstance(env.action_space, mock_ml_dependencies.spaces.Discrete)
    assert env.action_space.n == 4
    assert isinstance(env.observation_space, mock_ml_dependencies.spaces.Box)


def test_reset(env):
    observation, info = env.reset(seed=42)
    assert observation.shape == (7, 6, 6)
    
    state = get_protected_or_prop(env.game, "_state", "getState")
    current = get_protected_or_prop(state, "_current_position", "getCurrentPosition")
    path = get_protected_or_prop(state, "_path", "getPath")
    
    assert current == Position(0, 0)
    assert path == [Position(0, 0)]


# ==========================================
# REQUIRED Edge Cases & Error Handling
# ==========================================

def test_init_fails_on_none_board():
    from backend.rl_components.rl_environment import RLEnvironment
    with pytest.raises(ValueError, match="Board cannot be None"):
        RLEnvironment(None)


def test_init_fails_on_empty_board():
    from backend.rl_components.rl_environment import RLEnvironment
    board = Board(0)
    with pytest.raises(ValueError, match="Board size must be greater than 0"):
        RLEnvironment(board)


def test_step_exception_handling(env, monkeypatch):
    """Simulate a crash during game step to ensure environment handles exceptions safely."""
    env.reset()
    def mock_step(*args, **kwargs):
        raise RuntimeError("Simulated internal crash")
        
    monkeypatch.setattr(env.game, "step", mock_step)
    
    valid_action, _ = find_valid_action(env)
    obs, reward, term, trunc, info = env.step(valid_action)
    
    assert term is True
    assert info.get("invalid_move") is True
    assert "Simulated internal crash" in info.get("error", "")
    assert reward == env.config.invalid_move_penalty


def test_isolated_disconnected_cells():
    """Test mathematically impossible routing gracefully terminates upon hitting a wall."""
    from backend.rl_components.rl_environment import RLEnvironment
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWall(Position(0, 0), Position(1, 0))
    board.addWall(Position(0, 0), Position(0, 1))

    env = RLEnvironment(board)
    env.reset()
    
    # Force agent RIGHT directly into the barricade
    obs, reward, term, trunc, info = env.step(1)
    
    assert term is True
    assert info.get("invalid_move") is True
    assert reward == env.config.invalid_move_penalty


# ==========================================
# TDD Route Confirmations
# ==========================================

def test_step_invalid_move(env):
    env.reset()
    # Move OUT OF BOUNDS upwards
    observation, reward, terminated, truncated, info = env.step(0)
    assert reward == env.config.invalid_move_penalty
    assert terminated is True
    assert info.get("invalid_move") is True


def test_step_valid_move_new_cell(env):
    env.reset()
    valid_action, target = find_valid_action(env)
    observation, reward, terminated, truncated, info = env.step(valid_action)
    
    assert reward == env.config.new_cell_reward
    state = get_protected_or_prop(env.game, "_state", "getState")
    assert get_protected_or_prop(state, "_current_position", "getCurrentPosition") == target


def test_step_valid_move_waypoint():
    from backend.rl_components.rl_environment import RLEnvironment
    board = Board(6)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 0), 2)
    board.addWaypoint(Position(5, 5), 3)

    environment = RLEnvironment(board)
    environment.reset()
    observation, reward, terminated, truncated, info = environment.step(1)
    
    assert reward == environment.config.next_waypoint_reward
    assert terminated is False