import json
from typing import Any, Dict, List, Tuple, Union

from backend.api.dtos.PuzzleRequest import PuzzleRequest
from backend.puzzle_logic.board import Board
from backend.puzzle_logic import Position

# A parsed board request may reach the interpreter either as the API's PuzzleRequest
# DTO (POST /api/solve, /api/import) or as raw JSON (file path, file handle, or dict)
# for the standalone import-file workflow. Both are supported.
JsonSource = Union[str, dict, Any]


class JsonInterpreter:
    """Parses a puzzle definition into a populated :class:`Board`.

    Two entry points:

    * :meth:`buildBoard` — API-facing. Accepts a ``PuzzleRequest`` DTO (or a raw JSON
      source) and returns a ``Board``. Structural shape is already guaranteed by the DTO;
      semantic legality (in-bounds, adjacency, waypoint order) is ``InputValidator``'s
      responsibility, so this method does not re-run those checks for a DTO input.

    * :meth:`verifySyntax` — standalone JSON validator for the import-file workflow.
      Returns ``True``/``False`` for a raw JSON source (path, file handle, or dict) of the
      form::

          {
              "boardSize": 6,
              "waypoints": [[0, 0], [2, 2], [4, 4]],
              "walls": [ { "neighborA": [0, 0], "neighborB": [1, 0] } ],
              "solutionPath": []
          }

    Constraints enforced by :meth:`verifySyntax`:
      - boardSize in {6, 7, 8}
      - waypoints: list of [x, y] pairs, count in [2, boardSize**2], each in-bounds,
        all unique
      - walls: list of {"neighborA": [x, y], "neighborB": [x, y]}, count in
        [0, size*(size-1)*2], each cell in-bounds, the two cells cardinally adjacent,
        no duplicate wall (unordered)
      - solutionPath: present and an empty list
    """

    ALLOWED_BOARD_SIZES = (6, 7, 8)

    # ── API-facing entry point ──────────────────────────────────────────────

    def buildBoard(self, request: PuzzleRequest) -> Board:
        """Build a populated ``Board`` from a ``PuzzleRequest`` DTO or a raw JSON source.

        For a DTO, trusts the DTO's structural guarantees and constructs the board
        directly. For a raw JSON source, runs :meth:`verifySyntax` first and raises
        ``ValueError`` if it fails.
        """
        board_size, waypoints, walls = self._extract(request)

        board = Board(board_size)
        for order, (x, y) in enumerate(waypoints, start=1):
            board.addWaypoint(Position(x, y), order)
        for (ax, ay), (bx, by) in walls:
            board.addWall(Position(ax, ay), Position(bx, by))
        return board

    def _extract(
        self, source: Any
    ) -> Tuple[int, List[Tuple[int, int]], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """Normalise either a ``PuzzleRequest`` DTO or a raw JSON source into plain
        ``(board_size, waypoints, walls)`` tuples the ``Board`` constructor understands."""
        # Duck-typed DTO detection: PuzzleRequest exposes board_size / waypoints / walls.
        if hasattr(source, "board_size") and hasattr(source, "waypoints"):
            waypoints = [tuple(wp) for wp in source.waypoints]
            walls = [
                (tuple(w.neighbor_a), tuple(w.neighbor_b)) for w in source.walls
            ]
            return source.board_size, waypoints, walls

        # Raw JSON path: validate, then read the parsed dict.
        if not self.verifySyntax(source):
            raise ValueError("Invalid puzzle JSON: failed syntax/constraint checks.")
        data = self._load(source)
        waypoints = [tuple(pt) for pt in data["waypoints"]]
        walls = [
            (tuple(w["neighborA"]), tuple(w["neighborB"])) for w in data["walls"]
        ]
        return data["boardSize"], waypoints, walls

    # ── Standalone JSON validator ───────────────────────────────────────────

    def verifySyntax(self, file: JsonSource) -> bool:
        """Return ``True`` iff ``file`` matches the expected syntax and constraints.
        Never raises — any parsing/validation failure returns ``False``."""
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

        if not self._validate_waypoints(data["waypoints"], board_size):
            return False

        if not self._validate_walls(data["walls"], board_size):
            return False

        solution_path = data["solutionPath"]
        if not isinstance(solution_path, list) or len(solution_path) != 0:
            return False

        return True

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _load(self, arg: JsonSource) -> Dict[str, Any]:
        """Accept a file path (str), an open file-like object, or a dict."""
        if isinstance(arg, dict):
            return arg
        if isinstance(arg, str):
            with open(arg, "r", encoding="utf-8") as f:
                return json.load(f)
        if hasattr(arg, "read"):
            return json.loads(arg.read())
        raise TypeError(f"Unsupported argument type for json file: {type(arg)}")

    def _validate_board_size(self, board_size: Any) -> bool:
        # bool is a subclass of int — exclude it explicitly so True/False can't pass.
        if isinstance(board_size, bool):
            return False
        return board_size in self.ALLOWED_BOARD_SIZES

    def _is_valid_point(self, point: Any, board_size: int) -> bool:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        x, y = point
        if isinstance(x, bool) or isinstance(y, bool):
            return False
        if not (isinstance(x, int) and isinstance(y, int)):
            return False
        return 0 <= x < board_size and 0 <= y < board_size

    def _validate_waypoints(self, waypoints: Any, board_size: int) -> bool:
        if not isinstance(waypoints, list):
            return False

        if not (2 <= len(waypoints) <= board_size ** 2):
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
            if not self._is_valid_point(a, board_size) or not self._is_valid_point(b, board_size):
                return False

            ax, ay = a
            bx, by = b
            if (ax, ay) == (bx, by):
                return False

            # cardinal neighbours only
            if abs(ax - bx) + abs(ay - by) != 1:
                return False

            # unordered uniqueness -> at most one wall per cell pair
            key = frozenset({(ax, ay), (bx, by)})
            if key in seen_walls:
                return False
            seen_walls.add(key)

        return True