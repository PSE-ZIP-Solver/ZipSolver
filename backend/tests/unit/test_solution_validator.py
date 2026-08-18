import pytest
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position
from backend.solution_path import SolutionPath
from backend.solution_validator import SolutionValidator

@pytest.fixture
def validator():
    """
    Provisions a baseline validation gateway natively for isolated architectural testing loops.

    Returns:
        A completely fresh, fully stateless instance of the overarching domain rule evaluator.

    Implementation Details:
        Instantiates the strict mathematical verification engine securely without dependencies, 
        providing an absolutely pristine topological verifier natively for subsequent edge cases.
    """
    return SolutionValidator()

@pytest.fixture
def board_2x2():
    """
    Constructs a structurally minimal configuration specifically designed for boundary evaluations.

    Returns:
        The pre-configured, microscopically constrained domain baseline blueprint.

    Implementation Details:
        Allocates a strictly bounded two-by-two dimensional state natively. Securely populates 
        the topology with two mathematically sequential waypoints securely mapped to explicit coordinates 
        to ensure purely functional endpoints without overarching complexities.
    """
    # A 2x2 board has 4 cells in total
    board = Board(2)
    board.addWaypoint(Position(0, 0), 1)
    board.addWaypoint(Position(0, 1), 2)
    return board

@pytest.fixture
def empty_path():
    """
    Yields an entirely unpopulated spatial trajectory wrapper for null-state assertions.

    Returns:
        An instantiated path structure housing exactly zero navigational nodes.

    Implementation Details:
        Simply initializes the primary trajectory model natively without triggering any positional appending, 
        securely verifying early architectural short-circuit operations cleanly.
    """
    return SolutionPath()

@pytest.fixture
def valid_path_2x2():
    """
    Constructs a flawless, fully compliant trajectory natively traversing the minimal grid structure.

    Returns:
        A completely validated sequence perfectly exhausting localized spatial constraints natively.

    Implementation Details:
        Directly strings together an uncorrupted sequence of coordinates covering all theoretical quadrants. 
        Defensively adheres to all physical adjacency laws, preventing diagnostic failure loops on foundational tests.
    """
    # A completely valid path for a 2x2 board (covers all 4 cells exactly once, valid adjacent moves)
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 0))
    path.add(Position(1, 1))
    path.add(Position(0, 1))
    return path

@pytest.fixture
def invalid_length_path():
    """
    Synthesizes a structurally deficient navigational trace lacking necessary volumetric components.

    Returns:
        An incomplete sequential layout intentionally crafted to trigger absolute mathematical bounds failures.

    Implementation Details:
        Aggregates sequential points accurately but securely omits the absolute final coordinate natively, 
        resulting in an unresolved spatial layout guaranteed to provoke volumetric validation mismatches.
    """
    # Path with only 3 positions (fails length check for 2x2 board)
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 0))
    path.add(Position(0, 1))
    return path

@pytest.fixture
def rule_violating_path():
    """
    Assembles a mathematically flawed trajectory specifically designed to violate absolute traversal physics.

    Returns:
        A structurally complete but inherently impossible layout sequence.

    Implementation Details:
        Securely fulfills maximum volumetric limits perfectly, but natively implements an explicitly illegal 
        diagonal shift directly between nodes. This unequivocally trips strict internal state machines evaluating 
        absolute contiguous connections.
    """
    # Has correct length (4) but contains an invalid move (diagonal jump from (0,0) to (1,1))
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 1))  # Invalid adjacency
    path.add(Position(1, 0))
    path.add(Position(0, 1))
    return path


# --- Tests for _checkPathExists ---

def test_check_path_exists_with_none(validator):
    """
    Guarantees structural short-circuiting natively triggers when no underlying structure is injected.

    Args:
        validator: The stateless evaluation engine actively processing the request.

    Implementation Details:
        Bypasses standard wrappers and feeds a pure internal system constant securely into the private 
        existence verifier. Definitively asserts that the engine catches and correctly falsifies the 
        pure vacuum natively.
    """
    assert validator._checkPathExists(None) is False

def test_check_path_exists_with_empty_path(validator, empty_path):
    """
    Ensures that formally instantiated but entirely empty sequence structures correctly fail initial viability thresholds.

    Args:
        validator: The stateless evaluation engine executing boundary constraints.
        empty_path: The completely untraversed structural tracker natively yielding a volume of zero.

    Implementation Details:
        Directly routes the empty tracking model natively into the structural threshold checker, 
        asserting that mathematically barren arrays inherently resolve as functionally invalid natively.
    """
    assert validator._checkPathExists(empty_path) is False

def test_check_path_exists_with_valid_path(validator, valid_path_2x2):
    """
    Verifies the preliminary existence validation phase securely successfully acknowledges physically populated layouts.

    Args:
        validator: The stateless evaluation engine executing boundary constraints.
        valid_path_2x2: The securely structured target natively containing appropriate positional volume.

    Implementation Details:
        Funnels a fully constructed and populated domain sequence directly into the base existence checker, 
        asserting that strictly non-zero node structures appropriately trigger absolute true boolean returns.
    """
    assert validator._checkPathExists(valid_path_2x2) is True


# --- Tests for _checkPathLength ---

def test_check_path_length_correct(validator, board_2x2, valid_path_2x2):
    """
    Confirms the internal volume verifier successfully acknowledges arrays perfectly matching theoretical capacities.

    Args:
        validator: The stateless evaluation engine conducting absolute volumetric constraints.
        board_2x2: The strictly confined baseline domain representing maximum topological ceilings.
        valid_path_2x2: The sequence array natively holding an exact corresponding node count.

    Implementation Details:
        Computes the target layout constraints definitively and natively compares the absolute sequence length. 
        Asserts absolute parity strictly clears the isolated structural verifier loop safely.
    """
    # Board has 4 cells, path has 4 positions
    assert validator._checkPathLength(board_2x2, valid_path_2x2) is True

