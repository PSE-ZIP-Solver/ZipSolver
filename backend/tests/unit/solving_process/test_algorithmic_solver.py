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
    using the provided SolutionPath.getPositions property.
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
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert result._metrics._steps > 0
    assert verify_valid_hamiltonian_path(empty_3x3_board, result._path)

def test_solve_with_walls(quick_solver):
    board = Board(size=3)
    board.addWall(Position(0, 0), Position(0, 1))
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)

def test_solve_with_waypoints(quick_solver):
    board = Board(size=3)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(2, 2), 2)
    board.addWaypoint(Position(0, 2), 3)
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)


# --- Tests: Edge Cases & Optimizations ---

def test_start_on_waypoint(quick_solver):
    board = Board(size=2)
    board.addWaypoint(Position(0, 0), 1)
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert verify_valid_hamiltonian_path(board, result._path)

def test_1x1_board(quick_solver):
    board = Board(size=1)
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None
    assert result._metrics._steps >= 0
    assert verify_valid_hamiltonian_path(board, result._path)

def test_unsolvable_board_isolated_cell(quick_solver):
    board = Board(size=2)
    board.addWall(Position(0, 0), Position(0, 1))
    board.addWall(Position(0, 0), Position(1, 0))
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None
    assert result._metrics._steps > 0

def test_unsolvable_impossible_waypoints(quick_solver):
    board = Board(size=2)
    # Block the direct path to force a specific route
    board.addWall(Position(0, 0), Position(1, 0))
    
    # By forcing the path to go (0,0) -> (0,1) -> (1,1) -> (1,0),
    # placing a later waypoint earlier in the physical path makes it mathematically impossible.
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(1, 1), 2)
    board.addWaypoint(Position(0, 1), 3) # Hits WP 3 before WP 2!
    
    result = quick_solver.solve(board)
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert result._path is None

def test_flood_fill_pruning_trigger(quick_solver):
    """
    A 3x3 board completely divided into two disconnected halves.
    This safely bypasses the >2 dead-end check (exactly 2 dead ends),
    forcing the Flood-Fill to correctly identify the disconnected graph and prune it.
    """
    board = Board(size=3)
    board.addWall(Position(0, 1), Position(0, 2))
    board.addWall(Position(1, 1), Position(1, 2))
    board.addWall(Position(2, 1), Position(2, 2))
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Should be nearly instant due to flood fill pruning

def test_solver_timeout(timeout_solver):
    large_board = Board(size=6) 
    
    result = timeout_solver.solve(large_board)
    
    assert result._status == SolverStatus.TIMEOUT
    assert result._path is None
    assert result._metrics._runtimeMs >= 0

def test_zero_timeout_edge_case():
    solver = AlgorithmicSolver(timeout=0)
    board = Board(size=3)
    
    result = solver.solve(board)
    
    assert result._status == SolverStatus.TIMEOUT
    assert result._path is None

def test_heuristic_logic(quick_solver):
    board = Board(size=5)
    board.addWaypoint(Position(4, 4), 1)
    waypoints = board.getWaypoints
    
    # Heuristic calculates distance to Waypoint. 0,0 to 4,4 is 8.
    distance = quick_solver._heuristic(Position(0, 0), waypoints, 0)
    assert distance == 8

    distance_done = quick_solver._heuristic(Position(0, 0), waypoints, 1)
    assert distance_done == 0

def test_dead_end_pruning_trigger(quick_solver):
    """
    Tests the Dead-End degree-1 pruning logic.
    A board that is technically connected, but forces THREE dead-ends, 
    making a Hamiltonian path mathematically impossible.
    """
    board = Board(size=3)
    board.addWall(Position(0, 0), Position(1, 0)) # Isolates 0,0 to only go down
    board.addWall(Position(2, 0), Position(1, 0)) # Isolates 2,0 to only go down
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result._status == SolverStatus.UNSOLVABLE
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
    Verifies the > 2 dead-end constraint explicitly.
    Creates 3 cells that only have exactly 1 entrance/exit. 
    """
    board = Board(size=3)
    
    # Isolate Top-Left (0,0) to only exit via (1,0)
    board.addWall(Position(0, 0), Position(0, 1))
    
    # Isolate Bottom-Left (0,2) to only exit via (1,2)
    board.addWall(Position(0, 2), Position(0, 1))
    
    # Isolate Top-Right (2,0) to only exit via (1,0)
    board.addWall(Position(2, 0), Position(2, 1))
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result._status == SolverStatus.UNSOLVABLE
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
    
    assert result._status == SolverStatus.SOLVED
    assert result._path is not None

def test_heuristic_subgoal_consistency(quick_solver):
    """
    Tests if the heuristic correctly accounts for subsequent waypoints.
    If the heuristic drops to 0 when reaching WP1 while WP2 is far away,
    A* will stall. This ensures 'h' calculates total remaining path consistency.
    """
    board = Board(size=5)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(4, 4), 2)
    waypoints = sorted(board.getWaypoints, key=lambda w: w.getOrder)
    
    # Distance to WP1 (0,0) is 1. Distance from WP1 to WP2 (4,4) is 8.
    # Total heuristic MUST equal 9 to prevent queue stalling.
    h_start = quick_solver._heuristic(Position(0, 1), waypoints, 0)
    assert h_start == 9

def test_fully_walled_unreachable_target(quick_solver):
    """
    A board where the remaining unvisited cells are entirely split into 
    TWO disconnected groups. The Flood-fill MUST instantly flag this.
    """
    board = Board(size=3)
    # Wall off the top-right corner entirely
    board.addWall(Position(2, 0), Position(1, 0))
    board.addWall(Position(2, 0), Position(2, 1))
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result._status == SolverStatus.UNSOLVABLE
    assert duration < 0.2  # Ensures flood-fill caught it instantly

def test_bit_count_large_board_performance(quick_solver):
    """
    Ensures that the string-allocation garbage collection bug is fixed.
    An empty 4x4 board should be solved blazingly fast if .bit_count() is used,
    but would heavily lag if bin().count() was still in the A* loop.
    """
    board = Board(size=4)
    
    start = time.perf_counter()
    result = quick_solver.solve(board)
    duration = time.perf_counter() - start
    
    assert result._status == SolverStatus.SOLVED
    assert duration < 0.5  # High performance assertion