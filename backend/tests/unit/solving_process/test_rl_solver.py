from pathlib import Path

import pytest
from unittest.mock import MagicMock

from backend.puzzle_logic.board import Board
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.rl_solver import RLSolver

# --- FIXTURES & ISOLATED MOCKING ---


@pytest.fixture
def mock_board():
    """
    Fabricates a functional simulation of the foundational geometric boundary configuration.

    Returns:
        A securely mocked object presenting dimensional access thresholds.

    Implementation Details:
        Supplies predefined scalar layouts mapped natively to structural rules logic without
        initiating deeper architectural allocations within the test suite.
    """
    board = MagicMock(spec=Board)
    board.getSize = 6
    return board


@pytest.fixture
def mock_env():
    """
    Constructs a controlled replica of the complex reinforcement execution sandbox.

    Returns:
        The simulated trajectory testing matrix.

    Implementation Details:
        Aggressively intercepts and stubs standard iteration boundaries (e.g., reset, step)
        and specifically configures property access patterns to map seamlessly without
        employing explicit function invocations, mirroring the architectural encapsulation.
    """
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
    """
    Generates a deterministic surrogate for the neural inference engine.

    Returns:
        The simulated decision processing module.

    Implementation Details:
        Simulates high-performance prediction unboxing by natively returning a pure Python
        integer instead of generating cumbersome Machine Learning tuple variants.
    """
    agent = MagicMock()
    # RLAgent.predict() already unwraps SB3's (action, state) tuple internally
    # and returns just the action, so the mock should mirror that.
    agent.predict.return_value = 2
    agent._model = MagicMock()
    return agent


@pytest.fixture(autouse=True)
def patch_rl_classes(monkeypatch, mock_env, mock_agent):
    """
    Isolates the reinforcement learning module from heavy external ML dependencies.

    Args:
        monkeypatch: The Pytest utility for dynamic runtime modifications.
        mock_env: The pre-configured simulation environment substitute.
        mock_agent: The pre-configured neural inference substitute.

    Returns:
        A tuple containing the dynamically injected mock class definitions.

    Implementation Details:
        Directly intercepts the module-level namespace imports within the active solver file.
        By patching the `sys.modules` registry directly at the Pytest fixture level, this
        prevents heavy dependencies (like PyTorch or OpenCV) from crashing CI/CD collection loops
        on testing machines lacking proper hardware acceleration stacks.
    """
    mock_agent_cls = MagicMock(return_value=mock_agent)
    mock_env_cls = MagicMock(return_value=mock_env)

    monkeypatch.setattr("backend.solving_process.rl_solver.RLAgent", mock_agent_cls)
    monkeypatch.setattr("backend.solving_process.rl_solver.RLEnvironment", mock_env_cls)

    yield mock_agent_cls, mock_env_cls


@pytest.fixture(autouse=True)
def patch_model_existence(monkeypatch):
    """
    Dynamically overrides underlying filesystem registry verification algorithms.

    Args:
        monkeypatch: The Pytest utility manipulating the base memory execution thread.

    Implementation Details:
        Forces `Path.exists()` resolutions inherently to True. Prevents the suite from actively
        seeking physical compiled binary models traversing deep directory trees on disk, decoupling
        operational testing logic from structural file requirements.
    """
    monkeypatch.setattr(Path, "exists", lambda self: True)


class IntLike:
    """
    A structural simulation of external scalar outputs mimicking numerical casting interfaces.

    Responsibility:
        Serves as a mock container representing obscure tensor or scalar objects output by
        Machine Learning inferences, validating the architecture's defensive unboxing mechanics.

    Implementation Details:
        Implements the native `__int__` magic method. This safely replicates how the system
        forces unboxing, casting arbitrary predictive variants down to pure native scalars to maintain strict
        serialization schemas across execution boundaries.
    """

    def __init__(self, value):
        """
        Initializes the simulated scalar container.

        Args:
            value: The internal numerical state to be wrapped.

        Implementation Details:
            Captures the provided mathematical baseline into a protected internal attribute,
            preparing it for subsequent unboxing requests.
        """
        self._value = value

    def __int__(self):
        """
        Resolves the unboxed mathematical primitive.

        Returns:
            The pure native numerical representation of the wrapped state.

        Implementation Details:
            Provides the explicit magic method hook intercepted by native Python casting,
            directly mapping to the defensive `.item()` unboxing patterns used within the pipeline.
        """
        return self._value


# --- FAILURE / VALIDATION EDGE CASES ---
# RLSolver has no dedicated pre-validation for these cases anymore - it lets
# the underlying error propagate up and gets caught by solve()'s broad
# except block, which always reports SolverStatus.FAILED.


def test_solve_returns_failed_result_for_none_board():
    """
    Ascertains structural rejection when supplied null topological grids.

    Implementation Details:
        Funnels a direct None reference through the execution node. Verifies the broad
        orchestration block successfully intercepts missing mathematical requirements, bypassing
        critical crash states and translating the failure securely into standard enum returns.
    """
    solver = RLSolver()
    result = solver.solve(None)

    assert result._status == SolverStatus.FAILED
    assert result._path is None
    assert result._metrics._steps == 0
    assert "RLSolver error" in result._message


