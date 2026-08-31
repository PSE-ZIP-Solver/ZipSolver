import pytest
from backend.puzzle_logic import Board, Position
from offline_training.board_generator import BoardGenerator
# ==========================================
# Setup / Fixtures
# ==========================================

@pytest.fixture(autouse=True)
def setup_generator_results(monkeypatch):
    """
    Configures the testing environment by standardizing the output volume constraint for board generations.

    Args:
        monkeypatch: The active test environment fixture dynamically overriding module-level registries.

    Implementation Details:
        Targets the global threshold constant natively within the generator module and strictly forces 
        it to a static minimum. This defensively disables exhaustive combinatorial permutation runs 
        to mathematically guarantee swift, deterministic continuous integration workflows.
    """
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
    """
    Validates the overarching board generation orchestrator against standard spatial constraints.

    Args:
        size: The parameterized metric defining the exact topological bounds for the targeted generation run.

    Implementation Details:
        Initiates a standard architectural sequence utilizing moderate physical barrier and milestone configurations natively. 
        Asserts that definitively a single structurally sound domain model is synthesized natively, and strictly verifies 
        that its internal grid architecture exactly maps to the provided parameterized dimensional limit.
    """
    # Test with moderate waypoints and walls
    results = BoardGenerator.generate(size, 5, 5)
    
    assert len(results) == 1
    assert isinstance(results[0], Board)
    assert results[0].getSize == size


@pytest.mark.parametrize("size", [6, 7, 8])
def test_generate_two_distinct_random_positions(size):
    """
    Verifies that generated terminal coordinates strictly enforce spatial separation and parity rules.

    Args:
        size: The parameterized dimensional limit dictating overall layout capacities.

    Implementation Details:
        Evaluates the strict mathematical parity bounds mapping the topological checkerboard coloration 
        between the calculated origin and destination nodes natively. Secures that natively even-sized domains 
        guarantee completely mismatched parity outputs, whereas structurally odd-sized configurations rigidly 
        isolate terminal limits to the majority color layout to preserve absolutely unbroken Hamiltonian mechanics.
    """
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
    """
    Checks the deterministic pathfinding module's ability to synthetically generate mathematically perfect grid traversals.

    Implementation Details:
        Computes a raw positional array spanning an entirely unobstructed grid layout and strictly cross-references 
        its overall length natively against the maximum absolute volumetric capacity. Deduplicates the positional array 
        securely utilizing native casting implementations to definitively confirm perfectly zero-overlap physical coverage, 
        and validates that the absolute final coordinate maps strictly to the mandated topological terminal node.
    """
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
    """
    Evaluates algorithmic milestone assignment logic against absolute minimum and extreme boundary constraints.

    Implementation Details:
        Injects a completely contiguous mathematical baseline layout natively and evaluates the distribution limits. 
        Determines that a configuration requesting entirely zero intermediate milestones securely preserves the foundational 
        origin and terminal bounds, and definitively confirms that aggressively requesting constraints beyond maximum limits 
        seamlessly securely caps the total operational waypoints natively without overflowing the domain architecture.
    """
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
    """
    Validates that the physical barrier distribution system correctly mitigates mathematical overload conditions.

    Implementation Details:
        Triggers wall injection mechanisms leveraging structurally basic layouts. Initially securely evaluates a totally 
        barren topology target to guarantee uncorrupted origins. Subsequently executes an extreme overload scenario mapping 
        massively over-capacitated constraints natively, securely asserting that the resulting internal barrier tracking arrays 
        are definitively mathematically truncated directly below maximum possible thresholds natively, thus preventing complete 
        topological chokepoints.
    """
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
    """
    Confirms that synthesized progression milestones rigorously adopt strict sequentially ascending orders.

    Implementation Details:
        Constructs a completely predefined navigational trajectory and natively seeds multiple checkpoint components along it. 
        Sequentially isolates the internally attached waypoints natively by scanning their explicit mathematical property hooks, 
        and securely asserts an unbroken contiguous progression map. Recursively translates every discrete milestone back to 
        its raw coordinate index definitively to verify that spatial chronological alignment correctly never navigates in reverse.
    """
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