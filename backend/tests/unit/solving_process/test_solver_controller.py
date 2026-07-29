import pytest
from unittest.mock import MagicMock

from backend.puzzle_logic.board import Board
from backend.solution_path import SolutionPath
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.solver_metrics import SolverMetrics
from backend.solving_process.solver_result import SolverResult
from backend.validation_result import ValidationResult
from backend.solving_process.solver_controller import SolverController

# --- FIXTURES & MOCK FACTORIES ---

@pytest.fixture
def mock_dependencies():
    rl_solver = MagicMock()
    algo_solver = MagicMock()
    validator = MagicMock()
    return rl_solver, algo_solver, validator

@pytest.fixture
def controller(mock_dependencies):
    rl_solver, algo_solver, validator = mock_dependencies
    return SolverController(rl_solver, algo_solver, validator)

@pytest.fixture
def dummy_board():
    return Board(size=6)

@pytest.fixture
def dummy_metrics():
    metrics = MagicMock(spec=SolverMetrics)
    metrics._runtimeMs = 100
    metrics._steps = 10
    return metrics

def create_mock_solver_result(status, path, metrics):
    """Creates a mock honoring the protected attribute domain rules."""
    result = MagicMock(spec=SolverResult)
    result._status = status
    result._path = path
    result._metrics = metrics
    return result

def create_mock_validation(is_valid):
    """Mocks the property explicitly"""
    val = MagicMock(spec=ValidationResult)
    type(val).isValid = PropertyMock(return_value=is_valid) if hasattr(MagicMock, "PropertyMock") else is_valid
    val.isValid = is_valid  
    return val


# --- STANDARD ORCHESTRATION TESTS ---

def test_solve_rl_agent_succeeds_and_is_valid(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    valid_path = SolutionPath()
    
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.SOLVED, valid_path, dummy_metrics)
    validator.validate.return_value = create_mock_validation(True)

    response = controller.solve(dummy_board)

    # Restored: Crucial Orchestration Assertions
    rl_solver.solve.assert_called_once_with(dummy_board)
    validator.validate.assert_called_once_with(dummy_board, valid_path)
    algo_solver.solve.assert_not_called()

    # Rule Enforcement: Property usage without parentheses
    assert response.getSuccess is True
    assert response.getSolverUsed == "RLSolver"
    assert response.getPath == valid_path


def test_solve_rl_agent_invalid_path_triggers_fallback_and_succeeds(controller, mock_dependencies, dummy_board, dummy_metrics):
    # Restored: Testing the crucial branch where RL solves but validation flags it as mathematically invalid
    rl_solver, algo_solver, validator = mock_dependencies
    
    rl_path = SolutionPath()
    algo_path = SolutionPath()
    
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.SOLVED, rl_path, dummy_metrics)
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.SOLVED, algo_path, dummy_metrics)
    
    # First validation (RL) fails, Second validation (Algo) succeeds
    validator.validate.side_effect = [create_mock_validation(False), create_mock_validation(True)]

    response = controller.solve(dummy_board)

    rl_solver.solve.assert_called_once_with(dummy_board)
    algo_solver.solve.assert_called_once_with(dummy_board)
    
    assert response.getSuccess is True
    assert response.getSolverUsed == "AlgorithmicSolver"
    assert response.getPath == algo_path


def test_solve_rl_agent_raises_exception_triggers_fallback(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    valid_path = SolutionPath()
    
    # RL agent crashes (e.g., PyTorch Tensor exception)
    rl_solver.solve.side_effect = Exception("Tensor runtime error")
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.SOLVED, valid_path, dummy_metrics)
    validator.validate.return_value = create_mock_validation(True)

    response = controller.solve(dummy_board)

    # Assure controller swallowed the RL error and hit fallback successfully
    algo_solver.solve.assert_called_once_with(dummy_board)
    validator.validate.assert_called_once_with(dummy_board, valid_path)
    assert response.getSuccess is True
    assert response.getSolverUsed == "AlgorithmicSolver"


# --- REQUIRED EDGE CASE TESTS (From Design Spec) ---

def test_solve_edge_case_empty_board(controller, mock_dependencies, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    board_empty = Board(size=0)
    
    # 0x0 boards return mathematically unsolvable instantly
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)

    response = controller.solve(board_empty)
    
    validator.validate.assert_not_called()
    assert response.getSuccess is False
    assert response.getPath is None


def test_solve_edge_case_timeout(controller, mock_dependencies, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # Both time out without producing paths
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.TIMEOUT, None, dummy_metrics)
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.TIMEOUT, None, dummy_metrics)

    response = controller.solve(dummy_board)
    
    rl_solver.solve.assert_called_once_with(dummy_board)
    algo_solver.solve.assert_called_once_with(dummy_board)
    validator.validate.assert_not_called()  # No validation on timed-out empty paths
    
    assert response.getSuccess is False


def test_solve_edge_case_isolated_cells(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # Path is disconnected, solvers detect this early and return UNSOLVABLE (Replaced invalid FAILED enum)
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)

    response = controller.solve(dummy_board)
    
    assert response.getSuccess is False
    assert response.getPath is None
    assert response.getSolverUsed == "AlgorithmicSolver"