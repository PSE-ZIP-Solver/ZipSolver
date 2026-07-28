import pytest
import time

from backend.solving_process.algorithmic_solver import AlgorithmicSolver
from backend.solving_process.solver_status import SolverStatus
from backend.solution_path import SolutionPath
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

def verify_valid_hamiltonian_path(board: Board, path_obj: SolutionPath) -> bool:
    """
    Validates length, uniqueness, adjacency, walls, and waypoints
    using the provided SolutionPath.getPostions property.
    """
    positions = path_obj.getPositions
    
    if not positions:
        return False

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
    result = quick_solver.solve(empty_3x3_board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert result.metrics.steps > 0
    assert verify_valid_hamiltonian_path(empty_3x3_board, result.path)

def test_solve_with_walls(quick_solver):
    board = Board(size=3)
    board.addWall(Position(0, 0), Position(0, 1))
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert verify_valid_hamiltonian_path(board, result.path)

def test_solve_with_waypoints(quick_solver):
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
    board = Board(size=2)
    board.addWaypoint(Position(0, 0), 1)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert verify_valid_hamiltonian_path(board, result.path)

def test_1x1_board(quick_solver):
    board = Board(size=1)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert result.metrics.steps >= 0
    assert verify_valid_hamiltonian_path(board, result.path)

def test_unsolvable_board_isolated_cell(quick_solver):
    board = Board(size=2)
    board.addWall(Position(0, 0), Position(0, 1))
    board.addWall(Position(0, 0), Position(1, 0))
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert result.path is None
    assert result.metrics.steps > 0

def test_unsolvable_impossible_waypoints(quick_solver):
    board = Board(size=2)
    board.addWaypoint(Position(1, 1), 1) 
    board.addWaypoint(Position(0, 0), 2)
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert result.path is None

def test_flood_fill_pruning_trigger(quick_solver):
    """A 3x3 board where the middle column is completely walled off except for one gap."""
    board = Board(size=3)
    board.addWall(Position(0, 1), Position(1, 1))
    board.addWall(Position(2, 1), Position(1, 1))
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert duration < 0.5  # Should be nearly instant due to pruning

def test_solver_timeout(timeout_solver):
    large_board = Board(size=6) 
    
    result = timeout_solver.solve(large_board)
    
    assert result.status == SolverStatus.TIMEOUT
    assert result.path is None
    assert result.metrics.runtimeMs >= 1

def test_zero_timeout_edge_case():
    solver = AlgorithmicSolver(timeout=0)
    board = Board(size=3)
    
    result = solver.solve(board)
    
    assert result.status == SolverStatus.TIMEOUT
    assert result.path is None

def test_heuristic_logic(quick_solver):
    board = Board(size=5)
    board.addWaypoint(Position(4, 4), 1)
    waypoints = board.getWaypoints
    
    distance = quick_solver._heuristic(Position(0, 0), waypoints, 0)
    assert distance == 8

    distance_done = quick_solver._heuristic(Position(0, 0), waypoints, 1)
    assert distance_done == 0

def test_dead_end_pruning_trigger(quick_solver):
    """
    NEW Edge Case: Tests the Dead-End degree-1 pruning logic.
    A board that is technically connected, but forces two dead-ends, 
    making a Hamiltonian path mathematically impossible.
    """
    board = Board(size=3)
    # Block cells to create a "T" junction or similar shape that 
    # leaves two corners with only 1 entrance/exit.
    board.addWall(Position(0, 0), Position(1, 0)) # Isolates 0,0 to only go down
    board.addWall(Position(2, 0), Position(1, 0)) # Isolates 2,0 to only go down
    
    # Because (0,0) and (2,0) BOTH only have 1 valid exit (going down),
    # a single path cannot start and end in both. It must be unsolvable instantly.
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result.status == SolverStatus.UNSOLVABLE
    # Assert the new optimization pruned it before doing heavy searching
    assert duration < 0.2  
    
def test_bitmask_index_bounds(quick_solver):
    """
    Ensures the bitmask index calculation doesn't overflow or calculate incorrectly.
    """
    board = Board(size=8) # 8x8 requires up to 63 bits
    
    # Top left
    assert quick_solver._get_bit_index(Position(0, 0), 8) == 0
    # Bottom right
    assert quick_solver._get_bit_index(Position(7, 7), 8) == 63

def test_mathematical_pruning_3_dead_ends(quick_solver):
    """
    CRITICAL FIX TEST: Verifies the > 2 dead-end constraint.
    Creates 3 cells that only have exactly 1 entrance/exit. 
    A single continuous path can only connect 2 ends; connecting 3 is impossible.
    """
    board = Board(size=3)
    
    # Isolate Top-Left (0,0) to only exit via (1,0)
    board.addWall(Position(0, 0), Position(0, 1))
    
    # Isolate Bottom-Left (0,2) to only exit via (1,2)
    board.addWall(Position(0, 2), Position(0, 1))
    
    # Isolate Top-Right (2,0) to only exit via (1,0)
    board.addWall(Position(2, 0), Position(2, 1))
    
    # Now there are 3 dead ends in the unvisited graph: (0,0), (0,2), (2,0).
    # The solver MUST recognize this immediately and return UNSOLVABLE,
    # rather than taking seconds/minutes to brute force it.
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result.status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Should be nearly instant

def test_long_snake_valid_path(quick_solver):
    """
    Ensures that a long, snake-like path (which inherently has 2 dead ends at all times)
    is NOT falsely pruned by the dead-end logic.
    """
    board = Board(size=3)
    # Create an S-shaped tunnel that forces a specific path
    board.addWall(Position(0, 1), Position(1, 1))
    board.addWall(Position(1, 1), Position(2, 1))
    
    result = quick_solver.solve(board)
    
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None