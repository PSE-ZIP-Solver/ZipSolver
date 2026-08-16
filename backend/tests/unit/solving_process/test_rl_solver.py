from pathlib import Path

import pytest
from unittest.mock import MagicMock

from backend.puzzle_logic.board import Board
from backend.solution_path import SolutionPath
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.solver_result import SolverResult
from backend.solving_process.rl_solver import RLSolver

# --- FIXTURES & ISOLATED MOCKING ---


@pytest.fixture
def mock_board():
    board = MagicMock(spec=Board)
    board.getSize = 6
    return board


@pytest.fixture
def mock_env():
    env = MagicMock()
    env.reset.return_value = ({"grid": [0]}, {})
    env.step.return_value = ({"grid": [1]}, 1.0, True, False, {})

    # isFinished() is called as a method by _run_episode, not read as a property.
    env.game.isFinished.return_value = True
    # getState.getPath is accessed as a plain attribute (no call), so a direct
    # value assignment on the mock is enough - no property() trick needed.
    env.game.getState.getPath = ["Pos(0,0)", "Pos(0,1)"]

    return env


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    # RLAgent.predict() already unwraps SB3's (action, state) tuple internally
    # and returns just the action, so the mock should mirror that.
    agent.predict.return_value = 2
    agent._model = MagicMock()
    return agent


@pytest.fixture(autouse=True)
def patch_rl_classes(monkeypatch, mock_env, mock_agent):
    """
    Patch the RLAgent/RLEnvironment names actually used inside rl_solver.py.

    rl_solver.py does `from backend.rl_components.rl_agent import RLAgent`
    (and similarly for RLEnvironment) at import time, so those names live in
    rl_solver's own module namespace. Patching sys.modules after that import
    has already happened has no effect - the module-level names must be
    patched directly.
    """
    mock_agent_cls = MagicMock(return_value=mock_agent)
    mock_env_cls = MagicMock(return_value=mock_env)

    monkeypatch.setattr("backend.solving_process.rl_solver.RLAgent", mock_agent_cls)
    monkeypatch.setattr("backend.solving_process.rl_solver.RLEnvironment", mock_env_cls)

    yield mock_agent_cls, mock_env_cls


@pytest.fixture(autouse=True)
def patch_model_existence(monkeypatch):
    """
    _get_model_path() checks Path.exists() against a real path under
    PROJECT_ROOT. Tests shouldn't depend on a trained model actually being
    present on disk, so treat every path as existing.
    """
    monkeypatch.setattr(Path, "exists", lambda self: True)


class IntLike:
    """Stand-in for anything predict() might return that supports int()."""

    def __init__(self, value):
        self._value = value

    def __int__(self):
        return self._value


# --- FAILURE / VALIDATION EDGE CASES ---
# RLSolver has no dedicated pre-validation for these cases anymore - it lets
# the underlying error propagate up and gets caught by solve()'s broad
# except block, which always reports SolverStatus.FAILED.

def test_solve_returns_failed_result_for_none_board():
    solver = RLSolver()
    result = solver.solve(None)

    assert result._status == SolverStatus.FAILED
    assert result._path is None
    assert result._metrics._steps == 0
    assert "RLSolver error" in result._message


def test_solve_returns_failed_result_for_unsupported_board_size():
    board = MagicMock(spec=Board)
    board.getSize = 0  # no trained model exists for a 0x0 board

    solver = RLSolver()
    result = solver.solve(board)

    assert result._status == SolverStatus.FAILED
    assert result._metrics._steps == 0
    assert "No RL model available" in result._message


# --- BEHAVIOR TESTS ---

def test_solve_success_complete_solution(patch_rl_classes, mock_board, mock_env, mock_agent):
    mock_env.step.side_effect = [
        ({"grid": [1]}, 0.0, False, False, {}),
        ({"grid": [2]}, 0.0, False, False, {}),
        ({"grid": [3]}, 1.0, True, False, {}),
    ]

    solver = RLSolver()
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.SOLVED
    assert result._metrics._steps == 3
    assert result._path is not None
    mock_env.reset.assert_called_once()


def test_load_agent_caching_avoids_reloading_weights(patch_rl_classes, mock_board, mock_env, mock_agent):
    mock_agent_cls, mock_env_cls = patch_rl_classes

    solver = RLSolver()
    solver.solve(mock_board)

    # Simulate a second solve loop with a brand new environment.
    second_mock_env = MagicMock()
    second_mock_env.reset.return_value = ({"grid": [0]}, {})
    second_mock_env.step.return_value = ({"grid": [1]}, 1.0, True, False, {})
    second_mock_env.game.isFinished.return_value = True
    second_mock_env.game.getState.getPath = []

    mock_env_cls.return_value = second_mock_env

    solver.solve(mock_board)

    assert mock_agent_cls.call_count == 1  # model loaded from disk only once
    # On a cache hit, RLSolver swaps the environment on the cached agent
    # directly - it doesn't reach into agent._model itself.
    mock_agent.set_env.assert_called_with(second_mock_env)


@pytest.mark.parametrize(
    "agent_action,expected_action_int",
    [
        (5, 5),
        (IntLike(3), 3),
    ],
)
def test_run_episode_converts_predicted_action_to_int(
    patch_rl_classes, mock_board, mock_env, mock_agent, agent_action, expected_action_int
):
    mock_agent.predict.return_value = agent_action

    solver = RLSolver()
    solver.solve(mock_board)

    # Asserts the env's step() safely received a clean Python int.
    mock_env.step.assert_called_with(expected_action_int)


def test_solve_reports_failed_when_environment_truncates(patch_rl_classes, mock_board, mock_env, mock_agent):
    # RLSolver has no step-count guard of its own; it relies on the
    # environment to set truncated=True once its own max_steps is hit.
    mock_env.step.side_effect = [
        ({"grid": [1]}, 0.0, False, False, {}),
        ({"grid": [2]}, 0.0, False, False, {}),
        ({"grid": [3]}, 0.0, False, True, {}),
    ]

    solver = RLSolver()
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.FAILED
    assert result._metrics._steps == 3
    assert "maximum step limit reached" in result._message


def test_solve_handles_crashes_gracefully(patch_rl_classes, mock_board):
    mock_agent_cls, mock_env_cls = patch_rl_classes
    mock_env_cls.side_effect = Exception("CUDA Out of Memory Error")

    solver = RLSolver()
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.FAILED
    assert result._path is None
    assert result._metrics._steps == 0
    assert "CUDA Out of Memory Error" in result._message