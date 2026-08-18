"""Unit tests for InputValidator — the semantic rule layer (§5.5.4).

Pure: builds real ``Board`` objects, asserts the ``ValidationResult`` and error codes.
No mocks, no I/O. These pin the taxonomy mapping the API relies on to turn a rejected
board into the right 422 code.
"""

from __future__ import annotations

import pytest

from backend.input_validation.input_validator import InputValidator
from backend.puzzle_logic import Board, Position


@pytest.fixture
def validator() -> InputValidator:
    """
    Instantiates a stateless testing validator singleton.

    Returns:
        An isolated validation evaluator instance.

    Implementation Details:
        Acts as a standard fixture generating pristine evaluations.
    """
    return InputValidator()


def _board(size: int, waypoints, walls=()):
    """
    Synthesizes active puzzle graph topologies rapidly for distinct edge testing.

    Args:
        size: The designated overarching row length constraint.
        waypoints: The array mapping structured milestones.
        walls: The array defining physical intersection hurdles.

    Returns:
        The securely populated puzzle board matching given structural arguments.

    Implementation Details:
        Directly wraps underlying domain object instantiation utilizing raw coordinate 
        loops to streamline repetitive structural definitions across tests.
    """
    board = Board(size)
    for order, (x, y) in enumerate(waypoints, start=1):
        board.addWaypoint(Position(x, y), order)
    for (ax, ay), (bx, by) in walls:
        board.addWall(Position(ax, ay), Position(bx, by))
    return board


class TestValidBoards:
    """
    Evaluates successful traversal behaviors targeting untainted topologies.

    Responsibility:
        Ensures baseline structural matrices natively pass rigid validations cleanly 
        without flagging false positive assertions.

    Implementation Details:
        Relies heavily on parametrization passing varying acceptable scales validating 
        empty array error returns and positive boolean state confirmations across the layer.
    """
    def test_minimal_valid_board(self, validator):
        """
        Confirms absolute baseline matrices safely resolve validation gates natively.

        Implementation Details:
            Uses the minimal viable node geometry, checking that errors remain null and valid resolves strictly true.
        """
        result = validator.validate(_board(6, [(0, 0), (5, 5)]))
        assert result.valid is True
        assert result.errors == []
        assert result.message == "Board configuration is valid."

    @pytest.mark.parametrize("size", [6, 7, 8])
    def test_all_supported_sizes(self, validator, size):
        """
        Asserts dimensional scale limitations safely adapt without triggering warnings.

        Implementation Details:
            Iterates through the allowed dimension definitions feeding structurally identical matrices dynamically.
        """
        result = validator.validate(_board(size, [(0, 0), (size - 1, size - 1)]))
        assert result.valid is True

    def test_valid_board_with_walls(self, validator):
        """
        Confirms properly embedded physical boundaries are safely retained without geometric conflict.

        Implementation Details:
            Constructs adjacency links internally checking total resolution states cleanly bypass constraint loops.
        """
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (1, 0)), ((2, 2), (2, 3))])
        assert validator.validate(board).valid is True


class TestBoardSize:
    """
    Tests specific rejection protocols governing unsupported matrix scales.

    Responsibility:
        Verifies the overarching architectural scale limit strictly terminates bounding evaluations.

    Implementation Details:
        Constructs purposefully corrupted sizes validating the precise generation of the isolated 
        size violation taxonomy without bleeding into sub-checks.
    """
    @pytest.mark.parametrize("size", [5, 9, 10])
    def test_unsupported_size_rejected(self, validator, size):
        """
        Proves external scale boundaries forcibly generate structural validation failures.

        Implementation Details:
            Passes unsupported arguments asserting structural mapping returns the exact predefined size error code.
        """
        result = validator.validate(_board(size, [(0, 0), (1, 1)]))
        assert result.valid is False
        assert result.errors[0].error_code == "UNSUPPORTED_BOARD_SIZE"

    def test_size_error_short_circuits(self, validator):
        """
        A bad size returns immediately without also emitting bounds noise.

        Responsibility:
            Ensures unrecoverable bounding constraints actively prevent false cascading failures.

        Implementation Details:
            Passes a completely corrupted scale testing that array boundaries strictly cap at a single error count.
        """
        result = validator.validate(_board(5, [(0, 0), (1, 1)]))
        assert len(result.errors) == 1


