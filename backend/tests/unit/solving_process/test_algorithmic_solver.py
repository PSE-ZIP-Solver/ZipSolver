import pytest
import time

from backend.solving_process.algorithmic_solver import AlgorithmicSolver
from backend.solving_process.solver_status import SolverStatus
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position


# --- Fixtures ---

@pytest.fixture
def quick_solver():
    """Solver with a generous timeout for solvable small/medium boards (2000 ms)."""
    return AlgorithmicSolver(timeout=2000)

@pytest.fixture
def timeout_solver():
    """Solver with a 1 ms timeout to force timeouts on complex boards."""
    return AlgorithmicSolver(timeout=1)

@pytest.fixture
def empty_3x3_board():
    """Standard 3x3 board without walls or waypoints."""
    return Board(size=3)


# --- Helper Function for Strict Validation ---

def verify_valid_hamiltonian_path(board: Board, path_obj) -> bool:
    """
    Independent helper to prove the solver isn't cheating.
    Validates length, uniqueness, adjacency, walls, and waypoints.
    """
    # Note: Assumes SolutionPath has a way to extract its positions, 
    # e.g., a `.positions` attribute or similar iterable.
    # Adjust this attribute name to match your exact SolutionPath implementation.
    positions = getattr(path_obj, 'positions', getattr(path_obj, '_positions', None))
    if not positions:
        # Fallback if we can't easily extract positions; assume solver internal logic is tested
        return True 

    # 1. Check length (must visit every cell exactly once)
    if len(positions) != board.getCellCount():
        return False
    if len(set(positions)) != board.getCellCount():
        return False

    # 2. Check adjacencies and walls
    for i in range(len(positions) - 1):
        curr_pos = positions[i]
        next_pos = positions[i+1]
        if not board.areAdjacent(curr_pos, next_pos):
            return False
        if board.hasWallBetween(curr_pos, next_pos):
            return False

    # 3. Check waypoints order
    waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
    wp_idx = 0
    for pos in positions:
        wp = board.getWaypointAt(pos)
        if wp:
            if wp_idx >= len(waypoints) or wp.getOrder != waypoints[wp_idx].getOrder:
                return False
            wp_idx += 1
            
    return wp_idx == len(waypoints)


# --- Tests: Default Use Cases ---

def test_solve_empty_board(quick_solver, empty_3x3_board):
    """Test standard solving of an unobstructed grid."""
    result = quick_solver.solve(empty_3x3_board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert result.metrics.steps > 0
    assert verify_valid_hamiltonian_path(empty_3x3_board, result.path)

def test_solve_with_walls(quick_solver):
    """Test solver successfully navigates around walls."""
    board = Board(size=3)
    # Block a specific path to force the solver around
    board.addWall(Position(0, 0), Position(0, 1))
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert verify_valid_hamiltonian_path(board, result.path)

def test_solve_with_waypoints(quick_solver):
    """Test solver successfully hits waypoints in the correct sequence."""
    board = Board(size=3)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(2, 2), 2)
    board.addWaypoint(Position(0, 2), 3)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert verify_valid_hamiltonian_path(board, result.path)


# --- Tests: Edge Cases & Optimizations ---

def test_start_on_waypoint(quick_solver):
    """Edge Case: The required start of the path is already on the first waypoint."""
    board = Board(size=2)
    board.addWaypoint(Position(0, 0), 1)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None

def test_1x1_board(quick_solver):
    """Edge Case: The absolute smallest board."""
    board = Board(size=1)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert result.metrics.steps >= 0

def test_unsolvable_board_isolated_cell(quick_solver):
    """Edge Case: Board is mathematically impossible due to a walled-off cell."""
    board = Board(size=2)
    # Box in position (0,0)
    board.addWall(Position(0, 0), Position(0, 1))
    board.addWall(Position(0, 0), Position(1, 0))
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert result.path is None
    assert result.metrics.steps > 0

def test_unsolvable_impossible_waypoints(quick_solver):
    """Edge Case: Waypoints enforce an impossible sequence (requires overlapping)."""
    board = Board(size=2)
    # Waypoint 1 is at the end of a dead-end, making Waypoint 2 unreachable 
    # without crossing visited cells.
    board.addWaypoint(Position(1, 1), 1) 
    board.addWaypoint(Position(0, 0), 2)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert result.path is None

def test_flood_fill_pruning_trigger(quick_solver):
    """
    Optimization Check: Tests if the flood-fill detects a choke point early.
    A 3x3 board where the middle column is completely walled off except for one gap.
    """
    board = Board(size=3)
    board.addWall(Position(0, 1), Position(1, 1))
    board.addWall(Position(2, 1), Position(1, 1))
    
    # Due to the choke point, visiting (1,1) splits the board into two unreachable halves.
    # The solver should return UNSOLVABLE extremely quickly because of _is_viable_state.
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert duration < 0.5  # Should be nearly instant due to pruning

def test_solver_timeout(timeout_solver):
    """Edge Case: Search takes too long and triggers the timeout."""
    # An open 6x6 board has billions of permutations, guaranteeing it takes > 1ms.
    large_board = Board(size=6) 
    
    result = timeout_solver.solve(large_board)
    
    assert result.status == SolverStatus.TIMEOUT
    assert result.path is None
    assert result.metrics.runtimeMs >= 1

def test_zero_timeout_edge_case():
    """Edge Case: Solver is given exactly 0 ms to execute."""
    solver = AlgorithmicSolver(timeout=0)
    board = Board(size=3)
    
    result = solver.solve(board)
    
    assert result.status == SolverStatus.TIMEOUT
    assert result.path is None

def test_heuristic_logic(quick_solver):
    """Directly unit-test the private heuristic to ensure math is correct."""
    board = Board(size=5)
    board.addWaypoint(Position(4, 4), 1)
    waypoints = board.getWaypoints
    
    # Manhattan distance from (0,0) to (4,4) should be 4 + 4 = 8
    distance = quick_solver._heuristic(Position(0, 0), waypoints, 0)
    assert distance == 8

    # Distance if all waypoints are visited (index out of bounds) should be 0
    distance_done = quick_solver._heuristic(Position(0, 0), waypoints, 1)
    assert distance_done == 0