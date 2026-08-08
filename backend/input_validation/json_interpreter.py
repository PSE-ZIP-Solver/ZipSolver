import json
from typing import Any, Dict, Union


from backend.puzzle_logic.board import Board
from backend.puzzle_logic import Position

class JsonInterpreter:
    """
    Validates and parses puzzle definition JSON of the form:

    {
        "boardSize": 6,
        "waypoints": [[0, 0], [2, 2], [4, 4]],
        "walls": [ { "neighborA": [0, 0], "neighborB": [1, 0] } ],
        "solutionPath": []
    }

    Constraints enforced by verifySyntax():
      - boardSize must be one of {6, 7, 8}
      - waypoints: a list of [x, y] pairs, count between 2 and boardSize**2,
        each position inside the board, each position unique
      - walls: a list of {"neighborA": [x, y], "neighborB": [x, y]} objects,
        count between 0 and the max possible walls in the grid
        (size * (size - 1) * 2, i.e. every adjacent cell pair),
        each wall's two cells must be inside the board and adjacent
        (cardinal neighbors only), and walls must be unique - no duplicate
        wall between the same pair of cells (order of neighborA/neighborB
        doesn't matter), which also guarantees a cell has at most one wall
        per cardinal direction.
      - solutionPath: must be present and be an empty list
    """

    ALLOWED_BOARD_SIZES = (6, 7, 8)
    
    
    # TODO remove if not used!
    @staticmethod
    def verifySyntax(file: Union[str, dict, Any]) -> bool:
        """
        Takes a json file (path, open file object, or already-parsed dict)
        and returns True if it matches the expected syntax and constraints,
        False otherwise. Never raises - any parsing/validation failure just
        results in False.
        """
        try:
            data = JsonInterpreter._load(file)
        except Exception:
            return False

        if not isinstance(data, dict):
            return False

        required_keys = {"boardSize", "waypoints", "walls"}
        if not required_keys.issubset(data.keys()):
            return False

        board_size = data["boardSize"]
        if not JsonInterpreter._validate_board_size(board_size):
            return False

        waypoints = data["waypoints"]
        if not JsonInterpreter._validate_waypoints(waypoints, board_size):
            return False

        walls = data["walls"]
        if not JsonInterpreter._validate_walls(walls, board_size):
            return False

        # solutionPath is optional. The API's PuzzleRequest and the screenshot extractor
        # never send it; the reference board_configuration.json ships it populated. When
        # present it must be a list, but its contents are not constrained here (path
        # correctness is SolutionValidator's job, not the interpreter's).
        if "solutionPath" in data and not isinstance(data["solutionPath"], list):
            return False

        return True
    
    @staticmethod
    def buildBoard(file: Union[str, dict, Any]) -> Board:
        """
        Takes a json source (path, open file object, or already-parsed dict) and returns
        a populated Board.

        This performs STRUCTURAL parsing only — it checks that the payload has the right
        keys and that coordinates are 2-integer pairs, enough to construct a Board without
        crashing. It deliberately does NOT enforce semantic rules (board size in {6,7,8},
        waypoint bounds/count/uniqueness, wall adjacency); those belong to InputValidator,
        which the API runs immediately after this and which reports each failure as a
        structured 422 rather than a blanket ValueError. Running the semantic checks here
        too would collapse those into a 400 and lose the per-error detail.

        Raises ValueError only when the payload is too malformed to build a Board at all.
        """
        data = JsonInterpreter._load(file)

        if not isinstance(data, dict):
            raise ValueError("Puzzle JSON must be an object.")
        for key in ("boardSize", "waypoints", "walls"):
            if key not in data:
                raise ValueError(f"Puzzle JSON is missing required key: {key!r}.")
        if not isinstance(data["boardSize"], int) or isinstance(data["boardSize"], bool):
            raise ValueError("boardSize must be an integer.")
        if not isinstance(data["waypoints"], list) or not isinstance(data["walls"], list):
            raise ValueError("waypoints and walls must be lists.")

        def _point(value: Any) -> tuple[int, int]:
            if (
                not isinstance(value, (list, tuple))
                or len(value) != 2
                or not all(isinstance(c, int) and not isinstance(c, bool) for c in value)
            ):
                raise ValueError(f"Coordinate must be a [x, y] integer pair: {value!r}.")
            return int(value[0]), int(value[1])

        board = Board(data["boardSize"])

        # 1-based ordering: PuzzleRules._startsAtFirstWaypoint reads getWaypointByOrder(1)
        # and GameState starts at order 2, so the first waypoint must be order 1, not 0.
        for order, raw in enumerate(data["waypoints"], start=1):
            x, y = _point(raw)
            board.addWaypoint(Position(x, y), order)

        for wall in data["walls"]:
            if not isinstance(wall, dict) or "neighborA" not in wall or "neighborB" not in wall:
                raise ValueError("Each wall must have neighborA and neighborB.")
            ax, ay = _point(wall["neighborA"])
            bx, by = _point(wall["neighborB"])
            board.addWall(Position(ax, ay), Position(bx, by))

        return board


    @staticmethod
    def _load(arg: Union[str, dict, Any]) -> Dict[str, Any]:
        """Accepts a file path (str), an open file-like object, or a dict."""
        if isinstance(arg, dict):
            return arg
        if isinstance(arg, str):
            with open(arg, "r", encoding="utf-8") as f:
                return json.load(f)
        if hasattr(arg, "read"):
            content = arg.read()
            return json.loads(content)
        raise TypeError(f"Unsupported argument type for json file: {type(arg)}")
    
    @staticmethod
    def _validate_board_size(board_size: Any) -> bool:
        return board_size in JsonInterpreter.ALLOWED_BOARD_SIZES
    
    @staticmethod
    def _is_valid_point(point: Any, board_size: int) -> bool:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        x, y = point
        if not (isinstance(x, int) and isinstance(y, int)) \
                or isinstance(x, bool) or isinstance(y, bool):
            return False
        
        return 0 <= x < board_size and 0 <= y < board_size

    @staticmethod
    def _validate_waypoints(waypoints: Any, board_size: int) -> bool:
        if not isinstance(waypoints, list):
            return False

        max_waypoints = board_size ** 2
        if not (2 <= len(waypoints) <= max_waypoints):
            return False

        seen = set()
        for point in waypoints:
            if not JsonInterpreter._is_valid_point(point, board_size):
                return False
            key = (point[0], point[1])
            if key in seen:
                return False
            seen.add(key)

        return True

    @staticmethod
    def _validate_walls(walls: Any, board_size: int) -> bool:
        if not isinstance(walls, list):
            return False

        max_walls = board_size * (board_size - 1) * 2  # every adjacent cell pair
        if not (0 <= len(walls) <= max_walls):
            return False

        seen_walls = set()
        for wall in walls:
            if not isinstance(wall, dict):
                return False
            if not {"neighborA", "neighborB"}.issubset(wall.keys()):
                return False

            a = wall["neighborA"]
            b = wall["neighborB"]

            if not JsonInterpreter._is_valid_point(a, board_size):
                return False
            if not JsonInterpreter._is_valid_point(b, board_size):
                return False

            ax, ay = a
            bx, by = b

            if (ax, ay) == (bx, by):
                return False

            # must be cardinal neighbors (adjacent cells only)
            if abs(ax - bx) + abs(ay - by) != 1:
                return False

            # unordered uniqueness -> also ensures at most one wall
            # between a given cell and a given cardinal neighbor
            key = frozenset({(ax, ay), (bx, by)})
            if key in seen_walls:
                return False
            seen_walls.add(key)

        return True