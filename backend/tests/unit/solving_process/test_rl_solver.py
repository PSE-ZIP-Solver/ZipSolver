import pytest
import logging
from unittest.mock import patch, MagicMock

from backend.solving_process.solver_status import SolverStatus
from backend.puzzle_logic.board import Board
from backend.solving_process.rl_solver import RLSolver 


@pytest.fixture
def mock_board():
    return MagicMock(spec=Board)

@pytest.fixture
def mock_game():
    with patch('backend.rl_solver.Game') as mock:
        yield mock

@pytest.fixture
def mock_env():
    with patch('backend.rl_solver.RLEnvironment') as mock:
        yield mock

@pytest.fixture
def mock_agent():
    with patch('backend.rl_solver.RLAgent') as mock:
        yield mock


# --- DEFAULT USE CASES ---

def test_solve_success(mock_board, mock_game, mock_env, mock_agent):
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    game_instance = mock_game.return_value
    
    env_instance.reset.return_value = ("mock_obs_0", {})
    env_instance.step.side_effect = [
        ("mock_obs_1", 1.0, False, False, {}),               
        ("mock_obs_2", 10.0, True, False, {"is_success": True}) 
    ]
    
    agent_instance.predict.side_effect = [1, 2] 
    
    mock_state = MagicMock()
    mock_state.getPath = ["pos_start", "pos_1", "pos_2"]
    game_instance.getState = mock_state
    game_instance.isFinished.return_value = True
    
    solver = RLSolver(model_path="custom_model.zip")
    result = solver.solve(mock_board)
    
    assert result.getStatus == SolverStatus.SOLVED
    assert len(result.getPath.getPositions) == 3
    assert result.getMetrics.getSteps == 2


# --- RESOURCE & OPTIMIZATION TESTS ---

def test_environment_cleanup_prevents_memory_leak(mock_board, mock_env, mock_agent):
    """Ensure previous Gym environments are explicitly closed before creating new ones."""
    solver = RLSolver()
    
    # Run once
    solver.solve(mock_board)
    
    # Capture the first generated mock environment
    first_env_instance = solver._environment
    
    # Run twice
    solver.solve(mock_board)
    
    # Assert the old environment was closed before the new one replaced it
    first_env_instance.close.assert_called_once()


def test_agent_caching_prevents_reloading(mock_board, mock_env, mock_agent):
    """Ensure the heavy RLAgent is only loaded once, and environments are swapped."""
    solver = RLSolver()
    
    # 1st Solve
    solver.solve(mock_board)
    assert mock_agent.call_count == 1
    
    dummy_internal_model = MagicMock()
    solver._agent._model = dummy_internal_model

    # 2nd Solve
    solver.solve(mock_board)
    
    # Constructor only called once, but set_env was called to swap
    assert mock_agent.call_count == 1
    assert dummy_internal_model.set_env.call_count == 1


# --- DEFENSIVE EDGE CASES & FAILURES ---

def test_solve_handles_gym_environment_crash_gracefully(mock_board, mock_env, caplog):
    """Edge Case: The board is invalid or Env setup fails (e.g. ValueError)."""
    mock_env.side_effect = ValueError("Board has no starting Waypoint with order 1.")
    
    solver = RLSolver()
    
    with caplog.at_level(logging.ERROR):
        result = solver.solve(mock_board)
    
    assert result.getStatus == SolverStatus.FAILED
    assert result.getPath is None
    assert "RLSolver crashed during execution" in result.getMessage
    
    # Ensure the logger captured the exception stacktrace
    assert "RLSolver crashed during execution" in caplog.text


def test_action_unboxing_numpy_array(mock_board, mock_game, mock_env, mock_agent):
    """Edge Case: SB3 predict returns a 1D numpy array instead of a scalar."""
    import numpy as np
    
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    game_instance = mock_game.return_value
    
    env_instance.reset.return_value = ("mock_obs", {})
    env_instance.step.return_value = ("mock_obs", 1.0, True, False, {})
    
    # Pass a 1D numpy array like [3], which crashes standard int() calls
    agent_instance.predict.return_value = np.array([3]) 
    
    game_instance.getState.getPath = ["pos"]
    game_instance.isFinished.return_value = False
    
    solver = RLSolver()
    solver.solve(mock_board)
    
    action_passed_to_step = env_instance.step.call_args[0][0]
    assert type(action_passed_to_step) is int
    assert action_passed_to_step == 3


def test_solve_handles_none_path(mock_board, mock_game, mock_env, mock_agent):
    """Edge Case: GameState bugs out and returns None for the path."""
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    game_instance = mock_game.return_value
    
    env_instance.reset.return_value = ("mock_obs", {})
    env_instance.step.return_value = ("mock_obs", 1.0, True, False, {})
    agent_instance.predict.return_value = 1
    
    # Set getPath to None to simulate a state bug
    mock_state = MagicMock()
    mock_state.getPath = None
    game_instance.getState = mock_state
    game_instance.isFinished.return_value = False
    
    solver = RLSolver()
    result = solver.solve(mock_board)
    
    # Should not crash, should return a cleanly FAILED result with empty path
    assert result.getStatus == SolverStatus.FAILED
    assert len(result.getPath.getPositions) == 0


def test_failsafe_infinite_loop_prevention(mock_board, mock_game, mock_env, mock_agent):
    """Edge Case: Gym environment is bugged and never sets terminated/truncated to True."""
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    
    env_instance.reset.return_value = ("mock_obs", {})
    env_instance.step.return_value = ("mock_obs", 0.0, False, False, {})
    agent_instance.predict.return_value = 1
    
    solver = RLSolver()
    result = solver.solve(mock_board)
    
    assert result.getStatus == SolverStatus.FAILED
    assert result.getMetrics.getSteps == 1000
    assert "Hit hard loop limit" in result.getMessage