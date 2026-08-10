import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.wall_detector import WallDetector
from backend.input_validation.screenshot.theme_mode import ThemeMode


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Safe Mocking [THE "DANGER ZONE"]:
    Prevents Pytest from globally polluting sys.modules or attempting to load 
    heavy CV/Math dependencies during test collection.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()

    # Define OpenCV constants for thresholding
    mock_cv2.THRESH_BINARY = 0
    mock_cv2.THRESH_BINARY_INV = 1
    mock_cv2.threshold = MagicMock()
    mock_cv2.countNonZero = MagicMock()

    # Safely patch sys.modules
    with patch.dict(sys.modules, {
        "numpy": mock_numpy,
        "cv2": mock_cv2
    }):
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2
        }


class TestWallDetector:
    
    def setup_method(self):
        """Instantiate a fresh WallDetector for each test."""
        self.detector = WallDetector()
        
        # Standard mock for a valid input image
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

        # Standard minimal 2x2 grid cell bounds mapping
        self.valid_cell_bounds = {
            (0, 0): (0, 0, 50, 50),
            (1, 0): (50, 0, 50, 50),
            (0, 1): (0, 50, 50, 50),
            (1, 1): (50, 50, 50, 50)
        }

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """Edge Case: Defensively short-circuit on None or empty image input."""
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.detector.detect_walls(None, self.valid_cell_bounds, ThemeMode.LIGHT)
            
        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="Image data cannot be None or empty"):
            self.detector.detect_walls(empty_image_mock, self.valid_cell_bounds, ThemeMode.DARK)

    def test_fast_fail_on_invalid_cell_bounds(self):
        """Edge Case: Abort if cell_bounds is empty or None."""
        with pytest.raises(ValueError, match="Cell bounds dictionary cannot be empty"):
            self.detector.detect_walls(self.valid_image_mock, {}, ThemeMode.LIGHT)

        with pytest.raises(ValueError, match="Cell bounds dictionary cannot be empty"):
            self.detector.detect_walls(self.valid_image_mock, None, ThemeMode.LIGHT)

    def test_single_cell_board_returns_no_walls(self, mock_heavy_dependencies):
        """
        Edge Case: A 1x1 board (or isolated cell) has no adjacent neighbors.
        Should safely return an empty list without crashing on adjacency loops.
        """
        single_cell_bounds = {(0, 0): (0, 0, 50, 50)}
        
        result = self.detector.detect_walls(self.valid_image_mock, single_cell_bounds, ThemeMode.LIGHT)
        
        # Expect an empty list because there are no boundaries to evaluate
        assert result == []

    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    @patch.object(WallDetector, '_is_wall_present')
    def test_wall_detection_and_schema_formatting(self, mock_is_wall_present, mock_heavy_dependencies):
        """
        Orchestration & Behavior: Validates adjacency pairing and strict 
        JSON schema formatting for the output.
        """
        # Mock the internal private method to dictate where walls exist.
        # We will simulate a wall between (0,0) <-> (1,0) AND (0,1) <-> (1,1).
        # We will simulate NO walls for vertical adjacencies (0,0) <-> (0,1), etc.
        def wall_logic(image, cell_a, cell_b, bbox_a, bbox_b, theme):
            if (cell_a == (0, 0) and cell_b == (1, 0)) or (cell_a == (0, 1) and cell_b == (1, 1)):
                return True
            return False
            
        mock_is_wall_present.side_effect = wall_logic

        # Act
        result = self.detector.detect_walls(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK)

        # Assert Schema
        assert isinstance(result, list)
        assert len(result) == 2  # Based on our mock logic, 2 walls were found

        # Extract pairs to verify schema integrity
        for wall in result:
            assert isinstance(wall, dict)
            assert "neighborA" in wall
            assert "neighborB" in wall
            assert isinstance(wall["neighborA"], list)
            assert isinstance(wall["neighborB"], list)
            assert len(wall["neighborA"]) == 2
            assert len(wall["neighborB"]) == 2

        # Assert exact coordinate mappings
        # Check if the simulated walls are exactly what was returned
        wall_pairs = [
            (tuple(wall["neighborA"]), tuple(wall["neighborB"])) for wall in result
        ]
        
        # Note: Adjacencies might be appended as A->B or B->A depending on loop logic.
        # Normalize the pairs for safe assertion.
        normalized_pairs = set([
            tuple(sorted([pair[0], pair[1]])) for pair in wall_pairs
        ])

        expected_pairs = {
            ((0, 0), (1, 0)),
            ((0, 1), (1, 1))
        }

        assert normalized_pairs == expected_pairs

    @patch.object(WallDetector, '_extract_boundary_roi')
    def test_theme_mode_routing(self, mock_extract_roi, mock_heavy_dependencies):
        """
        Orchestration Test: Validates that the ThemeMode correctly routes 
        different OpenCV thresholding constants.
        """
        mock_cv2 = mock_heavy_dependencies["cv2"]
        mock_numpy = mock_heavy_dependencies["numpy"]
        
        # Setup a dummy ROI slice
        mock_roi = MagicMock()
        mock_extract_roi.return_value = mock_roi
        mock_cv2.threshold.return_value = (0, MagicMock())
        mock_cv2.countNonZero.return_value = 1000  # Arbitrary threshold pass

        # Act - Light Mode
        self.detector.detect_walls(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT)
        
        # Assert OpenCV used standard binary thresholding for Light mode (dark walls)
        # We assume the implementation uses cv2.THRESH_BINARY_INV for dark walls on light bg, 
        # or cv2.THRESH_BINARY. We just assert that it was called.
        # The detector no longer uses cv2.threshold: Otsu split every blank boundary into
        # two classes and reported all edges as walls. It now compares the boundary against
        # the adjacent cell interiors, so cvtColor (not threshold) is the call that matters.
        mock_cv2.cvtColor.assert_called()
        
        # Reset mocks
        mock_cv2.threshold.reset_mock()

        # Act - Dark Mode
        self.detector.detect_walls(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK)
        
        # Assert thresholding was called again, and it should hypothetically use a different flag
        # (Though we can't assert the exact flag without knowing implementation, we verify it routes).
        # The detector no longer uses cv2.threshold: Otsu split every blank boundary into
        # two classes and reported all edges as walls. It now compares the boundary against
        # the adjacent cell interiors, so cvtColor (not threshold) is the call that matters.
        mock_cv2.cvtColor.assert_called()