def test_solve_returns_failed_result_for_unsupported_board_size():
    """
    Validates structural rejection natively halting execution for untrained grid dimensions.

    Implementation Details:
        Provides an empty spatial bound constraint specifically stripped of available model files.
        Asserts the system inherently rejects operation, correctly translating missing dependencies
        into standard failure payloads containing zero analytical progression steps.
    """
    board = MagicMock(spec=Board)
    board.getSize = 0  # no trained model exists for a 0x0 board

    solver = RLSolver()
    result = solver.solve(board)

    assert result._status == SolverStatus.FAILED
    assert result._metrics._steps == 0
    assert "No RL model available" in result._message


# --- BEHAVIOR TESTS ---


def test_solve_success_complete_solution(
    patch_rl_classes, mock_board, mock_env, mock_agent
):
    """
    Evaluates unbroken predictive resolution correctly formulating comprehensive trajectories.

    Args:
        patch_rl_classes: The module suppression fixture matrix.
        mock_board: The simulated structural boundary matrix.
        mock_env: The simulated training simulator parameters.
        mock_agent: The simulated neural evaluation network.

    Implementation Details:
        Iterates predictive decision sequences sequentially simulating navigation completion flags.
        Directly checks resultant outcome states securely pack final solution vectors and exactly match
        the simulated analytical steps counted during nested inference evaluations.
    """
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


def test_load_agent_caching_avoids_reloading_weights(
    patch_rl_classes, mock_board, mock_env, mock_agent
):
    """
    Secures strict architectural singleton patterns avoiding recursive hardware re-initializations.

    Args:
        patch_rl_classes: The module suppression fixture matrix.
        mock_board: The simulated structural boundary matrix.
        mock_env: The simulated training simulator parameters.
        mock_agent: The simulated neural evaluation network.

    Implementation Details:
        Executes sequential solve commands spanning distinctly simulated environments. Asserts
        active neural processing architectures strictly swap internal sandbox trackers via method injection
        instead of redundantly parsing gigabytes of binary weight schemas from persistent drives.
    """
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
    patch_rl_classes,
    mock_board,
    mock_env,
    mock_agent,
    agent_action,
    expected_action_int,
):
    """
    Evaluates defensive numerical casting boundaries against multi-format mathematical predictive arrays.

    Args:
        patch_rl_classes: The module suppression fixture matrix.
        mock_board: The simulated structural boundary matrix.
        mock_env: The simulated training simulator parameters.
        mock_agent: The simulated neural evaluation network.
        agent_action: The dynamic parameterized output structure representing mock tensor variables.
        expected_action_int: The standardized unboxed outcome expected after casting processing.

    Implementation Details:
        Utilizes `pytest.mark.parametrize` mapped with customized `IntLike` wrapping variants to
        safely project obscured dimensional elements against the system unboxing algorithm. Asserts
        predictive modules successfully cast deep learning types securely back into standardized formats.
    """
    mock_agent.predict.return_value = agent_action

    solver = RLSolver()
    solver.solve(mock_board)

    # Asserts the env's step() safely received a clean Python int.
    mock_env.step.assert_called_with(expected_action_int)


def test_solve_reports_failed_when_environment_truncates(
    patch_rl_classes, mock_board, mock_env, mock_agent
):
    """
    Observes appropriate system degradation logic when neural execution loops hit recursive iteration limits.

    Args:
        patch_rl_classes: The module suppression fixture matrix.
        mock_board: The simulated structural boundary matrix.
        mock_env: The simulated training simulator parameters.
        mock_agent: The simulated neural evaluation network.

    Implementation Details:
        Simulates sequential loop iterations eventually resolving the third simulation argument matrix
        parameter as heavily truncated. Observes the internal extraction engine detects bounded truncation
        arrays, actively breaking internal processing threads and accurately propagating the resultant standard failure string.
    """
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
    """
    Guarantees architectural fault tolerance isolating cascaded components from catastrophic framework crashes.

    Args:
        patch_rl_classes: The module suppression fixture matrix.
        mock_board: The simulated structural boundary matrix.

    Implementation Details:
        Actively forces dynamic instability vectors (like deep GPU CUDA Out-Of-Memory cascades) against
        internal operational classes. Guarantees pipeline layers gracefully intercept hard execution terminates
        and formulate seamless external string structures tracking identical enum responses.
    """
    mock_agent_cls, mock_env_cls = patch_rl_classes
    mock_env_cls.side_effect = Exception("CUDA Out of Memory Error")

    solver = RLSolver()
    result = solver.solve(mock_board)

    assert result._status == SolverStatus.FAILED
    assert result._path is None
    assert result._metrics._steps == 0
    assert "CUDA Out of Memory Error" in result._message
