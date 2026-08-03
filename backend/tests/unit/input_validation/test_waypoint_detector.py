import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.theme_mode import ThemeMode

# Assuming WaypointDetectionError is defined in the same module as WaypointDetector
from backend.input_validation.screenshot.waypoint_detector import (
    WaypointDetector, 
    WaypointDetectionError
)

@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Safe Mocking [THE "DANGER ZONE"]:
    Strictly prevents Pytest from polluting sys.modules or loading heavy 
    ML/CV libraries (torch, easyocr, cv2) during test collection in CI/CD environments.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()
    mock_torch = MagicMock()
    mock_easyocr = MagicMock()

    # Safely patch sys.modules
    with patch.dict(sys.modules, {
        "numpy": mock_numpy,
        "cv2": mock_cv2,
        "torch": mock_torch,
        "easyocr": mock_easyocr
    }):
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2,
            "torch": mock_torch,
            "easyocr": mock_easyocr
        }


class MockTensor:
    """
    Utility class to simulate Stable-Baselines/Torch Tensors or NumPy scalars.
    Ensures that our unboxing logic actually casts custom objects to pure Python ints.
    """
    def __init__(self, value):
        self._value = value
        
    def item(self):
        return self._value
        
    def __int__(self):
        return int(self._value)


class TestWaypointDetector:

    def setup_method(self):
        """Instantiate a fresh WaypointDetector and setup valid stubs for each test."""
        self.detector = WaypointDetector()
        
        # Standard mock for a valid input image (numpy array abstraction)
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

        # Standard minimal 2x2 grid cell bounds mapping (x, y) -> (px, py, w, h)
        self.valid_cell_bounds = {
            (0, 0): (0, 0, 50, 50),
            (1, 0): (50, 0, 50, 50),
            (0, 1): (0, 50, 50, 50),
            (1, 1): (50, 50, 50, 50)
        }

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """Edge Case: Defensively short-circuit on None or empty image input."""
        with pytest.raises(ValueError, match="(?i)image.*none|empty"):
            self.detector.detect_waypoints(None, self.valid_cell_bounds, ThemeMode.LIGHT)
            
        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="(?i)image.*none|empty"):
            self.detector.detect_waypoints(empty_image_mock, self.valid_cell_bounds, ThemeMode.DARK)

    def test_fast_fail_on_invalid_cell_bounds(self):
        """Edge Case: Abort immediately if cell_bounds is empty or None."""
        with pytest.raises(ValueError, match="(?i)cell bounds.*empty|none"):
            self.detector.detect_waypoints(self.valid_image_mock, {}, ThemeMode.LIGHT)

        with pytest.raises(ValueError, match="(?i)cell bounds.*empty|none"):
            self.detector.detect_waypoints(self.valid_image_mock, None, ThemeMode.LIGHT)


    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    @patch.object(WaypointDetector, '_detect_marker_and_read', create=True)
    def test_waypoint_extraction_sorting_and_unboxing(self, mock_read, mock_heavy_dependencies):
        """
        Orchestration (Happy Path): 
        1. Ensures out-of-order markers are correctly sorted by numeral.
        2. Ensures numerals are stripped from the final array (`List[[x, y]]`).
        3. STRICT REQUIREMENT: Ensures ML tensors are unboxed to pure Python `int`.
        """
        def mock_ocr_logic(image, bbox, theme):
            # Simulate detecting numbers out-of-order, and leaving one cell empty
            if bbox == (0, 0, 50, 50):       # Cell (0,0)
                return MockTensor(2)         # Found '2', returning as a mock Tensor
            elif bbox == (0, 50, 50, 50):    # Cell (0,1)
                return MockTensor(1)         # Found '1', returning as a mock Tensor
            elif bbox == (50, 50, 50, 50):   # Cell (1,1)
                return MockTensor(3)         # Found '3', returning as a mock Tensor
            return None                      # Cell (1,0) has no waypoint

        mock_read.side_effect = mock_ocr_logic

        # Act
        result = self.detector.detect_waypoints(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT)

        # Assert correct sorting (1st is at [0,1], 2nd is at [0,0], 3rd is at [1,1])
        # Assert format matches JSON schema (numerals stripped, List[[x, y]])
        assert result == [[0, 1], [0, 0], [1, 1]]

        # Assert STRICT Type Unboxing (Must be pure Python int, not MockTensor or Numpy Scalar)
        for point in result:
            assert type(point[0]) is int
            assert type(point[1]) is int


    @patch.object(WaypointDetector, '_detect_marker_and_read', create=True)
    def test_no_waypoints_returns_empty_list(self, mock_read, mock_heavy_dependencies):
        """Edge Case: An empty board (no waypoints detected) should gracefully return []"""
        mock_read.return_value = None  # Simulate no markers found anywhere
        
        result = self.detector.detect_waypoints(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK)
        
        assert result == []


    # --- EXCEPTION BUBBLING TESTS ---

    @patch.object(WaypointDetector, '_detect_marker_and_read', create=True)
    def test_missing_sequence_gap_raises_exception(self, mock_read, mock_heavy_dependencies):
        """
        Exception Bubbling: If OCR reads [1, 3] but misses 2, 
        it MUST explicitly raise WaypointDetectionError.
        """
        def mock_ocr_logic(image, bbox, theme):
            if bbox == (0, 0, 50, 50): return 1
            if bbox == (50, 50, 50, 50): return 3
            return None

        mock_read.side_effect = mock_ocr_logic

        with pytest.raises(WaypointDetectionError, match="(?i)missing.*sequence|gap"):
            self.detector.detect_waypoints(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT)


    @patch.object(WaypointDetector, '_detect_marker_and_read', create=True)
    def test_unreadable_ocr_marker_raises_exception(self, mock_read, mock_heavy_dependencies):
        """
        Exception Bubbling: If a marker is detected (e.g., Hough Circles finds it) 
        but OCR reads '?' or nothing, it MUST explicitly raise WaypointDetectionError.
        """
        def mock_ocr_logic(image, bbox, theme):
            if bbox == (0, 0, 50, 50): return '?'  # Detected, but failed to interpret
            return None

        mock_read.side_effect = mock_ocr_logic

        with pytest.raises(WaypointDetectionError, match="(?i)unreadable|failed to read|invalid numeral"):
            self.detector.detect_waypoints(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK)


    @patch.object(WaypointDetector, '_detect_marker_and_read', create=True)
    def test_duplicate_waypoints_raises_exception(self, mock_read, mock_heavy_dependencies):
        """
        Exception Bubbling: If the ML incorrectly predicts the same number twice (e.g. [1, 1]),
        it MUST explicitly raise WaypointDetectionError.
        """
        def mock_ocr_logic(image, bbox, theme):
            if bbox == (0, 0, 50, 50): return 1
            if bbox == (50, 0, 50, 50): return 1
            return None

        mock_read.side_effect = mock_ocr_logic

        with pytest.raises(WaypointDetectionError, match="(?i)duplicate"):
            self.detector.detect_waypoints(self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT)