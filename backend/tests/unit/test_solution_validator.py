import pytest
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position
from backend.solution_path import SolutionPath
from backend.solution_validator import SolutionValidator

@pytest.fixture
def validator():
    return SolutionValidator()

@pytest.fixture
def board_2x2():
    # A 2x2 board has 4 cells in total
    return Board(size=2)

@pytest.fixture
def empty_path():
    return SolutionPath()

@pytest.fixture
def valid_path_2x2():
    # A completely valid path for a 2x2 board (covers all 4 cells exactly once, valid adjacent moves)
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 0))
    path.add(Position(1, 1))
    path.add(Position(0, 1))
    return path

@pytest.fixture
def invalid_length_path():
    # Path with only 3 positions (fails length check for 2x2 board)
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 0))
    path.add(Position(0, 1))
    return path

@pytest.fixture
def rule_violating_path():
    # Has correct length (4) but contains an invalid move (diagonal jump from (0,0) to (1,1))
    path = SolutionPath()
    path.add(Position(0, 0))
    path.add(Position(1, 1))  # Invalid adjacency
    path.add(Position(1, 0))
    path.add(Position(0, 1))
    return path


# --- Tests for _checkPathExists ---

def test_check_path_exists_with_none(validator):
    assert validator._checkPathExists(None) is False

def test_check_path_exists_with_empty_path(validator, empty_path):
    assert validator._checkPathExists(empty_path) is False

def test_check_path_exists_with_valid_path(validator, valid_path_2x2):
    assert validator._checkPathExists(valid_path_2x2) is True


# --- Tests for _checkPathLength ---

def test_check_path_length_correct(validator, board_2x2, valid_path_2x2):
    # Board has 4 cells, path has 4 positions
    assert validator._checkPathLength(board_2x2, valid_path_2x2) is True

def test_check_path_length_incorrect(validator, board_2x2, invalid_length_path):
    # Board has 4 cells, path has 3 positions
    assert validator._checkPathLength(board_2x2, invalid_length_path) is False

def test_check_path_length_with_empty_path(validator, board_2x2, empty_path):
    # Empty paths should naturally fail the length check safely
    assert validator._checkPathLength(board_2x2, empty_path) is False


# --- Tests for validate() ---

def test_validate_path_is_none(validator, board_2x2):
    result = validator.validate(board_2x2, None)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "PATH_EMPTY"
    assert result.getErrors[0].getAffectedField == "path"

def test_validate_path_empty(validator, board_2x2, empty_path):
    result = validator.validate(board_2x2, empty_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "PATH_EMPTY"

def test_validate_invalid_length(validator, board_2x2, invalid_length_path):
    result = validator.validate(board_2x2, invalid_length_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "INVALID_LENGTH"
    assert "3" in result.getErrors[0].getMessage  # Checks if actual length is in the error message
    assert "4" in result.getErrors[0].getMessage  # Checks if expected length is in the error message

def test_validate_rule_violation(validator, board_2x2, rule_violating_path):
    # The path length is correct (4), but it contains a diagonal jump which violates PuzzleRules
    result = validator.validate(board_2x2, rule_violating_path)
    
    assert result.isValid is False
    assert len(result.getErrors) == 1
    assert result.getErrors[0].getErrorCode == "RULE_VIOLATION"

def test_validate_success(validator, board_2x2, valid_path_2x2):
    # A perfectly valid path on a 2x2 board
    result = validator.validate(board_2x2, valid_path_2x2)
    
    assert result.isValid is True
    assert len(result.getErrors) == 0
    assert result.getMessage == "Solution is fully valid."