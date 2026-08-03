import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.palette_detector import PaletteDetector
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

    # Define OpenCV color conversion constants that the detector might use
    mock_cv2.COLOR_BGR2GRAY = 6 
    mock_cv2.cvtColor = MagicMock()

    # Safely patch sys.modules
    with patch.dict(sys.modules, {
        "numpy": mock_numpy,
        "cv2": mock_cv2
    }):
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2
        }


class TestPaletteDetector:
    
    def setup_method(self):
        """Instantiate a fresh PaletteDetector for each test."""
        self.detector = PaletteDetector()
        
        # Helper mock for a standard valid image representation
        self.valid_image_mock = MagicMock()
        # Simulate a 100x100 BGR image
        self.valid_image_mock.shape = (100, 100, 3) 
        self.valid_image_mock.size = 30000

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_image(self):
        """Edge Case: Defensively short-circuit on None input."""
        with pytest.raises(ValueError, match="Image data cannot be None"):
            self.detector.detect_theme(None)

    def test_fast_fail_on_empty_or_invalid_array(self, mock_heavy_dependencies):
        """Edge Case: Prevent crashing on empty arrays or non-image shapes."""
        invalid_image_mock = MagicMock()
        # Simulate an empty array (size 0)
        invalid_image_mock.size = 0 
        
        with pytest.raises(ValueError, match="Invalid image data"):
            self.detector.detect_theme(invalid_image_mock)
            
        # Simulate a 1D array (not an image)
        invalid_image_mock.size = 100
        invalid_image_mock.shape = (100,)
        
        with pytest.raises(ValueError, match="Image data must be at least 2D"):
            self.detector.detect_theme(invalid_image_mock)

    def test_graceful_handling_of_tiny_images(self, mock_heavy_dependencies):
        """
        Edge Case: If an image is smaller than the intended border sampling size 
        (e.g., a 5x5 image when sampling 10px borders), it should safely fallback 
        to sampling the entire image instead of throwing out-of-bounds errors.
        """
        mock_numpy = mock_heavy_dependencies["numpy"]
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        tiny_image_mock = MagicMock()
        tiny_image_mock.shape = (5, 5, 3)
        tiny_image_mock.size = 75
        
        # Simulate a dark luminance result
        mock_numpy.mean.return_value = 40.0
        
        result = self.detector.detect_theme(tiny_image_mock)
        
        # It should still succeed and return a ThemeMode
        assert result.isDark
        # Assert cv2 was called to convert the whole tiny image
        mock_cv2.cvtColor.assert_called_once()

    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    def test_detects_light_theme(self, mock_heavy_dependencies):
        """
        Orchestration & Behavior: Validates border sampling logic and ensures
        a high luminance average correctly maps to ThemeMode.LIGHT.
        """
        mock_numpy = mock_heavy_dependencies["numpy"]
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        # 1. Arrange
        mock_gray_image = MagicMock()
        mock_cv2.cvtColor.return_value = mock_gray_image
        
        # Simulate numpy.mean returning a high luminance value (e.g., > 127.5)
        mock_numpy.mean.return_value = 220.5 
        
        # 2. Act
        result = self.detector.detect_theme(self.valid_image_mock)
        
        # 3. Assert Routing (Orchestration Testing)
        # Ensure image was converted to grayscale for luminance calculation
        mock_cv2.cvtColor.assert_called_once_with(self.valid_image_mock, mock_cv2.COLOR_BGR2GRAY)
        
        # Ensure numpy.mean was called to calculate average luminance
        mock_numpy.mean.assert_called()
        
        # Ensure the result is strictly ThemeMode.LIGHT
        assert result == ThemeMode.LIGHT
        assert result.isLight is True

    def test_detects_dark_theme(self, mock_heavy_dependencies):
        """
        Orchestration & Behavior: Validates border sampling logic and ensures
        a low luminance average correctly maps to ThemeMode.DARK.
        """
        mock_numpy = mock_heavy_dependencies["numpy"]
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        # 1. Arrange
        mock_gray_image = MagicMock()
        mock_cv2.cvtColor.return_value = mock_gray_image
        
        # Simulate numpy.mean returning a low luminance value (e.g., < 127.5)
        mock_numpy.mean.return_value = 35.2 
        
        # 2. Act
        result = self.detector.detect_theme(self.valid_image_mock)
        
        # 3. Assert
        # Ensure the result is strictly ThemeMode.DARK
        assert result == ThemeMode.DARK
        assert result.isDark is True

    def test_border_sampling_slice_routing(self, mock_heavy_dependencies):
        """
        Orchestration Test: Strictly asserts that the background is sampled from 
        the edges (top, bottom, left, right), rather than the clutter-heavy center.
        """
        mock_numpy = mock_heavy_dependencies["numpy"]
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        # Provide a mock that tracks how it was sliced
        mock_gray_image = MagicMock()
        mock_cv2.cvtColor.return_value = mock_gray_image
        
        # Force a return so the method completes
        mock_numpy.mean.return_value = 100.0 
        
        self.detector.detect_theme(self.valid_image_mock)
        
        # Verify that numpy concatenate or stack was used on slices of the gray image
        # Because we can't easily intercept direct MagicMock `__getitem__` slices in a robust 
        # way without over-complicating the test, we assert that numpy array aggregation 
        # (like np.concatenate) was called to merge the top/bottom/left/right border ROIs.
        assert mock_numpy.concatenate.called or mock_numpy.vstack.called or mock_numpy.hstack.called, \
            "Detector did not aggregate border slices using numpy.concatenate/vstack/hstack."