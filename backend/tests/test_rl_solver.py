import pytest
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
    """Test standard success path where agent navigates to the end."""
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    game_instance = mock_game.return_value
    
    env_instance.reset.return_value = ("mock_obs_0", {})
    env_instance.step.side_effect = [
        ("mock_obs_1", 1.0, False, False, {}),               
        ("mock_obs_2", 10.0, True, False, {"is_success": True}) 
    ]
    
    # Predict returns standard integers
    agent_instance.predict.side_effect = [1, 2] 
    
    mock_state = MagicMock()
    mock_state.getPath = ["pos_start", "pos_1", "pos_2"]
    game_instance.getState = mock_state
    game_instance.isFinished.return_value = True
    
    solver = RLSolver()
    result = solver.solve(mock_board)
    
    assert result.getStatus == SolverStatus.SOLVED
    assert len(result.getPath.getPositions) == 3
    assert result.getMetrics.getSteps == 2


# --- EDGE CASES & FAILURES ---

def test_solve_handles_gym_environment_crash_gracefully(mock_board, mock_env):
    """Edge Case: The board is invalid or Env setup fails (e.g. ValueError)."""
    # Force the RLEnvironment constructor to throw an error (simulating bad board)
    mock_env.side_effect = ValueError("Board has no starting Waypoint with order 1.")
    
    solver = RLSolver()
    result = solver.solve(mock_board)
    
    # Assert it didn't crash the program, but returned a clean FAILED result
    assert result.getStatus == SolverStatus.FAILED
    assert result.getPath is None
    assert "RLSolver crashed during execution" in result.getMessage
    assert "no starting Waypoint" in result.getMessage


def test_solve_handles_numpy_action_types(mock_board, mock_game, mock_env, mock_agent):
    """Edge Case: SB3 predict returns a numpy scalar instead of a raw int."""
    import numpy as np
    
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    game_instance = mock_game.return_value
    
    env_instance.reset.return_value = ("mock_obs", {})
    env_instance.step.return_value = ("mock_obs", 1.0, True, False, {})
    
    # Simulate a numpy scalar return (common in SB3)
    agent_instance.predict.return_value = np.int64(3) 
    
    game_instance.getState.getPath = ["pos"]
    game_instance.isFinished.return_value = False
    
    solver = RLSolver()
    solver.solve(mock_board)
    
    # Ensure env.step was called with a native python int, NOT a numpy int
    action_passed_to_step = env_instance.step.call_args[0][0]
    assert type(action_passed_to_step) is int
    assert action_passed_to_step == 3


def test_failsafe_infinite_loop_prevention(mock_board, mock_game, mock_env, mock_agent):
    """Edge Case: Gym environment is bugged and never sets terminated/truncated to True."""
    env_instance = mock_env.return_value
    agent_instance = mock_agent.return_value
    
    env_instance.reset.return_value = ("mock_obs", {})
    # Always returns False for terminated and truncated
    env_instance.step.return_value = ("mock_obs", 0.0, False, False, {})
    agent_instance.predict.return_value = 1
    
    solver = RLSolver()
    result = solver.solve(mock_board)
    
    # Should trip the failsafe at 1000 steps and exit safely
    assert result.getStatus == SolverStatus.FAILED
    assert result.getMetrics.getSteps == 1000
    assert "Hit hard loop limit" in result.getMessage