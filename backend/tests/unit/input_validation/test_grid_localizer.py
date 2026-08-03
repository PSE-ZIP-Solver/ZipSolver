import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.gird_localizer import GridLocalizer


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Safe Mocking [THE "DANGER ZONE"]:
    Prevents Pytest from globally polluting sys.modules or attempting to load 
    heavy CV/Math dependencies during test collection.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()

    # Define OpenCV constants expected to be used in GridLocalizer
    mock_cv2.RETR_EXTERNAL = 0
    mock_cv2.RETR_LIST = 1
    mock_cv2.CHAIN_APPROX_SIMPLE = 2
    
    mock_cv2.Canny = MagicMock()
    mock_cv2.findContours = MagicMock()
    mock_cv2.approxPolyDP = MagicMock()
    mock_cv2.arcLength = MagicMock()
    mock_cv2.getPerspectiveTransform = MagicMock()
    mock_cv2.warpPerspective = MagicMock()

    # Safely patch sys.modules
    with patch.dict(sys.modules, {
        "numpy": mock_numpy,
        "cv2": mock_cv2
    }):
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2
        }


class TestGridLocalizer:
    
    def setup_method(self):
        """Instantiate a fresh GridLocalizer for each test."""
        self.localizer = GridLocalizer()
        
        # Standard mock for a valid input image
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """Edge Case: Defensively short-circuit on None or empty image input."""
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(None)
            
        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.localizer.localize_grid(empty_image_mock)

    def test_fast_fail_on_no_square_contour_found(self, mock_heavy_dependencies):
        """
        Edge Case: If Canny/findContours cannot find a valid board outline, 
        it must cleanly abort instead of throwing IndexError or Math domain errors.
        """
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        # Simulate finding zero contours
        mock_cv2.findContours.return_value = ([], MagicMock())
        
        with pytest.raises(ValueError, match="Could not detect a valid square puzzle board in the image"):
            self.localizer.localize_grid(self.valid_image_mock)

    @patch.object(GridLocalizer, '_calculate_grid_size', return_value=5)
    def test_fast_fail_on_invalid_grid_size_too_small(self, mock_calc_size, mock_heavy_dependencies):
        """
        Schema Enforcement: Grid size `n` MUST be 6, 7, or 8.
        If a 5x5 grid is detected, it must fast-fail.
        """
        self._setup_successful_contour_mocks(mock_heavy_dependencies["cv2"])
        
        with pytest.raises(ValueError, match="Invalid board size detected: 5. Schema strictly requires 6, 7, or 8."):
            self.localizer.localize_grid(self.valid_image_mock)

    @patch.object(GridLocalizer, '_calculate_grid_size', return_value=9)
    def test_fast_fail_on_invalid_grid_size_too_large(self, mock_calc_size, mock_heavy_dependencies):
        """
        Schema Enforcement: Grid size `n` MUST be 6, 7, or 8.
        If a 9x9 grid is detected, it must fast-fail.
        """
        self._setup_successful_contour_mocks(mock_heavy_dependencies["cv2"])
        
        with pytest.raises(ValueError, match="Invalid board size detected: 9. Schema strictly requires 6, 7, or 8."):
            self.localizer.localize_grid(self.valid_image_mock)

    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    @patch.object(GridLocalizer, '_calculate_grid_size', return_value=6)
    def test_successful_localization_and_routing(self, mock_calc_size, mock_heavy_dependencies):
        """
        Orchestration Test: Validates that OpenCV operations are executed in the correct 
        sequence (Canny -> Contours -> Perspective Warp) and the bounding boxes are mapped.
        """
        mock_cv2 = mock_heavy_dependencies["cv2"]
        mock_numpy = mock_heavy_dependencies["numpy"]
        
        self._setup_successful_contour_mocks(mock_cv2)
        
        # Mock warped image shape (flattened square, e.g., 600x600 pixels)
        mock_warped_image = MagicMock()
        mock_warped_image.shape = (600, 600, 3)
        mock_cv2.warpPerspective.return_value = mock_warped_image

        # Act
        n, cell_bounds = self.localizer.localize_grid(self.valid_image_mock)

        # Assert Routing: OpenCV Edge & Contour Extraction
        mock_cv2.Canny.assert_called_once()
        mock_cv2.findContours.assert_called_once()
        mock_cv2.approxPolyDP.assert_called()
        
        # Assert Routing: Perspective Transform
        mock_cv2.getPerspectiveTransform.assert_called_once()
        mock_cv2.warpPerspective.assert_called_once()
        
        # Assert Grid Math Output
        assert n == 6
        assert isinstance(cell_bounds, dict)
        
        # For a 6x6 grid, there MUST be exactly 36 mapped cells
        assert len(cell_bounds) == 36
        
        # Validate schema of the returned cell bounds map
        for coord, bbox in cell_bounds.items():
            # Coordinate is a Tuple[int, int]
            assert len(coord) == 2
            assert isinstance(coord[0], int)
            assert isinstance(coord[1], int)
            # Bounding box is a Tuple[int, int, int, int] (x, y, w, h)
            assert len(bbox) == 4
            assert all(isinstance(val, int) for val in bbox)
            
        # Specific check: Ensure (0,0) and (5,5) are in the bounds map for an n=6 grid
        assert (0, 0) in cell_bounds
        assert (5, 5) in cell_bounds
        assert (6, 0) not in cell_bounds

    # --- PRIVATE TEST HELPER METHODS ---

    def _setup_successful_contour_mocks(self, mock_cv2):
        """
        Helper method to stub out the OpenCV contour finding process, 
        simulating the successful detection of a 4-point square contour.
        """
        # Mock a 4-point contour (a square)
        mock_contour = MagicMock()
        mock_contour.shape = (4, 1, 2)
        
        # findContours returns (contours, hierarchy)
        mock_cv2.findContours.return_value = ([mock_contour], MagicMock())
        
        # approxPolyDP returns a simplified contour, simulate returning the 4 points
        mock_cv2.approxPolyDP.return_value = mock_contour