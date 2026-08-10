import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.grid_localizer import GridLocalizer


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """Safe Mocking [THE "DANGER ZONE"]: keep heavy CV/Math deps out of collection.

    The localizer lazy-imports cv2/numpy inside its methods. We patch sys.modules so those
    imports resolve to mocks and no native library loads during unit tests.
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
    def setup_method(self):
        self.localizer = GridLocalizer()
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """Defensively short-circuit on None or empty image input."""
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(None)

        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(empty_image_mock)

    def test_no_board_when_no_panel_and_no_circles(self):
        """With a known size but neither a bright panel nor any waypoint discs, the image
        contains no board -> NoBoardDetectedError ("No board detected")."""
        with patch.object(GridLocalizer, "_detect_circles", return_value=[]), \
             patch.object(GridLocalizer, "_panel_bounds", return_value=None):
            with pytest.raises(ValueError, match="No board detected"):
                self.localizer.localize_grid(self.valid_image_mock, board_size=6)

    # --- KNOWN-SIZE (PRODUCTION) PATH ---

    def test_known_size_uses_panel_geometry(self):
        """When board_size is provided and a panel is found, geometry comes straight from
        the panel (side / n) — no size guessing. Cell bounds cover the full n x n grid."""
        # panel at (100,100) 600x600 -> pitch 100 for n=6
        with patch.object(GridLocalizer, "_detect_circles", return_value=[]), \
             patch.object(GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)):
            n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock, board_size=6)

        assert n == 6
        assert len(cell_bounds) == 36           # 6 x 6 cells
        assert (0, 0) in cell_bounds
        assert (5, 5) in cell_bounds
        # top-left cell sits at the panel origin, cell size == pitch
        x, y, w, h = cell_bounds[(0, 0)]
        assert (x, y) == (100, 100)
        assert w == 100 and h == 100

    def test_known_size_rejects_unsupported_size(self):
        """A board_size outside {6,7,8} is a caller error -> AmbiguousBoardError."""
        with pytest.raises(ValueError, match="Unsupported board size"):
            self.localizer.localize_grid(self.valid_image_mock, board_size=5)

    def test_known_size_refines_origin_from_discs(self):
        """Discs inside the footprint are collected for origin refinement. Under mocked
        numpy the arithmetic is a no-op, so this asserts the path runs and still returns a
        complete grid (the numeric refinement itself is covered by the corpus validation)."""
        with patch.object(GridLocalizer, "_detect_circles",
                          return_value=[(155.0, 155.0, 30.0)]), \
             patch.object(GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)):
            n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock, board_size=6)
        assert n == 6
        assert len(cell_bounds) == 36

    def test_known_size_full_board_uses_disc_pitch(self):
        """When no panel is found (board fills the crop) but there are >=4 discs, pitch is
        the median nearest-neighbour disc gap and the origin comes from the disc extent."""
        discs = [(100.0, 100.0, 30.0), (200.0, 100.0, 30.0),
                 (100.0, 200.0, 30.0), (200.0, 200.0, 30.0)]
        with patch.object(GridLocalizer, "_detect_circles", return_value=discs), \
             patch.object(GridLocalizer, "_panel_bounds", return_value=None), \
             patch.object(GridLocalizer, "_nearest_neighbour_pitch", return_value=100.0):
            n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock, board_size=6)
        assert n == 6
        assert len(cell_bounds) == 36

    # --- LEGACY (NO SIZE HINT) PATH ---

    def test_legacy_bad_size_is_ambiguous(self):
        """Without a size hint, an out-of-range edge estimate -> AmbiguousBoardError."""
        with patch.object(GridLocalizer, "_estimate_size_from_edges", return_value=5):
            with pytest.raises(ValueError, match="size could not be resolved"):
                self.localizer.localize_grid(self.valid_image_mock)

    def test_legacy_good_size_routes_to_geometry(self):
        """Without a size hint, a valid edge estimate flows into the same geometry path."""
        with patch.object(GridLocalizer, "_estimate_size_from_edges", return_value=6), \
             patch.object(GridLocalizer, "_detect_circles", return_value=[]), \
             patch.object(GridLocalizer, "_panel_bounds", return_value=(100, 100, 600, 600)):
            n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock)
        assert n == 6
        assert len(cell_bounds) == 36