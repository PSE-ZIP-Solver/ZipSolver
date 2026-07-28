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

    def verifySyntax(self, file: Union[str, dict, Any]) -> bool:
        """
        Takes a json file (path, open file object, or already-parsed dict)
        and returns True if it matches the expected syntax and constraints,
        False otherwise. Never raises - any parsing/validation failure just
        results in False.
        """
        try:
            data = self._load(file)
        except Exception:
            return False

        if not isinstance(data, dict):
            return False

        required_keys = {"boardSize", "waypoints", "walls", "solutionPath"}
        if not required_keys.issubset(data.keys()):
            return False

        board_size = data["boardSize"]
        if not self._validate_board_size(board_size):
            return False

        waypoints = data["waypoints"]
        if not self._validate_waypoints(waypoints, board_size):
            return False

        walls = data["walls"]
        if not self._validate_walls(walls, board_size):
            return False

        solution_path = data["solutionPath"]
        if not isinstance(solution_path, list):
            return False
        if len(solution_path) != 0:
            return False

        return True

    def buildBoard(self, file: Union[str, dict, Any]) -> Board:
        """
        Takes a json file (path, open file object, or already-parsed dict),
        validates it, and returns a populated Board instance.
        Raises ValueError if the json does not match the expected syntax.
        """
        if not self.verifySyntax(file):
            raise ValueError("Invalid puzzle JSON: failed syntax/constraint checks.")

        data = self._load(file)

        board = Board(data["boardSize"])

        for order, (x, y) in enumerate(data["waypoints"]):
            board.addWaypoint(Position(x, y), order)

        for wall in data["walls"]:
            ax, ay = wall["neighborA"]
            bx, by = wall["neighborB"]
            board.addWall(Position(ax, ay), Position(bx, by))

        return board

    # ---------- internal helpers ----------

    def _load(self, arg: Union[str, dict, Any]) -> Dict[str, Any]:
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

    def _validate_board_size(self, board_size: Any) -> bool:
        return board_size in self.ALLOWED_BOARD_SIZES

    def _is_valid_point(self, point: Any, board_size: int) -> bool:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        x, y = point
        if not (isinstance(x, int) and isinstance(y, int)) \
                or isinstance(x, bool) or isinstance(y, bool):
            return False
        return 0 <= x < board_size-1 and 0 <= y < board_size-1

    def _validate_waypoints(self, waypoints: Any, board_size: int) -> bool:
        if not isinstance(waypoints, list):
            return False

        max_waypoints = board_size ** 2
        if not (2 <= len(waypoints) <= max_waypoints):
            return False

        seen = set()
        for point in waypoints:
            if not self._is_valid_point(point, board_size):
                return False
            key = (point[0], point[1])
            if key in seen:
                return False
            seen.add(key)

        return True

    def _validate_walls(self, walls: Any, board_size: int) -> bool:
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

            if not self._is_valid_point(a, board_size):
                return False
            if not self._is_valid_point(b, board_size):
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