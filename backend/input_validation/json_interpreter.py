import json
from typing import Any, Dict, Union, cast


from backend.input_validation.errors import BoardParseError, DuplicateWallError
from backend.puzzle_logic.board import Board
from backend.puzzle_logic import Position

class JsonInterpreter:
    """
    Validates and parses structural and topological puzzle definition JSON data.

    Responsibility:
        Serves as the primary validation gateway for incoming layout schemas, asserting 
        structural integrity, bounds checking, and preventing impossible geometries before 
        passing objects downstream.

    Implementation Details:
        Functions as a static namespace without maintaining an active state. Constrains 
        attributes such as dimensional arrays, waypoint lengths, and adjacency rules by 
        processing raw formats into Python dicts. Employs independent verification loops 
        for disparate object blocks to efficiently identify logical rule breaking.
    """

    ALLOWED_BOARD_SIZES = (6, 7, 8)

    # Retained deliberately, not dead code. ``verifySyntax`` is the all-or-nothing gate for
    # the *file* path — a board configuration read from disk (the reference
    # ``board_configuration.json``, fixtures, CLI use) where a single boolean verdict is
    # what the caller wants. The HTTP path deliberately does NOT use it: an endpoint has to
    # report *which* rule failed as a structured 422, which a bool cannot express, so
    # requests go through ``buildBoard`` + ``InputValidator`` instead. Two callers, two
    # contracts, one rule set.
    @staticmethod
    def verifySyntax(file: Union[str, dict, Any]) -> bool:
        """
        Validates whether an input file strictly matches expected syntax and constraints.

        Args:
            file: The raw file path, stream object, or parsed structure requiring evaluation.

        Returns:
            A definitive boolean confirming absolute structural and spatial adherence.

        Implementation Details:
            Acts as an all-or-nothing boolean gate designed explicitly for disk-based 
            configurations (reference boards, fixtures) where precise error reporting is 
            unnecessary. Submits the raw input to protected load methods, masking crashes 
            in a defensive exception block, and delegates nested array checks to targeted 
            validation helpers. Short-circuits heavily upon the first encountered anomaly.
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
        Constructs an actionable layout matrix from an input mapping source.

        Args:
            file: The raw JSON document payload or location referencing the overarching structure.

        Returns:
            An actively populated domain representation equipped with milestones and borders.

        Raises:
            ValueError: If the supplied mapping fundamentally fails schema structure or formatting.
            DuplicateWallError: If identical barrier parameters map out over the identical segment.

        Implementation Details:
            Applies structural parsing exclusively. Extracts valid dictionary pairs utilizing 
            an internal cast closure (`_point`) to strip booleans and force native integer bounds. 
            Deliberately abstains from overarching semantic checks (like dimensional size) to 
            avoid collapsing specific error codes into blanket responses. Leverages a local 
            `frozenset` generation hook to explicitly trap unordered wall duplication before 
            injecting it into the lossy board-level properties.
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

        # Duplicate walls are rejected HERE and nowhere else. Board keeps walls in a set
        # with order-independent equality, so {A,B} and {B,A} silently collapse on insert;
        # once that has happened InputValidator has no way to observe — let alone report —
        # the duplicate. The ordered payload list is the last point at which the rule of
        # §5.5.1 is checkable, so the check runs before the Board is populated.
        seen_walls: set[frozenset[tuple[int, int]]] = set()

        for wall in data["walls"]:
            if not isinstance(wall, dict) or "neighborA" not in wall or "neighborB" not in wall:
                raise ValueError("Each wall must have neighborA and neighborB.")
            ax, ay = _point(wall["neighborA"])
            bx, by = _point(wall["neighborB"])

            key = frozenset({(ax, ay), (bx, by)})
            if key in seen_walls:
                raise DuplicateWallError(
                    f"Duplicate wall between ({ax}, {ay}) and ({bx}, {by}). "
                    "A wall may only be declared once, in either cell order."
                )
            seen_walls.add(key)

            board.addWall(Position(ax, ay), Position(bx, by))

        return board


    @staticmethod
    def _load(arg: Union[str, dict, Any]) -> Dict[str, Any]:
        """
        Translates dynamic input objects into a structured domain schema.

        Args:
            arg: The ambiguous reference target potentially matching disk paths or byte payloads.

        Returns:
            The definitively unpacked dictionary mapping native parameters.

        Raises:
            TypeError: If the supplied reference target structurally contradicts supported patterns.

        Implementation Details:
            Sequences extraction based strictly upon `duck-typing`. Evaluates Pydantic structures 
            utilizing `.model_dump()` paired with alias rules, bypassing object inheritance checks. 
            Applies standard UTF-8 parsing via native IO hooks directly mapping string locations 
            and fallback memory objects into operational dictionaries.
        """
        if isinstance(arg, dict):
            return arg
        # Pydantic models (e.g. PuzzleRequest from the API layer): serialise by alias so the
        # keys match the schema (boardSize/waypoints/walls). Checked before str/read since a
        # model has neither.
        if hasattr(arg, "model_dump"):
            return cast(Any, arg).model_dump(by_alias=True)
        if isinstance(arg, str):
            with open(arg, "r", encoding="utf-8") as f:
                return json.load(f)
        if hasattr(arg, "read"):
            content = arg.read()
            return json.loads(content)
        raise TypeError(f"Unsupported argument type for json file: {type(arg)}")
    
    @staticmethod
    def _validate_board_size(board_size: Any) -> bool:
        """
        Confirms if a numeric scale falls within permitted execution dimensions.

        Args:
            board_size: The targeted grid span requiring authorization.

        Returns:
            A boolean denoting direct support for the requested parameters.

        Implementation Details:
            Conducts a direct membership evaluation against the class-level tuple defining 
            architectural capacities, ensuring limits stay bounded safely.
        """
        return board_size in JsonInterpreter.ALLOWED_BOARD_SIZES
    
    @staticmethod
    def _is_valid_point(point: Any, board_size: int) -> bool:
        """
        Authenticates coordinate topologies against boundary maximums and types.

        Args:
            point: The isolated array chunk mapping Cartesian sequences.
            board_size: The bounding constraint defining out-of-bounds parameters.

        Returns:
            A boolean identifying uncorrupted and internal map placement.

        Implementation Details:
            Explicitly intercepts boolean inheritance exploits native to Python before enforcing 
            strictly constrained zero-indexed Cartesian boundaries against both internal indices.
        """
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        x, y = point
        if not (isinstance(x, int) and isinstance(y, int)) \
                or isinstance(x, bool) or isinstance(y, bool):
            return False
        
        return 0 <= x < board_size and 0 <= y < board_size

    @staticmethod
    def _validate_waypoints(waypoints: Any, board_size: int) -> bool:
        """
        Verifies milestone sequences follow spatial routing and saturation rules.

        Args:
            waypoints: The aggregated array sequence containing trajectory checkpoints.
            board_size: The overarching spatial maximum utilized for capacity validation.

        Returns:
            A boolean acknowledging clean structural separation and correct payload depth.

        Implementation Details:
            Computes grid saturation ceilings natively utilizing basic exponents. Traverses 
            point definitions aggressively pushing translated tuples against a generic Set 
            tracker to instantly trigger upon coordinate repetition.
        """
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
        """
        Examines barrier parameters to enforce architectural boundaries and adjacency laws.

        Args:
            walls: The extracted payload list mapping physical interruptions.
            board_size: The dimensional framework utilized to calculate max block limits.

        Returns:
            A boolean indicating all grid partitions maintain localized rules.

        Implementation Details:
            Generates theoretical mathematical limits applying standard combination geometry 
            to short-circuit large payloads. Evaluates positional relationships directly against 
            Manhattan sums to enforce cardinal adjacency. Utilizes immutable `frozenset` objects 
            to trap any identical boundary declarations without regard to directional ordering.
        """
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