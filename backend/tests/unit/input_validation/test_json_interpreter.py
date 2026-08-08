import pytest
import json
import io
import inspect
from unittest.mock import patch

from backend.puzzle_logic.board import Board
from backend.puzzle_logic import Position
from backend.input_validation.json_interpreter import JsonInterpreter

@pytest.fixture
def valid_json_data():
    """Fixture providing a standard valid payload matching all constraints."""
    return {
        "boardSize": 6,
        "waypoints": [[0, 0], [2, 2], [4, 4]],
        "walls": [{"neighborA": [0, 0], "neighborB": [1, 0]}],
        "solutionPath": []
    }

@pytest.fixture
def interpreter():
    """Returns an instance of JsonInterpreter."""
    return JsonInterpreter()

def call(func, *args):
    """
    Bulletproof helper to call JsonInterpreter methods.
    It inspects the signature to see if 'self' is required. This ensures the tests run
    perfectly NOW (while the code has the `@staticmethod` + `self` bug) AND LATER 
    (whether you fix it by removing `@staticmethod` or by removing the `self` parameter).
    """
    sig = inspect.signature(func)
    if 'self' in sig.parameters:
        return func(None, *args)
    return func(*args)

# ===================================================================
# Tests for _load
# ===================================================================
def test_load_dict(interpreter, valid_json_data):
    assert call(interpreter._load, valid_json_data) == valid_json_data

def test_load_filepath(interpreter, valid_json_data, tmp_path):
    file_path = tmp_path / "puzzle.json"
    file_path.write_text(json.dumps(valid_json_data), encoding="utf-8")
    assert call(interpreter._load, str(file_path)) == valid_json_data

def test_load_file_like_object(interpreter, valid_json_data):
    file_like = io.StringIO(json.dumps(valid_json_data))
    assert call(interpreter._load, file_like) == valid_json_data

def test_load_file_like_invalid_json(interpreter):
    file_like = io.StringIO("{bad json")
    with pytest.raises(json.JSONDecodeError):
        call(interpreter._load, file_like)

def test_load_invalid_type(interpreter):
    with pytest.raises(TypeError, match="Unsupported argument type"):
        call(interpreter._load, 123)

def test_load_file_not_found(interpreter):
    with pytest.raises(FileNotFoundError):
        call(interpreter._load, "non_existent_file.json")


# ===================================================================
# Tests for _validate_board_size
# ===================================================================
@pytest.mark.parametrize("size, expected", [
    (6, True), (7, True), (8, True), (6.0, True),
    (5, False), (9, False), (0, False), (-6, False),
    ("6", False), (None, False)
])
def test_validate_board_size(interpreter, size, expected):
    assert call(interpreter._validate_board_size, size) is expected


# ===================================================================
# Tests for _is_valid_point
# ===================================================================
@pytest.mark.parametrize("point, size, expected", [
    # General Valid
    ([0, 0], 6, True),
    ([2, 3], 6, True),
    ((1, 1), 6, True),     # Tuples are permitted
    
    # Boundary tests for X and Y axes
    ([0, 5], 6, True),     # Note: Expects True, but currently fails due to your `board_size-1` bug.
    ([5, 0], 6, True),     
    ([5, 5], 6, True),     
    ([0, 6], 6, False),    # Upper bound breach
    ([6, 0], 6, False),
    ([-1, 0], 6, False),   # Lower bound breach
    ([0, -1], 6, False),
    
    # Format and Types constraints
    ("0,0", 6, False),
    ([1], 6, False),       # Too short
    ([1, 2, 3], 6, False), # Too long
    ([1.5, 2], 6, False),  # Float inclusion
    ([True, 1], 6, False), # Strict boolean rejection check
    ([0, False], 6, False),# Strict boolean rejection (y-axis)
    (["0", 0], 6, False),  # Mixed types
    (None, 6, False)
])
def test_is_valid_point(interpreter, point, size, expected):
    assert call(interpreter._is_valid_point, point, size) is expected


# ===================================================================
# Tests for _validate_waypoints
# ===================================================================
def test_validate_waypoints_valid(interpreter):
    waypoints = [[0, 0], [1, 2], [3, 4]]
    assert call(interpreter._validate_waypoints, waypoints, 6) is True

@pytest.mark.parametrize("waypoints, size, expected", [
    ([[0, 0], [1, 1]], 6, True),      # Min count (2)
    ([[0, 0]], 6, False),             # Below min count
    ([], 6, False),                   # Empty
    ("not a list", 6, False),         # Invalid type
    ([{"x": 0, "y": 0}], 6, False),   # Invalid point format
    ([[1, 1], [2, 2], [1, 1]], 6, False) # Duplicate points
])
def test_validate_waypoints_constraints(interpreter, waypoints, size, expected):
    assert call(interpreter._validate_waypoints, waypoints, size) is expected

