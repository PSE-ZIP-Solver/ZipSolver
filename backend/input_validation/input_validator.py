"""Semantic validation of a constructed ``Board`` (§5.5.4).

``JsonInterpreter`` guarantees *structural* shape — types are right, waypoints look like
``[x, y]`` pairs, walls carry ``neighborA``/``neighborB``. ``InputValidator`` is what
follows: it enforces the puzzle-domain rules that shape validation cannot express, and
returns a machine-readable ``ValidationResult`` with error codes mapped to the API
taxonomy (§5.5.5) so the router turns each into the right HTTP status.

Rules under this validator (all semantic):
  - Board size ∈ {6, 7, 8}                          → UNSUPPORTED_BOARD_SIZE
  - Waypoints: ≥ 2, in bounds, all unique          → INVALID_WAYPOINTS
  - Walls: cells in bounds, cardinally adjacent,
    unique (unordered), and the two cells differ   → INVALID_WALLS

Rules NOT under this validator:
  - Wire shape / types                              → ``PuzzleRequest`` (Pydantic)
  - Solve-time move legality                        → ``PuzzleRules``
  - Post-solve path correctness                     → ``SolutionValidator``

The validator is exhaustive — it collects *every* error it finds so the frontend can
surface all of them at once, rather than a "fix one, get the next" drip. When there are
errors, the message summarises "N issues found" and the individual codes/fields live in
``errors``.
"""

from __future__ import annotations

from typing import Iterable

from backend.api.dtos.ValidationResult import ValidationError, ValidationResult
from backend.puzzle_logic import Board, Position

_ALLOWED_BOARD_SIZES = (6, 7, 8)


def _err(code: str, field: str | None, message: str) -> ValidationError:
    return ValidationError(errorCode=code, affectedField=field, message=message)


def _wall_key(a: Position, b: Position) -> frozenset[tuple[int, int]]:
    """Order-independent wall identity: {(ax,ay), (bx,by)}. Matches ``Wall.__hash__``
    so this validator's dedup semantics agree with ``Board`` storage."""
    return frozenset({(a.getX, a.getY), (b.getX, b.getY)})


class InputValidator:
    """Semantic validator invoked by ``BackendAPI`` after ``JsonInterpreter.buildBoard``.

    Stateless: safe to instantiate once and share. Exposes a single public method,
    ``validate``, so it satisfies ``InputValidatorProtocol`` without any surface area
    the API doesn't need.
    """

    def validate(self, board: Board) -> ValidationResult:
        size = board.getSize
        errors: list[ValidationError] = []

        # Board size gate — everything downstream depends on this being sane, so if it
        # fails we return early. Otherwise the bounds checks below emit noisy false
        # positives against a size we've already rejected.
        if not self._is_valid_size(size):
            errors.append(
                _err(
                    "UNSUPPORTED_BOARD_SIZE",
                    "boardSize",
                    f"Board size {size} is not supported. Allowed sizes: 6, 7, 8.",
                )
            )
            return self._result(errors)

        errors.extend(self._check_waypoints(board, size))
        errors.extend(self._check_walls(board, size))

        return self._result(errors)

    # ── Rule blocks ─────────────────────────────────────────────────────────

    def _check_waypoints(self, board: Board, size: int) -> Iterable[ValidationError]:
        waypoints = board.getWaypoints
        cell_count = board.getCellCount()

        if len(waypoints) < 2:
            yield _err(
                "INVALID_WAYPOINTS",
                "waypoints",
                f"At least 2 waypoints are required; got {len(waypoints)}.",
            )
        if len(waypoints) > cell_count:
            yield _err(
                "INVALID_WAYPOINTS",
                "waypoints",
                f"Too many waypoints for a {size}x{size} board (max {cell_count}).",
            )

        seen: set[tuple[int, int]] = set()
        for index, wp in enumerate(waypoints):
            pos = wp.getPosition
            key = (pos.getX, pos.getY)

            if not board.isInside(pos):
                yield _err(
                    "INVALID_WAYPOINTS",
                    f"waypoints[{index}]",
                    f"Waypoint {index + 1} at ({pos.getX}, {pos.getY}) is outside the board.",
                )

            if key in seen:
                yield _err(
                    "INVALID_WAYPOINTS",
                    f"waypoints[{index}]",
                    f"Waypoint {index + 1} at ({pos.getX}, {pos.getY}) is a duplicate.",
                )
            seen.add(key)

    def _check_walls(self, board: Board, size: int) -> Iterable[ValidationError]:
        walls = board.getWalls
        max_walls = size * (size - 1) * 2  # every adjacent cell pair
        if len(walls) > max_walls:
            yield _err(
                "INVALID_WALLS",
                "walls",
                f"Too many walls for a {size}x{size} board (max {max_walls}).",
            )

        # ``board._walls`` is a set that already dedups by unordered pair, so counting
        # duplicates here would always report zero. Duplicates are enforced upstream in
        # ``JsonInterpreter._validate_walls``; here we cover in-bounds, adjacency, and
        # self-connection — anything the interpreter cannot know without a Board.
        for wall in walls:
            a, b = wall.getCellA, wall.getCellB
            a_in = board.isInside(a)
            b_in = board.isInside(b)

            if not a_in or not b_in:
                oob = []
                if not a_in:
                    oob.append(f"neighborA ({a.getX}, {a.getY})")
                if not b_in:
                    oob.append(f"neighborB ({b.getX}, {b.getY})")
                yield _err(
                    "INVALID_WALLS",
                    "walls",
                    "Wall references cell(s) outside the board: " + ", ".join(oob) + ".",
                )
                # Skip adjacency / equality checks for out-of-bounds walls; the coordinates
                # aren't meaningful, and reporting them adds noise the user can't act on.
                continue

            if a == b:
                yield _err(
                    "INVALID_WALLS",
                    "walls",
                    f"Wall's two cells are identical: ({a.getX}, {a.getY}).",
                )
                continue

            if not board.areAdjacent(a, b):
                yield _err(
                    "INVALID_WALLS",
                    "walls",
                    f"Wall cells ({a.getX}, {a.getY}) and ({b.getX}, {b.getY}) "
                    "are not cardinally adjacent.",
                )

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _is_valid_size(self, size: int) -> bool:
        if isinstance(size, bool):
            return False
        return size in _ALLOWED_BOARD_SIZES

    def _result(self, errors: list[ValidationError]) -> ValidationResult:
        if not errors:
            return ValidationResult(
                valid=True, message="Board configuration is valid.", errors=[]
            )
        summary = (
            f"{len(errors)} issue{'s' if len(errors) != 1 else ''} found in the board "
            "configuration."
        )
        return ValidationResult(valid=False, message=summary, errors=errors)