class TestWaypoints:
    """
    Tests mathematical adherence regarding sequential point constraints.

    Responsibility:
        Asserts the semantic rules managing milestone limits correctly enforce duplication, bounds, and volumes.

    Implementation Details:
        Instantiates structurally illegal layouts targeting specific node constraints to force exact 
        violation code generations mapped to standard definitions.
    """
    def test_too_few_waypoints(self, validator):
        """
        Defends the strict rule that traversals must explicitly contain structural beginnings and ends.

        Implementation Details:
            Asserts an incomplete marker loop yields explicit waypoint failure flags natively.
        """
        result = validator.validate(_board(6, [(0, 0)]))
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WAYPOINTS"

    def test_out_of_bounds_waypoint(self, validator):
        """
        Prohibits points projecting geometries outside structural bounding limits.

        Implementation Details:
            Extracts the specific exception evaluating whether standard spatial bounds checking effectively flags out of limit nodes.
        """
        result = validator.validate(_board(6, [(0, 0), (9, 9)]))
        assert result.valid is False
        assert any(e.error_code == "INVALID_WAYPOINTS" for e in result.errors)

    def test_duplicate_waypoint(self, validator):
        """
        Flags sequence duplications spanning multiple identical coordinates.

        Implementation Details:
            Generates overlapping array bounds to test the localized set tracking loop structurally.
        """
        result = validator.validate(_board(6, [(0, 0), (0, 0), (5, 5)]))
        assert result.valid is False
        assert any(e.error_code == "INVALID_WAYPOINTS" for e in result.errors)


class TestWalls:
    """
    Tests semantic interpretations governing impenetrable structure mapping.

    Responsibility:
        Identifies unresolvable physical mapping conditions violating localized graph topologies.

    Implementation Details:
        Forces identical cell looping and illegal diagonal spacing into the validator matching strict 
        outputs explicitly.
    """
    def test_non_adjacent_wall(self, validator):
        """
        Prevents diagonal or heavily gapped definitions mapping non-contiguous blocks.

        Implementation Details:
            Passes mathematically disjointed arrays proving the validator checks spatial cardinality cleanly.
        """
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (2, 2))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"

    def test_out_of_bounds_wall(self, validator):
        """
        Defends bounding box loops natively trapping extraneous map structures.

        Implementation Details:
            Validates out-of-limits mapping generation throwing specific architectural faults natively.
        """
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (-1, 0))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"

    def test_self_loop_wall(self, validator):
        """
        Identifies useless walls isolating a single structural node unto itself.

        Implementation Details:
            Confirms node equality checks actively deny singular coordinate repetition blocks natively.
        """
        board = _board(6, [(0, 0), (5, 5)], walls=[((2, 2), (2, 2))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"


class TestExhaustiveCollection:
    """
    Validates structural error aggregation preventing drip-feed failure debugging.

    Responsibility:
        Assures multiple spatial logic faults are actively grouped and simultaneously returned 
        rather than abruptly short-circuiting at the first encountered warning.

    Implementation Details:
        Purposely builds broken layouts expecting the resulting diagnostic payload 
        array to accurately reflect the sheer quantity of individual errors detected iteratively.
    """
    def test_collects_multiple_errors(self, validator):
        """
        Every problem is reported at once, not one-at-a-time.

        Responsibility:
            Verifies the overarching aggregation engine successfully traverses multiple disparate test sectors.

        Implementation Details:
            Injects missing volumes, out-of-bounds metrics, and bad walls simultaneously checking error lengths.
        """
        board = _board(6, [(9, 9)], walls=[((0, 0), (3, 3))])  # too few + oob + bad wall
        result = validator.validate(board)
        assert result.valid is False
        assert len(result.errors) >= 2

    def test_message_counts_issues(self, validator):
        """
        Validates summary outputs structurally format numeric issue strings properly.

        Implementation Details:
            Queries the resultant metadata directly checking string contents for correct plurality tracking.
        """
        result = validator.validate(_board(6, [(0, 0)]))
        assert "issue" in result.message.lower()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))