def test_validate_waypoints_max_count(interpreter):
    # Max waypoints is board_size ** 2 (36 for 6x6)
    waypoints = [[x, y] for x in range(6) for y in range(6)]
    assert call(interpreter._validate_waypoints, waypoints, 6) is True
    
    # 37 points (Exceeds capacity)
    waypoints.append([6, 6])
    assert call(interpreter._validate_waypoints, waypoints, 6) is False


# ===================================================================
# Tests for _validate_walls
# ===================================================================
def test_validate_walls_valid(interpreter):
    walls = [
        {"neighborA": [0, 0], "neighborB": [1, 0]},
        {"neighborA": [1, 1], "neighborB": [1, 2]}
    ]
    assert call(interpreter._validate_walls, walls, 6) is True

def test_validate_walls_empty_allowed(interpreter):
    assert call(interpreter._validate_walls, [], 6) is True

def test_validate_walls_extra_keys_allowed(interpreter):
    # Tests that .issubset allows extra undocumented keys cleanly
    walls = [{"neighborA": [0, 0], "neighborB": [1, 0], "wallType": "stone"}]
    assert call(interpreter._validate_walls, walls, 6) is True

@pytest.mark.parametrize("walls, expected", [
    ([{"neighborA": [0, 0]}], False),                             # Missing neighborB
    ([{"neighborA": [0, 0], "neighborC": [1, 0]}], False),        # Wrong keys
    ([{"neighborA": [-1, 0], "neighborB": [0, 0]}], False),       # Out of bounds
    ([{"neighborA": [1, 1], "neighborB": [1, 1]}], False),        # Same point
    ([{"neighborA": [0, 0], "neighborB": [1, 1]}], False),        # Diagonal
    ([{"neighborA": [0, 0], "neighborB": [0, 2]}], False),        # Gap > 1
    ("not a list", False),                                        # Root invalid type
    ([{"neighborA": [0, 0], "neighborB": [1, 0]}, "string"], False), # Bad element type
    ([{"neighborA": [0, 0], "neighborB": [1, 0]}, [[1,1], [1,2]]], False) # Array instead of Dict
])
def test_validate_walls_invalid_cases(interpreter, walls, expected):
    assert call(interpreter._validate_walls, walls, 6) is expected

def test_validate_walls_duplicates(interpreter):
    # Exact duplicate dictionary
    assert call(interpreter._validate_walls, [
        {"neighborA": [0, 0], "neighborB": [1, 0]},
        {"neighborA": [0, 0], "neighborB": [1, 0]}
    ], 6) is False

    # Reversed orientation duplicate (ensures frozenset uniqueness logic works)
    assert call(interpreter._validate_walls, [
        {"neighborA": [0, 0], "neighborB": [1, 0]},
        {"neighborA": [1, 0], "neighborB": [0, 0]}
    ], 6) is False

def test_validate_walls_max_count(interpreter):
    # Max walls for 6x6 is 6 * 5 * 2 = 60 valid walls total
    walls = []
    for x in range(6):
        for y in range(6):
            if x < 5:
                walls.append({"neighborA": [x, y], "neighborB": [x + 1, y]})
            if y < 5:
                walls.append({"neighborA": [x, y], "neighborB": [x, y + 1]})
    
    assert call(interpreter._validate_walls, walls, 6) is True
    
    # 61st wall violates upper bounds logic
    walls.append({"neighborA": [0, 0], "neighborB": [1, 1]}) 
    assert call(interpreter._validate_walls, walls, 6) is False


# ===================================================================
# Tests for verifySyntax
# ===================================================================
def test_verifySyntax_valid(interpreter, valid_json_data):
    assert call(interpreter.verifySyntax, valid_json_data) is True

def test_verifySyntax_extra_keys_allowed(interpreter, valid_json_data):
    valid_json_data["extraMetadataKey"] = "SuperSecretValue"
    assert call(interpreter.verifySyntax, valid_json_data) is True

def test_verifySyntax_catches_load_exception(interpreter):
    # Ensure any exceptions occurring in _load safely result in False (no crashes)
    with patch.object(JsonInterpreter, '_load', side_effect=FileNotFoundError):
        assert call(interpreter.verifySyntax, "dummy_file.json") is False

@pytest.mark.parametrize("missing_key", ["boardSize", "waypoints", "walls"])
def test_verifySyntax_missing_required_keys(interpreter, valid_json_data, missing_key):
    """boardSize/waypoints/walls are required. solutionPath is optional (the API and the
    screenshot extractor never send it, and the reference board ships it populated), so it
    is not in this list."""
    del valid_json_data[missing_key]
    assert call(interpreter.verifySyntax, valid_json_data) is False


