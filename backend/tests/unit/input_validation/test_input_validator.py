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
    return InputValidator()


def _board(size: int, waypoints, walls=()):
    board = Board(size)
    for order, (x, y) in enumerate(waypoints, start=1):
        board.addWaypoint(Position(x, y), order)
    for (ax, ay), (bx, by) in walls:
        board.addWall(Position(ax, ay), Position(bx, by))
    return board


class TestValidBoards:
    def test_minimal_valid_board(self, validator):
        result = validator.validate(_board(6, [(0, 0), (5, 5)]))
        assert result.valid is True
        assert result.errors == []
        assert result.message == "Board configuration is valid."

    @pytest.mark.parametrize("size", [6, 7, 8])
    def test_all_supported_sizes(self, validator, size):
        result = validator.validate(_board(size, [(0, 0), (size - 1, size - 1)]))
        assert result.valid is True

    def test_valid_board_with_walls(self, validator):
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (1, 0)), ((2, 2), (2, 3))])
        assert validator.validate(board).valid is True


class TestBoardSize:
    @pytest.mark.parametrize("size", [5, 9, 10])
    def test_unsupported_size_rejected(self, validator, size):
        result = validator.validate(_board(size, [(0, 0), (1, 1)]))
        assert result.valid is False
        assert result.errors[0].error_code == "UNSUPPORTED_BOARD_SIZE"

    def test_size_error_short_circuits(self, validator):
        """A bad size returns immediately without also emitting bounds noise."""
        result = validator.validate(_board(5, [(0, 0), (1, 1)]))
        assert len(result.errors) == 1


class TestWaypoints:
    def test_too_few_waypoints(self, validator):
        result = validator.validate(_board(6, [(0, 0)]))
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WAYPOINTS"

    def test_out_of_bounds_waypoint(self, validator):
        result = validator.validate(_board(6, [(0, 0), (9, 9)]))
        assert result.valid is False
        assert any(e.error_code == "INVALID_WAYPOINTS" for e in result.errors)

    def test_duplicate_waypoint(self, validator):
        result = validator.validate(_board(6, [(0, 0), (0, 0), (5, 5)]))
        assert result.valid is False
        assert any(e.error_code == "INVALID_WAYPOINTS" for e in result.errors)


class TestWalls:
    def test_non_adjacent_wall(self, validator):
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (2, 2))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"

    def test_out_of_bounds_wall(self, validator):
        board = _board(6, [(0, 0), (5, 5)], walls=[((0, 0), (-1, 0))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"

    def test_self_loop_wall(self, validator):
        board = _board(6, [(0, 0), (5, 5)], walls=[((2, 2), (2, 2))])
        result = validator.validate(board)
        assert result.valid is False
        assert result.errors[0].error_code == "INVALID_WALLS"


class TestExhaustiveCollection:
    def test_collects_multiple_errors(self, validator):
        """Every problem is reported at once, not one-at-a-time."""
        board = _board(6, [(9, 9)], walls=[((0, 0), (3, 3))])  # too few + oob + bad wall
        result = validator.validate(board)
        assert result.valid is False
        assert len(result.errors) >= 2

    def test_message_counts_issues(self, validator):
        result = validator.validate(_board(6, [(0, 0)]))
        assert "issue" in result.message.lower()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))