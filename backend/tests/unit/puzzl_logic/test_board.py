import pytest
from puzzle_logic.data_models import Position
from puzzle_logic.board import Board

@pytest.fixture
def board():
    """Provides a fresh 5x5 board for each test."""
    return Board(5)

# ==========================================
# Initialization & Properties
# ==========================================

def test_init_and_properties(board):
    assert board.getSize == 5
    assert board.getCellCount() == 25
    assert len(board.getWaypoints) == 0
    assert len(board.getWalls) == 0

# ==========================================
# Waypoints (Defaults, Multiples, and Conflicts)
# ==========================================

def test_add_multiple_waypoints(board):
    """Test adding and retrieving multiple waypoints."""
    p1 = Position(0, 0)
    p2 = Position(4, 4)
    p3 = Position(2, 2)
    
    board.addWaypoint(p1, 1)
    board.addWaypoint(p2, 2)
    board.addWaypoint(p3, 3)
    
    assert len(board.getWaypoints) == 3
    
    # Check specific retrievals from the populated list
    assert board.getWaypointAt(p2).getOrder == 2
    assert board.getWaypointByOrder(3).getPosition == p3

def test_waypoint_duplicate_edge_cases(board):
    """
    Edge Case: The code uses a List and returns the first match. 
    If duplicates are added, we must ensure it behaves predictably (returning the first).
    """
    p_conflict = Position(1, 1)
    
    board.addWaypoint(p_conflict, 1) # Inserted first
    board.addWaypoint(p_conflict, 2) # Same position, different order
    board.addWaypoint(Position(2, 2), 1) # Different position, same order
    
    assert len(board.getWaypoints) == 3
    
    # getWaypointAt should return the FIRST waypoint found at (1, 1), which has order 1
    assert board.getWaypointAt(p_conflict).getOrder == 1
    
    # getWaypointByOrder should return the FIRST waypoint found with order 1, which is at (1, 1)
    assert board.getWaypointByOrder(1).getPosition == p_conflict

def test_get_waypoint_not_found(board):
    """Edge Case: Retrieving from an empty board or missing values."""
    assert board.getWaypointAt(Position(0, 0)) is None
    assert board.getWaypointByOrder(1) is None
    
    board.addWaypoint(Position(2, 2), 2)
    assert board.getWaypointAt(Position(3, 3)) is None
    assert board.getWaypointByOrder(99) is None

# ==========================================
# Walls
# ==========================================

def test_add_multiple_walls_and_duplicate_edge_case(board):
    posA, posB = Position(0, 0), Position(0, 1)
    posC, posD = Position(2, 2), Position(2, 3)
    
    board.addWall(posA, posB)
    board.addWall(posC, posD)
    assert len(board.getWalls) == 2
    
    # Edge case: Adding duplicate (reversed) wall should be ignored by the Set
    board.addWall(posB, posA)
    assert len(board.getWalls) == 2

def test_has_wall_between(board):
    p1, p2, p3 = Position(1, 1), Position(1, 2), Position(2, 1)
    
    # Edge case: Empty board
    assert not board.hasWallBetween(p1, p2)
    
    board.addWall(p1, p2)
    
    # True positives
    assert board.hasWallBetween(p1, p2)
    assert board.hasWallBetween(p2, p1) # Reversed check
    
    # True negatives
    assert not board.hasWallBetween(p1, p3) # Adjacent but no wall
    assert not board.hasWallBetween(p1, Position(4, 4)) # Not adjacent

# ==========================================
# Geometry & Bounds (isInside, areAdjacent, getAllPositions)
# ==========================================

def test_is_inside(board):
    # True positives
    assert board.isInside(Position(0, 0))
    assert board.isInside(Position(4, 4))
    
    # True negatives (OOB)
    assert not board.isInside(Position(-1, 0))
    assert not board.isInside(Position(0, -1))
    assert not board.isInside(Position(5, 0))
    assert not board.isInside(Position(0, 5))

def test_are_adjacent(board):
    center = Position(2, 2)
    up, down = Position(2, 1), Position(2, 3)
    left, right = Position(1, 2), Position(3, 2)
    
    # True positives
    assert board.areAdjacent(center, up)
    assert board.areAdjacent(center, down)
    assert board.areAdjacent(center, left)
    assert board.areAdjacent(center, right)
    
    # True negatives
    assert not board.areAdjacent(center, Position(3, 3))   # Diagonal
    assert not board.areAdjacent(center, center)           # Same cell
    assert not board.areAdjacent(center, Position(2, 4))   # Distance 2

def test_are_adjacent_out_of_bounds_edge_case(board):
    """
    Edge case: Adjacency is purely mathematical (Manhattan distance).
    It should return True even if coordinates are negative or larger than board size.
    """
    p_edge = Position(0, 0)
    p_off_board = Position(-1, 0)
    
    assert board.areAdjacent(p_edge, p_off_board)

def test_get_all_positions(board):
    positions = board.getAllPositions()
    
    assert len(positions) == 25
    assert Position(0, 0) in positions
    assert Position(4, 4) in positions
    assert Position(5, 5) not in positions

# ==========================================
# Extreme Edge Cases
# ==========================================

def test_edge_case_zero_size_board():
    """Test behavior if an empty board (size 0) is created."""
    zero_board = Board(0)
    
    assert zero_board.getSize == 0
    assert zero_board.getCellCount() == 0
    assert len(zero_board.getAllPositions()) == 0
    assert not zero_board.isInside(Position(0, 0))

def test_edge_case_negative_size_board():
    """Test behavior if a negative size board is created."""
    neg_board = Board(-5)
    
    assert neg_board.getSize == -5
    assert neg_board.getCellCount() == 25 # -5 * -5 = 25 (mathematical quirk)
    
    # range(-5) is empty in python, so getAllPositions will be empty
    assert len(neg_board.getAllPositions()) == 0 
    
    # 0 <= x < -5 is always false
    assert not neg_board.isInside(Position(0, 0))