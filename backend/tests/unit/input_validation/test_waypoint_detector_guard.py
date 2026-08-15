"""Regression guard: an empty disc map must not fabricate waypoints.

GridLocalizer returns ``last_waypoint_cells = {}`` when it finds no discs. The detector
previously branched on truthiness in one place and identity in another, so an empty dict
took the per-cell scan path AND had every miss promoted to a detected marker — turning a
board-less screenshot into n^2 phantom waypoints that passed semantic validation.
"""

from unittest.mock import patch

import pytest

from backend.input_validation.screenshot.theme_mode import ThemeMode
from backend.input_validation.screenshot.waypoint_detector import WaypointDetector


CELL_BOUNDS = {
    (x, y): (x * 10, y * 10, 10, 10) for x in range(6) for y in range(6)
}


@pytest.mark.parametrize("disc_cells", [None, {}])
def test_no_markers_yields_no_waypoints(disc_cells):
    detector = WaypointDetector()
    with patch.object(detector, "_detect_marker_and_read", return_value=None):
        result = detector.detect_waypoints(
            _fake_image(), CELL_BOUNDS, ThemeMode.LIGHT, disc_cells
        )
    assert result == []
    assert detector.last_warnings == []


def test_supplied_disc_positions_are_trusted_even_when_unreadable():
    """A disc found by global detection counts as a waypoint even if its digit is not read."""
    detector = WaypointDetector()
    discs = {(0, 0): (5.0, 5.0, 3.0), (5, 5): (55.0, 55.0, 3.0)}
    with patch.object(detector, "_detect_marker_and_read", return_value=None):
        result = detector.detect_waypoints(
            _fake_image(), CELL_BOUNDS, ThemeMode.LIGHT, discs
        )
    assert sorted(map(tuple, result)) == [(0, 0), (5, 5)]
    assert detector.last_warnings, "unreadable numerals must be reported as warnings"


def test_warnings_are_structured_with_a_discriminating_code():
    detector = WaypointDetector()
    discs = {(0, 0): (5.0, 5.0, 3.0), (5, 5): (55.0, 55.0, 3.0)}
    with patch.object(detector, "_detect_marker_and_read", return_value=None):
        detector.detect_waypoints(_fake_image(), CELL_BOUNDS, ThemeMode.LIGHT, discs)

    for warning in detector.last_warnings:
        assert isinstance(warning, dict)
        assert warning["code"] in {
            "WAYPOINT_NUMBER_UNREADABLE",
            "WAYPOINT_NUMBER_DUPLICATE",
            "WAYPOINT_ORDER_INFERRED",
        }
        assert warning["message"]


def _fake_image():
    import numpy as np

    return np.zeros((60, 60, 3), dtype=np.uint8)