def test_check_path_length_incorrect(validator, board_2x2, invalid_length_path):
    """
    Validates that trajectories explicitly falling below strict volumetric thresholds are safely intercepted natively.

    Args:
        validator: The targeted evaluation engine analyzing dimensional properties.
        board_2x2: The constrained baseline environment demanding maximum total coverage.
        invalid_length_path: The functionally stunted sequence intentionally devoid of complete spatial parity.

    Implementation Details:
        Submits the partially completed array strictly into the volume verification phase, verifying 
        that exact inequalities natively cause immediate structural termination responses.
    """
    # Board has 4 cells, path has 3 positions
    assert validator._checkPathLength(board_2x2, invalid_length_path) is False

def test_check_path_length_with_empty_path(validator, board_2x2, empty_path):
    """
    Ensures entirely absent sequence arrays gracefully safely collapse without triggering computational exceptions.

    Args:
        validator: The mathematical evaluation engine managing bounds.
        board_2x2: The structured target expecting massive internal traversal capacities.
        empty_path: The strictly unoccupied wrapper actively mapped to zero nodes natively.

    Implementation Details:
        Defensively routes zero-capacity sequences into the exact mathematical validator natively, 
        securing evidence that empty iterables securely cleanly fail evaluations without breaking 
        the underlying execution loop.
    """
    # Empty paths should naturally fail the length check safely
    assert validator._checkPathLength(board_2x2, empty_path) is False


# --- Tests for validate() ---

def test_validate_path_is_none(validator, board_2x2):
    """
    Verifies that the overarching validation pipeline severely rigidly intercepts wholly undefined payloads natively.

    Args:
        validator: The primary state-verification orchestrator processing external resolutions natively.
        board_2x2: The targeted topological constraint map serving as truth.

    Implementation Details:
        Circumvents object instantiation safely and securely dumps primitive empty states natively into 
        the top-level public interface. Comprehensively evaluates the returned granular error wrapper to exactly 
        confirm the resulting payload properly explicitly targets an unrecoverable structural absence code natively.
    """
    result = validator.validate(board_2x2, None)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "PATH_EMPTY"
    assert result.getErrors[0].getAffectedField == "path"

def test_validate_path_empty(validator, board_2x2, empty_path):
    """
    Validates that instantiated but entirely bare tracking sequences accurately trip early validation short-circuits.

    Args:
        validator: The overarching validation module processing spatial compliance natively.
        board_2x2: The rigid mathematical layout domain model.
        empty_path: The cleanly initialized but volumetrically barren trajectory container.

    Implementation Details:
        Submits zero-volume configurations cleanly through the public architectural interface natively. 
        Asserts that the strict cascade correctly aborts at the preliminary state, aggressively yielding an 
        exactly targeted granular failure package securely bypassing heavy node mathematics entirely.
    """
    result = validator.validate(board_2x2, empty_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "PATH_EMPTY"

def test_validate_invalid_length(validator, board_2x2, invalid_length_path):
    """
    Checks that spatially incomplete trajectories natively trigger targeted mathematical disparity warnings.

    Args:
        validator: The overarching architectural validation engine governing adherence.
        board_2x2: The fundamental reference map dictating structural minimums natively.
        invalid_length_path: The purposefully shortened spatial model lacking volumetric fulfillment.

    Implementation Details:
        Injects the functionally truncated layout safely through the primary pipeline. Strictly targets 
        the internal properties of the emitted contextual failure array securely, confirming that the dynamic 
        error message successfully interpolates exactly both the active count and the absolutely required maximums natively.
    """
    result = validator.validate(board_2x2, invalid_length_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "INVALID_LENGTH"
    assert "3" in result.getErrors[0].getMessage  # Checks if actual length is in the error message
    assert "4" in result.getErrors[0].getMessage  # Checks if expected length is in the error message

def test_validate_rule_violation(validator, board_2x2, rule_violating_path):
    """
    Ensures that trajectories violating contiguous traversal logic securely yield rigorous mathematical failure constraints natively.

    Args:
        validator: The comprehensive internal pipeline evaluating spatial physics.
        board_2x2: The pristine environmental layout managing structural truth.
        rule_violating_path: The completely populated but theoretically impossible sequence containing illegal shifting.

    Implementation Details:
        Routes mathematically correct total volumes containing definitively corrupt sequential linkages safely 
        through the stateless engine. Asserts that the process strictly clears length hurdles natively but safely 
        collapses during deep sequential neighbor validations natively, reporting specifically the overarching bounds violation natively.
    """
    # The path length is correct (4), but it contains a diagonal jump which violates PuzzleRules
    result = validator.validate(board_2x2, rule_violating_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "RULE_VIOLATION"

def test_validate_success(validator, board_2x2, valid_path_2x2):
    """
    Verifies that wholly pristine trajectories securely navigate all cascading mathematical verifications flawlessly natively.

    Args:
        validator: The central verification subsystem governing all progression models.
        board_2x2: The rigid, fully confined environment testing baseline.
        valid_path_2x2: The exhaustively checked mathematical sequence cleanly traversing all bounds natively.

    Implementation Details:
        Executes a perfectly formed array correctly directly through the absolute core architecture. 
        Definitively asserts that strictly zero granular errors accumulate securely natively, and that the overarching 
        completion message correctly translates into a safely confirmed success metric output natively.
    """
    # A perfectly valid path on a 2x2 board
    result = validator.validate(board_2x2, valid_path_2x2)
    
    assert result.isValid is True
    assert len(result.getErrors) == 0
    assert result.getMessage == "Solution is fully valid."