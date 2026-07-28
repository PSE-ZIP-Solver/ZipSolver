import pytest
from unittest.mock import MagicMock
from backend.puzzle_logic.board import Board
from backend.solution_path import SolutionPath
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.solver_metrics import SolverMetrics
from backend.solving_process.solver_result import SolverResult
from backend.validation_result import ValidationResult
from backend.solving_process.solver_controller import SolverController


@pytest.fixture
def mock_dependencies():
    """
    Creates mocked versions of the injected dependencies.
    """
    rl_solver = MagicMock()
    algo_solver = MagicMock()
    validator = MagicMock()
    return rl_solver, algo_solver, validator


@pytest.fixture
def controller(mock_dependencies):
    """
    Instantiates the SolverController with the mocked dependencies.
    """
    rl_solver, algo_solver, validator = mock_dependencies
    return SolverController(rl_solver, algo_solver, validator)


@pytest.fixture
def dummy_board():
    return Board(size=3)


@pytest.fixture
def dummy_metrics():
    return SolverMetrics(runtimeMs=100, steps=10, attempts=1)


def test_solve_rl_agent_succeeds_and_is_valid(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # 1. Setup: RL returns a valid solution
    valid_path = SolutionPath()
    rl_result = SolverResult(SolverStatus.SOLVED, valid_path, "RL Done", dummy_metrics)
    rl_solver.solve.return_value = rl_result
    
    validation_result = ValidationResult(valid=True, message="Looks good", errors=[])
    validator.validate.return_value = validation_result

    # 2. Action
    response = controller.solve(dummy_board)

    # 3. Assertions
    rl_solver.solve.assert_called_once_with(dummy_board)
    validator.validate.assert_called_once_with(dummy_board, valid_path)
    
    # Algorithmic fallback should NOT be called
    algo_solver.solve.assert_not_called()
    
    assert response.getSuccess is True
    assert response.getSolverUsed == "RLSolver"
    assert response.getPath == valid_path


def test_solve_rl_agent_fails_fallback_succeeds(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # 1. Setup: RL fails entirely (no path)
    rl_result = SolverResult(SolverStatus.FAILED, None, "RL Failed", dummy_metrics)
    rl_solver.solve.return_value = rl_result
    
    # Setup: Algorithmic solver succeeds
    valid_path = SolutionPath()
    algo_result = SolverResult(SolverStatus.SOLVED, valid_path, "Algo Done", dummy_metrics)
    algo_solver.solve.return_value = algo_result
    
    validation_result = ValidationResult(valid=True, message="Looks good", errors=[])
    validator.validate.return_value = validation_result

    # 2. Action
    response = controller.solve(dummy_board)

    # 3. Assertions
    rl_solver.solve.assert_called_once_with(dummy_board)
    algo_solver.solve.assert_called_once_with(dummy_board)
    validator.validate.assert_called_once_with(dummy_board, valid_path)
    
    assert response.getSuccess is True
    assert response.getSolverUsed == "AlgorithmicSolver"
    assert response.getPath == valid_path


def test_solve_rl_agent_invalid_path_triggers_fallback(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # 1. Setup: RL returns a path, but the validator says it's WRONG.
    rl_path = SolutionPath()
    rl_result = SolverResult(SolverStatus.SOLVED, rl_path, "RL Found Path", dummy_metrics)
    rl_solver.solve.return_value = rl_result
    
    algo_path = SolutionPath()
    algo_result = SolverResult(SolverStatus.SOLVED, algo_path, "Algo Found Path", dummy_metrics)
    algo_solver.solve.return_value = algo_result
    
    # First validation (for RL) fails, Second validation (for Algo) succeeds
    failed_val = ValidationResult(valid=False, message="Invalid RL Path", errors=[])
    success_val = ValidationResult(valid=True, message="Valid Algo Path", errors=[])
    validator.validate.side_effect = [failed_val, success_val]

    # 2. Action
    response = controller.solve(dummy_board)

    # 3. Assertions
    rl_solver.solve.assert_called_once_with(dummy_board)
    algo_solver.solve.assert_called_once_with(dummy_board)
    
    assert validator.validate.call_count == 2
    
    assert response.getSuccess is True
    assert response.getSolverUsed == "AlgorithmicSolver"
    assert response.getPath == algo_path


def test_solve_both_solvers_fail(controller, mock_dependencies, dummy_board, dummy_metrics):
    rl_solver, algo_solver, validator = mock_dependencies
    
    # 1. Setup: Both fail to find a solution
    rl_result = SolverResult(SolverStatus.FAILED, None, "RL Failed", dummy_metrics)
    algo_result = SolverResult(SolverStatus.UNSOLVABLE, None, "Algo Failed", dummy_metrics)
    
    rl_solver.solve.return_value = rl_result
    algo_solver.solve.return_value = algo_result

    # 2. Action
    response = controller.solve(dummy_board)

    # 3. Assertions
    rl_solver.solve.assert_called_once_with(dummy_board)
    algo_solver.solve.assert_called_once_with(dummy_board)
    
    # No path was generated, so validation should never be called
    validator.validate.assert_not_called()
    
    assert response.getSuccess is False
    assert response.getPath is None
    assert response.getSolverUsed == "AlgorithmicSolver"  # The fallback solver was the last one used