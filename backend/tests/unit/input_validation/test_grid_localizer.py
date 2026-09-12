import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.grid_localizer import GridLocalizer


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Safe Mocking [THE "DANGER ZONE"]: keep heavy CV/Math deps out of collection.

    Responsibility:
        Ensures the test suite runs deterministically without bootstrapping heavy
        external C-based libraries during the test discovery phase.

    Implementation Details:
        Intercepts and dynamically patches the global module registry before any test executes.
        Replaces actual module references with strictly configured mock objects, injecting
        essential baseline constant values to prevent runtime attribution errors when the
        tested components attempt lazy imports.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()
    mock_cv2.RETR_EXTERNAL = 0
    mock_cv2.CHAIN_APPROX_SIMPLE = 2
    mock_cv2.MORPH_OPEN = 2
    mock_cv2.MORPH_CLOSE = 3
    mock_cv2.COLOR_BGR2HSV = 40
    mock_cv2.COLOR_BGR2GRAY = 6
    with patch.dict(sys.modules, {"numpy": mock_numpy, "cv2": mock_cv2}):
        yield {"numpy": mock_numpy, "cv2": mock_cv2}


class TestGridLocalizer:
    """
    Test suite validating the structural boundary detection of the grid localizer.

    Responsibility:
        Ensures the localizer accurately calculates topological scales, origins, and
        bounding boxes for grid layouts while appropriately raising documented domain
        errors during invalid states.

    Implementation Details:
        Relies purely on mocked image matrices and computer vision operations. Focuses on
        orchestrating the internal method pipelines, validating both the production (hinted size)
        and legacy (estimated size) mathematical scaling logic natively without actual I/O.
    """

    def setup_method(self):
        """
        Initializes fresh test fixtures preventing state bleed between unit tests.

        Implementation Details:
            Instantiates the primary component alongside a standard mocked multidimensional
            array representing a valid target baseline.
        """
        self.localizer = GridLocalizer()
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """
        Defensively short-circuit on None or empty image input.

        Responsibility:
            Verifies the component actively rejects invalid null payloads before attempting evaluation.

        Implementation Details:
            Passes entirely absent data and intentionally flattened mock objects into the processor,
            asserting that a strict validation error is aggressively raised.
        """
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(None)

        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(empty_image_mock)

    def test_no_board_when_no_panel_and_no_circles(self):
        """
        With a known size but neither a bright panel nor any waypoint discs, the image
        contains no board -> NoBoardDetectedError ("No board detected").

        Responsibility:
            Confirms the system correctly aborts evaluation when standard visual markers
            fail to resolve, rather than generating a randomized origin guess.

        Implementation Details:
            Forcefully overrides internal circle and panel detection methods to yield empty arrays.
            Validates that the component recognizes the lack of reference material and triggers
            the designated error code.
        """
        with (
            patch.object(GridLocalizer, "_detect_circles", return_value=[]),
            patch.object(GridLocalizer, "_panel_bounds", return_value=None),
        ):
            with pytest.raises(ValueError, match="No board detected"):
                self.localizer.localize_grid(self.valid_image_mock, board_size=6)

    # --- KNOWN-SIZE (PRODUCTION) PATH ---

    def test_known_size_uses_panel_geometry(self):
        """
        When board_size is provided and a panel is found, geometry comes straight from
        the panel (side / n) — no size guessing. Cell bounds cover the full n x n grid.

        Responsibility:
            Validates the standard production behavior computing exact mathematical coordinate blocks.

        Implementation Details:
            Mocks panel detection bounding boxes directly and evaluates whether the internal
            mathematical loop appropriately divides the region by the hinted limit, resulting in
            the exact expected number of localized bounds matching the input size.
        """
        # panel at (100,100) 600x600 -> pitch 100 for n=6
        with (
            patch.object(GridLocalizer, "_detect_circles", return_value=[]),
            patch.object(
                GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)
            ),
        ):
            n, cell_bounds = self.localizer.localize_grid(
                self.valid_image_mock, board_size=6
            )

        assert n == 6
        assert len(cell_bounds) == 36  # 6 x 6 cells
        assert (0, 0) in cell_bounds
        assert (5, 5) in cell_bounds
        # top-left cell sits at the panel origin, cell size == pitch
        x, y, w, h = cell_bounds[(0, 0)]
        assert (x, y) == (100, 100)
        assert w == 100 and h == 100

    def test_known_size_rejects_unsupported_size(self):
        """
        A board_size outside {6,7,8} is a caller error -> AmbiguousBoardError.

        Responsibility:
            Asserts dimensional hints are explicitly checked against defined operational constraints.

        Implementation Details:
            Supplies an arbitrary out-of-range structural variable, expecting the localizer
            to defensively break utilizing explicit error terminology.
        """
        with pytest.raises(ValueError, match="Unsupported board size"):
            self.localizer.localize_grid(self.valid_image_mock, board_size=5)

    def test_known_size_refines_origin_from_discs(self):
        """
        Discs inside the footprint are collected for origin refinement. Under mocked
        numpy the arithmetic is a no-op, so this asserts the path runs and still returns a
        complete grid (the numeric refinement itself is covered by the corpus validation).

        Responsibility:
            Ensures spatial refinement loops execute without throwing syntax or state errors.

        Implementation Details:
            Mocks singular circle variables overlapping panel zones. Relies on internal mocked
            objects to bypass the actual math while ensuring the overarching conditional
            block safely exits returning the uncorrupted cell total.
        """
        with (
            patch.object(
                GridLocalizer, "_detect_circles", return_value=[(155.0, 155.0, 30.0)]
            ),
            patch.object(GridLocalizer, "_disc_spacing_pitch", return_value=None),
            patch.object(
                GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)
            ),
        ):
            n, cell_bounds = self.localizer.localize_grid(
                self.valid_image_mock, board_size=6
            )
        assert n == 6
        assert len(cell_bounds) == 36

    def test_known_size_full_board_uses_disc_pitch(self):
        """
        With no panel but several discs, the pitch comes from the disc spacing and the
        origin falls back to the disc extent. Still yields a complete n x n grid.

        Responsibility:
            Proves the localizer securely calculates foundational geometry based entirely
            on node clustering when standard architectural panels remain obscured.

        Implementation Details:
            Overwrites panel detection strictly to nothing, while simultaneously injecting
            a mathematically uniform array of circular nodes. Asserts the extraction
            algorithm still yields the absolute complete matrix.
        """
        discs = [
            (100.0, 100.0, 30.0),
            (200.0, 100.0, 30.0),
            (100.0, 200.0, 30.0),
            (200.0, 200.0, 30.0),
        ]
        with (
            patch.object(GridLocalizer, "_detect_circles", return_value=discs),
            patch.object(GridLocalizer, "_panel_bounds", return_value=None),
            patch.object(GridLocalizer, "_disc_spacing_pitch", return_value=100.0),
        ):
            n, cell_bounds = self.localizer.localize_grid(
                self.valid_image_mock, board_size=6
            )
        assert n == 6
        assert len(cell_bounds) == 36

    # --- LEGACY (NO SIZE HINT) PATH ---

    def test_legacy_bad_size_is_ambiguous(self):
        """
        Without a size hint, an out-of-range edge estimate -> AmbiguousBoardError.

        Responsibility:
            Ensures legacy estimations are clamped safely against established domain rules.

        Implementation Details:
            Forces the native estimation algorithm to yield a mathematically invalid scalar,
            confirming the module rejects the resolution utilizing a domain-specific exception.
        """
        with patch.object(GridLocalizer, "_estimate_size_from_edges", return_value=5):
            with pytest.raises(ValueError, match="size could not be resolved"):
                self.localizer.localize_grid(self.valid_image_mock)

    def test_legacy_good_size_routes_to_geometry(self):
        """
        Without a size hint, a valid edge estimate flows into the same geometry path.

        Responsibility:
            Verifies fallback size generations appropriately chain back into standard math generation.

        Implementation Details:
            Hooks the estimator to output an accepted constant, confirming standard pipeline
            resolution executes exactly as it would given direct production inputs.
        """
        with (
            patch.object(GridLocalizer, "_estimate_size_from_edges", return_value=6),
            patch.object(GridLocalizer, "_detect_circles", return_value=[]),
            patch.object(
                GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)
            ),
        ):
            n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock)
        assert n == 6
        assert len(cell_bounds) == 36
