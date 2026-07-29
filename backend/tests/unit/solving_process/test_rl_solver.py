import pytest
from unittest.mock import MagicMock, patch
import sys

from backend.puzzle_logic.board import Board
from backend.solution_path import SolutionPath
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.solver_result import SolverResult
from backend.solving_process.rl_solver import RLSolver

# --- FIXTURES & ISOLATED MOCKING ---

@pytest.fixture
def mock_board():
    board = MagicMock(spec=Board)
    # Architectural Rule: Property mocking
    type(board).getSize = property(lambda self: 6)
    return board

@pytest.fixture
def mock_env():
    env = MagicMock()
    env.reset.return_value = ({"grid": [0]}, {})
    env.step.return_value = ({"grid": [1]}, 1.0, True, False, {})
    
    mock_game = MagicMock()
    type(mock_game).isFinished = property(lambda self: True)
    type(mock_game.getState).getPath = property(lambda self: ["Pos(0,0)", "Pos(0,1)"])
    env.game = mock_game
    return env

@pytest.fixture
def mock_agent():
    agent = MagicMock()
    # SB3 predict() returns a tuple of (action, states)
    agent.predict.return_value = (2, None)
    agent._model = MagicMock()
    return agent


@pytest.fixture(autouse=True)
def patch_rl_classes(mock_env, mock_agent):
    """
    Safely mocks heavy ML dependencies AND the internal RL modules that import them.
    This injects directly into sys.modules, entirely bypassing unittest.mock.patch's
    AttributeError when dealing with locally scoped/lazy imports.
    """
    mock_agent_cls = MagicMock(return_value=mock_agent)
    mock_env_cls = MagicMock(return_value=mock_env)
    
    mock_agent_mod = MagicMock()
    mock_agent_mod.RLAgent = mock_agent_cls
    
    mock_env_mod = MagicMock()
    mock_env_mod.RLEnvironment = mock_env_cls
    
    mock_mods = {
        'gymnasium': MagicMock(),
        'torch': MagicMock(),
        'stable_baselines3': MagicMock(),
        'backend.rl_components': MagicMock(),
        'backend.rl_components.RLAgent': mock_agent_mod,
        'backend.rl_components.RLEnvironment': mock_env_mod,
    }
    
    with patch.dict(sys.modules, mock_mods):
        # Yielding the classes so tests can assert against their constructors if needed
        yield mock_agent_cls, mock_env_cls


# --- TDD FAST FAIL EDGE CASES ---

def test_solve_fast_fails_on_none_board():
    solver = RLSolver("backend/agent.zip")
    result = solver.solve(None)
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None
    assert result._metrics._steps == 0
    assert "Invalid or mathematically unsolvable" in result._message

def test_solve_fast_fails_on_empty_board():
    board = MagicMock(spec=Board)
    type(board).getSize = property(lambda self: 0)
    
    solver = RLSolver("backend/agent.zip")
    result = solver.solve(board)
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert result._metrics._steps == 0


# --- BEHAVIOR TESTS ---

def test_solve_success_complete_solution(patch_rl_classes, mock_board, mock_env, mock_agent):
    # Simulate an episode taking a few steps
    mock_env.step.side_effect = [
        ({"grid": [1]}, 0.0, False, False, {}),
        ({"grid": [2]}, 0.0, False, False, {}),
        ({"grid": [3]}, 1.0, True, False, {})
    ]

    solver = RLSolver("backend/agent.zip")
    result = solver.solve(mock_board)

    # Architectural Rule: Strictly asserting against protected attributes
    assert result._status == SolverStatus.SOLVED
    assert result._metrics._steps == 3
    assert result._path is not None
    mock_env.reset.assert_called_once()


def test_load_agent_caching_avoids_reloading_weights(patch_rl_classes, mock_board, mock_env, mock_agent):
    mock_agent_cls, mock_env_cls = patch_rl_classes

    solver = RLSolver("backend/agent.zip")
    solver.solve(mock_board)
    
    # Simulate a second solve loop with a brand new environment
    second_mock_env = MagicMock()
    second_mock_env.reset.return_value = ({"grid": [0]}, {})
    second_mock_env.step.return_value = ({"grid": [1]}, 1.0, True, False, {})
    type(second_mock_env.game).isFinished = property(lambda self: True)
    type(second_mock_env.game.getState).getPath = property(lambda self: [])
    
    # RLEnvironment(...) will now return our second_mock_env
    mock_env_cls.return_value = second_mock_env

    solver.solve(mock_board)
    
    # Important validation: RLAgent was NOT loaded from disk a second time
    assert mock_agent_cls.call_count == 1 
    assert mock_agent._env == second_mock_env
    mock_agent._model.set_env.assert_called_with(second_mock_env)


# Helper class to simulate PyTorch tensors for the parametrize test cleanly
class MockTensor:
    def item(self):
        return 3

@pytest.mark.parametrize("action_tuple,expected_action_int", [
    ((MockTensor(), None), 3),  # PyTorch 0D tensor + states
    ((5, None), 5),             # Pure Python int + states
    (([4], None), 4),           # List/1D array + states
])
def test_run_episode_unboxes_tuple_actions_correctly(
    patch_rl_classes, mock_board, mock_env, mock_agent, action_tuple, expected_action_int
):
    """
    Ensures that the SB3 predict() tuple (action, states) is correctly split,
    and the action array/tensor is successfully flattened to a Python integer.
    """
    mock_agent.predict.return_value = action_tuple

    solver = RLSolver("backend/agent.zip")
    solver.solve(mock_board)

    # Asserts Gym step() safely received a clean Python int
    mock_env.step.assert_called_with(expected_action_int)


def test_solve_failsafe_infinite_loop_prevention(patch_rl_classes, mock_board, mock_env, mock_agent):
    # Env gets stuck returning False indefinitely
    mock_env.step.return_value = ({"grid": [1]}, 0.0, False, False, {})

    solver = RLSolver("backend/agent.zip")
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.TIMEOUT
    assert result._metrics._steps == 1000
    assert "Hit hard loop limit" in result._message


def test_solve_handles_crashes_gracefully(patch_rl_classes, mock_board):
    mock_agent_cls, mock_env_cls = patch_rl_classes
    mock_env_cls.side_effect = Exception("CUDA Out of Memory Error")

    solver = RLSolver("backend/agent.zip")
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None
    assert result._metrics._steps == 0
    assert "crashed during execution" in result._message