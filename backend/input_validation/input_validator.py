"""Semantic validation of a constructed ``Board`` (§5.5.4).

``JsonInterpreter`` guarantees *structural* shape — types are right, waypoints look like
``[x, y]`` pairs, walls carry ``neighborA``/``neighborB``. ``InputValidator`` is what
follows: it enforces the puzzle-domain rules that shape validation cannot express, and
returns a machine-readable ``ValidationResult`` with error codes mapped to the API
taxonomy (§5.5.5) so the router turns each into the right HTTP status.

Rules under this validator (all semantic):
  - Board size in {6, 7, 8}                          -> UNSUPPORTED_BOARD_SIZE
  - Waypoints: >= 2, in bounds, all unique           -> INVALID_WAYPOINTS
  - Walls: cells in bounds, cardinally adjacent,
    and the two cells differ                          -> INVALID_WALLS

Rules NOT under this validator:
  - Wire shape / types                               -> ``PuzzleRequest`` (Pydantic)
  - Solve-time move legality                          -> ``PuzzleRules``
  - Post-solve path correctness                       -> ``SolutionValidator``

The validator is exhaustive — it collects *every* error it finds so the frontend can
surface all of them at once rather than a fix-one-see-the-next drip.
"""

from __future__ import annotations

from typing import Iterable

from backend.input_validation.validation_dtos import ValidationError, ValidationResult
from backend.puzzle_logic import Board

_ALLOWED_BOARD_SIZES = (6, 7, 8)


def _err(code: str, field: str | None, message: str) -> ValidationError:
    return ValidationError(errorCode=code, affectedField=field, message=message)


class InputValidator:
    """Semantic validator invoked by ``BackendAPI`` after ``JsonInterpreter.buildBoard``.

    Stateless: safe to instantiate once and share. Exposes a single public method,
    ``validate``, so it satisfies ``InputValidatorProtocol`` without any surface area the
    API does not need.
    """

    def validate(self, board: Board) -> ValidationResult:
        size = board.getSize
        errors: list[ValidationError] = []

        # Board size gate first — everything downstream depends on it being sane, so if it
        # fails we return early rather than emitting noisy bounds errors against a size we
        # have already rejected.
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

    # ── Rule blocks ──────────────────────────────────────────────────────────

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

        # ``board.getWalls`` is a set that already dedups by unordered pair, so counting
        # duplicates here would always report zero. Duplicates are handled upstream in the
        # interpreter; here we cover in-bounds, adjacency, and self-connection — anything
        # the interpreter cannot know without a Board.
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
                # Coordinates are meaningless once out of bounds; skip the adjacency and
                # equality checks so the user is not handed noise they cannot act on.
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

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _is_valid_size(self, size: int) -> bool:
        # bool is a subclass of int — exclude it so True/False can't pass as a size.
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