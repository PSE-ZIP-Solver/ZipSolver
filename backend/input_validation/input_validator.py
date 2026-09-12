"""
Semantic validation of a constructed Board (§5.5.4).

Responsibility:
    Functions as the specialized domain evaluator for overarching puzzle elements following
    raw structure digestion. Generates descriptive, machine-readable validation outputs
    designed to plug dynamically into API taxonomies while consolidating all identifiable
    failures.

Implementation Details:
    Operates entirely apart from raw payload interpretation (managed by `JsonInterpreter`)
    and runtime logic (`PuzzleRules`). The architecture enforces comprehensive, exhaustive
    scanning, rejecting isolated drip-feed corrections by aggregating every discovered flaw
    across nodes and barriers into a single return execution.
"""

from __future__ import annotations

from typing import Iterable

from backend.input_validation.validation_dtos import ValidationError, ValidationResult
from backend.puzzle_logic import Board

_ALLOWED_BOARD_SIZES = (6, 7, 8)


def _err(code: str, field: str | None, message: str) -> ValidationError:
    """
    Constructs a localized violation object mapped to an external taxonomy code.

    Args:
        code: The rigid identifier linking directly to overarching system status taxonomies.
        field: The targeted contextual string highlighting the faulty payload region.
        message: The descriptive summary intended for human-readable debug logs.

    Returns:
        The initialized transport container encapsulating the localized fault.

    Implementation Details:
        Leverages strict constructor invocation for the localized DTO wrapper, ensuring
        consistent structure for the payload's subsequent serialization up to the orchestrator.
    """
    return ValidationError(errorCode=code, affectedField=field, message=message)


class InputValidator:
    """
    Semantic rule validator executed post-construction to secure model viability.

    Responsibility:
        Evaluates a structured domain matrix enforcing absolute boundaries, valid geometric
        shapes, and node counts prior to dispatching them toward execution engines.

    Implementation Details:
        Functions statelessly, satisfying an implicit `InputValidatorProtocol` seamlessly.
        Built to be instantiated globally or shared across concurrent threading limits
        without fear of internal state corruption, exposing only a singular public operation.
    """

    def validate(self, board: Board) -> ValidationResult:
        """
        Aggregates independent structural checks to assess ultimate domain safety.

        Args:
            board: The actively populated grid structure representing puzzle conditions.

        Returns:
            A definitive packaged finding communicating structural validity and contextual flaws.

        Implementation Details:
            Safeguards execution channels defensively by validating primary matrix boundaries
            first. Aborts immediately upon gross size violations to prevent overwhelming arrays
            of secondary errors, before chaining array generators to pool disparate milestone
            and barrier failures safely.
        """
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
        """
        Scans milestone configurations to locate mathematical bounds and collision issues.

        Args:
            board: The populated grid structure acting as the analytical focal point.
            size: The bounding limit controlling maximum node array depths.

        Returns:
            A generator pushing distinct contextual violation envelopes upon detection.

        Implementation Details:
            Traverses embedded spatial instances comparing localized grid keys against internal
            `Board` evaluation methods. Constructs memory maps via tuple Sets to efficiently
            reject node coordinates stacked onto identical active spaces.
        """
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
        """
        Inspects internal barrier definitions for coordinate failures and topological breaks.

        Args:
            board: The architectural matrix mapping spatial configurations.
            size: The bounding dimensions utilized to enforce edge volumes.

        Returns:
            An iterative sequence of localized error envelopes identifying violations.

        Implementation Details:
            Dynamically limits evaluations natively before iterating internal array items.
            Selectively short-circuits internal validation branches when nodes register as
            entirely out-of-bounds, actively preventing garbage calculations or misleading
            adjacent failure tags from polluting downstream system logs.
        """
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
                    "Wall references cell(s) outside the board: "
                    + ", ".join(oob)
                    + ".",
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
        """
        Checks target scaling limits against permissible internal frameworks.

        Args:
            size: The exact numeric grid scale necessitating authorization.

        Returns:
            A definitive boolean affirming direct system support.

        Implementation Details:
            Defensively intercepts edge cases associated with base `bool` inheritance prior to
            accessing the global allowance tuple, explicitly returning internal validation flags.
        """
        # bool is a subclass of int — exclude it so True/False can't pass as a size.
        if isinstance(size, bool):
            return False
        return size in _ALLOWED_BOARD_SIZES

    def _result(self, errors: list[ValidationError]) -> ValidationResult:
        """
        Packages an array of operational faults into a formalized transfer object.

        Args:
            errors: The compiled lists encompassing all captured localized warnings.

        Returns:
            The comprehensive container utilized by outer orchestrators to map system behavior.

        Implementation Details:
            Examines array lengths actively to construct dynamically populated warning strings.
            Differentiates directly between plural grammatical structures and instantiates
            external validation models utilizing absolute state bindings.
        """
        if not errors:
            return ValidationResult(
                valid=True, message="Board configuration is valid.", errors=[]
            )
        summary = (
            f"{len(errors)} issue{'s' if len(errors) != 1 else ''} found in the board "
            "configuration."
        )
        return ValidationResult(valid=False, message=summary, errors=errors)
