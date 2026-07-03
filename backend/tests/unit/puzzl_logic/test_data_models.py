import pytest
from backend.puzzle_logic.data_models import Position, Wall, Waypoint
# ==========================================
# Tests for Position
# ==========================================

def test_position_init_and_properties():
    # Default use case
    pos = Position(3, 4)
    assert pos.getX == 3
    assert pos.getY == 4

    # Edge case: Negative coordinates
    neg_pos = Position(-1, -99)
    assert neg_pos.getX == -1
    assert neg_pos.getY == -99

# TODO remove entirely
# def test_position_setters():
#    pos = Position(0, 0)
#    pos.setX(10)
#    pos.setY(-5)
#    assert pos.getX == 10
#    assert pos.getY == -5

def test_position_equality():
    pos1 = Position(5, 10)
    pos2 = Position(5, 10)
    pos3 = Position(1, 10)  # Different X
    pos4 = Position(5, 11)  # Different Y
    
    # True positive
    assert pos1 == pos2
    
    # True negatives
    assert pos1 != pos3
    assert pos1 != pos4
    
    # Type mismatch edge cases
    assert pos1 != "(5, 10)"
    assert pos1 is not None

def test_position_hash():
    pos1 = Position(2, 2)
    pos2 = Position(2, 2)
    pos3 = Position(3, 3)
    
    # Equal objects must have equal hashes
    assert hash(pos1) == hash(pos2)
    
    unique_positions = {pos1, pos2, pos3}
    assert len(unique_positions) == 2


# ==========================================
# Tests for Waypoint
# ==========================================

def test_waypoint_init_and_properties():
    pos = Position(1, 1)
    waypoint = Waypoint(pos, 5)
    
    assert waypoint.getPosition == pos
    assert waypoint.getOrder == 5


# ==========================================
# Tests for Wall
# ==========================================

@pytest.fixture
def positions():
    """
    A pytest fixture that provides a dictionary of common Position objects 
    to be used by any test that requests 'positions' as a parameter.
    """
    return {
        'A': Position(0, 0),
        'B': Position(0, 1),
        'C': Position(1, 0),
        'D': Position(1, 1)
    }

def test_wall_init_and_properties(positions):
    wall = Wall(positions['A'], positions['B'])
    assert wall.getCellA == positions['A']
    assert wall.getCellB == positions['B']

def test_wall_connects(positions):
    wall = Wall(positions['A'], positions['B'])
    
    # True positives
    assert wall.connects(positions['A'], positions['B'])
    assert wall.connects(positions['B'], positions['A'])
    
    # True negatives
    assert not wall.connects(positions['A'], positions['C']) # Shares one node, but wrong
    assert not wall.connects(positions['C'], positions['D']) # Completely unrelated nodes
    assert not wall.connects(positions['A'], positions['A']) # Same node twice

def test_wall_equality(positions):
    wall1 = Wall(positions['A'], positions['B'])
    wall2 = Wall(positions['A'], positions['B'])
    wall3_reversed = Wall(positions['B'], positions['A'])
    wall4_different = Wall(positions['A'], positions['C'])
    
    assert wall1 == wall2
    assert wall1 == wall3_reversed
    
    # True negative
    assert wall1 != wall4_different
    assert wall1 != positions['A']
    assert wall1 is not None

def test_wall_hash(positions):
    wall1 = Wall(positions['A'], positions['B'])
    wall2_reversed = Wall(positions['B'], positions['A'])
    
    assert hash(wall1) == hash(wall2_reversed)
    
    unique_walls = {wall1, wall2_reversed}
    assert len(unique_walls) == 1