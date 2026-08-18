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
    """
    Provides isolated stub configurations preventing cascaded dependency invocations.

    Returns:
        A sequential tuple encompassing strictly mocked RL, algorithmic, and validation frameworks.

    Implementation Details:
        Utilizes `MagicMock` to structurally sever deep algorithmic logic and strict mathematical validation 
        layers, permitting centralized behavioral testing of the controller's state orchestration.
    """
    rl_solver = MagicMock()
    algo_solver = MagicMock()
    validator = MagicMock()
    return rl_solver, algo_solver, validator

@pytest.fixture
def controller(mock_dependencies):
    """
    Instantiates the overarching computational orchestrator initialized with dummy components.

    Args:
        mock_dependencies: The isolated mock configurations representing active modules.

    Returns:
        The fully fabricated solver controller tracking dynamic pipeline operations.

    Implementation Details:
        Utilizes native constructor dependency injection seamlessly circumventing the architectural 
        lazy-loading safeguards typically initialized directly internally.
    """
    rl_solver, algo_solver, validator = mock_dependencies
    return SolverController(rl_solver, algo_solver, validator)

@pytest.fixture
def dummy_board():
    """
    Generates a localized lightweight spatial limitation boundary.

    Returns:
        The instantiated baseline layout configuration.

    Implementation Details:
        Creates a structurally valid default array preventing architectural null-reference errors 
        when passed sequentially into orchestrator pathways.
    """
    return Board(size=6)

@pytest.fixture
def dummy_metrics():
    """
    Fabricates consistent analytical telemetry readings for assertion mapping.

    Returns:
        The protected analytical payload.

    Implementation Details:
        Explicitly seeds localized magic tracking variants bound directly to hidden protected attributes, 
        violently bypassing immutable domain models securely encapsulating read-only property parameters.
    """
    metrics = MagicMock(spec=SolverMetrics)
    metrics._runtimeMs = 100
    metrics._steps = 10
    return metrics

def create_mock_solver_result(status, path, metrics):
    """
    Simulates securely formatted architectural execution packages returned by solving models.

    Args:
        status: The desired simulated absolute outcome enum matrix.
        path: The resultant sequence graph map object structure.
        metrics: The simulated telemetry metric wrapper parameter.

    Returns:
        The safely parameterized standard payload envelope simulating engine completions.

    Implementation Details:
        Ensures strict domain boundaries by intentionally bypassing encapsulation via direct protected 
        attribute mapping instead of relying upon external constructors, satisfying deep nested property 
        hook architectures expected during testing iterations.
    """
    """Creates a mock honoring the protected attribute domain rules."""
    result = MagicMock(spec=SolverResult)
    result._status = status
    result._path = path
    result._metrics = metrics
    return result

def create_mock_validation(is_valid):
    """
    Fabricates a simulated mathematical compliance report.

    Args:
        is_valid: The desired truth state representing structural compliance.

    Returns:
        The stubbed validation result envelope.

    Implementation Details:
        Leverages dynamic property mocking to securely bind the truth flag to the 
        `isValid` attribute. This explicitly mirrors the domain's strict encapsulation 
        rule requiring access via uninvoked property hooks rather than standard method calls.
    """
    """Mocks the property explicitly"""
    val = MagicMock(spec=ValidationResult)
    type(val).isValid = PropertyMock(return_value=is_valid) if hasattr(MagicMock, "PropertyMock") else is_valid
    val.isValid = is_valid  
    return val


# --- STANDARD ORCHESTRATION TESTS ---

def test_solve_rl_agent_succeeds_and_is_valid(controller, mock_dependencies, dummy_board, dummy_metrics):
    """
    Verifies optimal execution sequences utilizing direct primary engine success logic.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_board: The local spatial baseline simulation object.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Projects successful initial evaluation patterns passing both native calculation logic and 
        secondary rule evaluations securely. Actively guarantees the orchestrator appropriately skips 
        exhaustive algorithmic engines, routing parameters seamlessly while accessing specific payload arrays 
        without standard parenthesis execution logic.
    """
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
    """
    Evaluates execution persistence securely degrading processing loops upon mathematical rejection.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_board: The local spatial baseline simulation object.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Mechanically seeds the mathematical validator explicitly rejecting the primary engine output, 
        simulating a scenario where the network yields hallucinatory moves. Asserts the controller natively 
        absorbs the logical disruption and actively routes computations into the strictly deterministic A* module.
    """
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
    """
    Confirms robust orchestration survival isolating primary framework hardware exceptions.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_board: The local spatial baseline simulation object.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Forcefully generates severe localized framework termination crashes upon initial network engine invocation. 
        Records definitive testing verifying the orchestration cleanly catches execution faults seamlessly, entirely 
        ignoring pipeline corruption as it natively engages secondary heuristic fallbacks securely.
    """
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
    """
    Secures absolute pipeline rejection managing unresolvable minimum limit boundaries.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Pushes impossible scalar environments through the nested solver array tracking. Employs 
        mock tracking identifying validators natively abstained from evaluating execution arrays since 
        both frameworks definitively terminated calculations entirely mapped under strict unsolvable domains.
    """
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
    """
    Evaluates safe traversal failure managing cascaded temporal calculation limits.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Submits evaluation frameworks configured strictly to emulate severe computational boundaries. 
        Confirms orchestrators acknowledge simultaneous time limit breeches cleanly without invoking 
        mathematical structural checks upon unpopulated tracking pathways.
    """
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
    """
    Confirms robust reporting mapping distinct mathematical impossibility boundaries.

    Args:
        controller: The fully instantiated operational orchestration gateway.
        mock_dependencies: The isolated mock configurations containing framework nodes.
        dummy_board: The local spatial baseline simulation object.
        dummy_metrics: The mapped metric outcome parameters.

    Implementation Details:
        Binds deep logic evaluations dictating absolutely uncrossable topology formations. Validates 
        orchestration mechanics successfully map distinct internal unsolvable execution matrices over broad 
        generic failures safely to standardized string endpoints representing correct diagnostic arrays.
    """
    rl_solver, algo_solver, validator = mock_dependencies
    
    # Path is disconnected, solvers detect this early and return UNSOLVABLE (Replaced invalid FAILED enum)
    rl_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)
    algo_solver.solve.return_value = create_mock_solver_result(SolverStatus.UNSOLVABLE, None, dummy_metrics)

    response = controller.solve(dummy_board)
    
    assert response.getSuccess is False
    assert response.getPath is None
    assert response.getSolverUsed == "AlgorithmicSolver"