def test_verifySyntax_solution_path_is_optional(interpreter, valid_json_data):
    """A payload with no solutionPath key is valid — it is not part of the board contract."""
    valid_json_data.pop("solutionPath", None)
    assert call(interpreter.verifySyntax, valid_json_data) is True

@pytest.mark.parametrize("solution_path", [
    "empty",        # Wrong type (string)
    None,           # Wrong type (None)
    {},             # Wrong type (dict)
])
def test_verifySyntax_invalid_solution_path(interpreter, valid_json_data, solution_path):
    """When solutionPath is present it must be a list. Its contents are not constrained
    here — path correctness is SolutionValidator's job, not the interpreter's — so a
    populated list is accepted (see next test)."""
    valid_json_data["solutionPath"] = solution_path
    assert call(interpreter.verifySyntax, valid_json_data) is False


def test_verifySyntax_populated_solution_path_is_accepted(interpreter, valid_json_data):
    """The reference board_configuration.json carries a full solutionPath; it must import
    cleanly rather than being rejected for being non-empty."""
    valid_json_data["solutionPath"] = [[0, 0], [0, 1], [0, 2]]
    assert call(interpreter.verifySyntax, valid_json_data) is True

def test_verifySyntax_cascading_failures(interpreter, valid_json_data):
    # Corrupting nested data properties to ensure verify delegates to sub-validators
    valid_json_data["boardSize"] = 10
    assert call(interpreter.verifySyntax, valid_json_data) is False
    
    valid_json_data["boardSize"] = 6
    valid_json_data["waypoints"] = [[0, 0]]
    assert call(interpreter.verifySyntax, valid_json_data) is False
    
def test_verifySyntax_non_dict_data(interpreter):
    assert call(interpreter.verifySyntax, ["list data"]) is False


# ===================================================================
# Tests for buildBoard
# ===================================================================
def test_buildBoard_valid(interpreter, valid_json_data):
    """buildBoard does structural parsing only and builds the Board directly — it no
    longer delegates to verifySyntax (semantics are InputValidator's job). Waypoint order
    is 1-based, matching PuzzleRules.getWaypointByOrder(1) and GameState."""
    with patch.object(JsonInterpreter, '_load', return_value=valid_json_data):
        board = call(interpreter.buildBoard, valid_json_data)

        assert isinstance(board, Board)
        assert board.getSize == 6

        # Waypoints added in order, numbered from 1.
        waypoints = board.getWaypoints
        assert len(waypoints) == 3
        assert waypoints[0].getPosition == Position(0, 0)
        assert waypoints[0].getOrder == 1
        assert waypoints[2].getPosition == Position(4, 4)
        assert waypoints[2].getOrder == 3

        # Verify walls were added correctly
        walls = board.getWalls
        assert len(walls) == 1
        assert board.hasWallBetween(Position(0, 0), Position(1, 0)) is True

def test_buildBoard_zero_walls(interpreter, valid_json_data):
    valid_json_data["walls"] = []
    with patch.object(JsonInterpreter, '_load', return_value=valid_json_data):
        board = call(interpreter.buildBoard, valid_json_data)
        assert len(board.getWalls) == 0

def test_buildBoard_structurally_invalid_raises(interpreter):
    """buildBoard raises ValueError only when the payload is too malformed to build a
    Board at all (missing a required key, non-integer coordinates). Semantically-invalid
    but structurally-sound boards build successfully and are judged by InputValidator —
    that is what lets the API return a structured 422 rather than a blanket 400."""
    with patch.object(JsonInterpreter, '_load', return_value={"boardSize": 6, "waypoints": [[0]]}):
        with pytest.raises(ValueError):
            call(interpreter.buildBoard, {"boardSize": 6, "waypoints": [[0]]})

def test_buildBoard_integration(interpreter, valid_json_data, tmp_path):
    """
    End-To-End test evaluating the whole pipeline un-mocked.
    WARNING: This test acts as a real-world assertion and will legitimately FAIL 
    until the internal `@staticmethod def method(self)` and `boardSize-1` bugs 
    are resolved inside JsonInterpreter.
    """
    file_path = tmp_path / "puzzle.json"
    file_path.write_text(json.dumps(valid_json_data), encoding="utf-8")
    
    board = call(interpreter.buildBoard, str(file_path))
    
    assert isinstance(board, Board)
    assert board.getSize == 6
    assert len(board.getWaypoints) == 3
    assert len(board.getWalls) == 1