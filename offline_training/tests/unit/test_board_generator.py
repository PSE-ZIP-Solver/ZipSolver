import pytest
from backend.puzzle_logic import Board, Position
from offline_training.board_generator import BoardGenerator

# ==========================================
# Setup / Fixtures
# ==========================================

@pytest.fixture(autouse=True)
def setup_generator_results(monkeypatch):
    """
    This fixture automatically runs before every test.
    It safely overrides the global RESULTS constant in the BoardGenerator 
    module to 1 to ensure tests run fast, restoring it after the test.
    """
    monkeypatch.setattr('offline_training.board_generator.RESULTS', 1)

# ==========================================
# Tests
# ==========================================

@pytest.mark.parametrize("size", [6, 7, 8])
def test_generate(size):
    """Tests the main entry point for different sizes and basic constraints."""
    # Test with moderate waypoints and walls
    results = BoardGenerator.generate(size, 5, 5)
    
    assert len(results) == 1
    assert isinstance(results[0], Board)
    assert results[0].getSize == size


@pytest.mark.parametrize("size", [6, 7, 8])
def test_generate_two_distinct_random_positions(size):
    """Tests _generateTwoDistinctRandomPositions logic and parity."""
    start, end = BoardGenerator._generateTwoDistinctRandomPositions(size)
    
    assert start != end
    
    p_start = (start.getX + start.getY) % 2
    p_end = (end.getX + end.getY) % 2
    
    if size % 2 == 0:
        # Even: different parity
        assert p_start != p_end
    else:
        # Odd: both must be parity 0 (majority color)
        assert p_start == 0
        assert p_end == 0


def test_find_hamiltonian_path():
    """Tests if the path visits every cell exactly once."""
    size = 6
    board = Board(size)
    start, end = BoardGenerator._generateTwoDistinctRandomPositions(size)
    path = BoardGenerator._findHamiltonianPath(board, start, end)
    
    assert path is not None
    assert len(path) == size * size
    
    # Check for uniqueness using the class's built-in __hash__
    assert len(set(path)) == size * size
    assert path[-1] == end


def test_edge_cases_place_random_waypoints():
    """Tests _placeRandomWaypoints with 0 and max waypoints."""
    size = 6
    board = Board(size)
    path = [Position(x, 0) for x in range(size)] 
    
    # 0 intermediate waypoints -> 2 total (Start/End)
    BoardGenerator._placeRandomWaypoints(board, path, 0)
    assert len(board.getWaypoints) == 2

    # Max waypoints -> All cells in path become waypoints
    board_max = Board(size)
    BoardGenerator._placeRandomWaypoints(board_max, path, 1000) 
    assert len(board_max.getWaypoints) == len(path)


def test_place_random_walls():
    """Tests _placeRandomWalls with 0 and unrealistic wall counts."""
    size = 6
    board = Board(size)
    path = [Position(0, 0), Position(1, 0)]
    
    # 0 walls
    BoardGenerator._placeRandomWalls(board, path, 0)
    assert len(board.getWalls) == 0

    # Excess walls (should be capped safely)
    BoardGenerator._placeRandomWalls(board, path, 500)
    max_possible = (2 * size * (size - 1)) - (len(path) - 1)
    assert len(board.getWalls) <= max_possible


def test_waypoint_ordering():
    """Verifies waypoints are in ascending order relative to the path sequence."""
    size = 6
    board = Board(size)
    path = [Position(0,0), Position(1,0), Position(1,1), Position(0,1), Position(0,2)]
    
    BoardGenerator._placeRandomWaypoints(board, path, 2)
    wps = sorted(board.getWaypoints, key=lambda w: w.getOrder)
    
    # Verify continuous ordering (1, 2, 3...)
    for i, wp in enumerate(wps):
        assert wp.getOrder == i + 1

    # Verify path sequence
    for i in range(len(wps) - 1):
        idx_curr = path.index(wps[i].getPosition)
        idx_next = path.index(wps[i+1].getPosition)
        assert idx_curr < idx_next
