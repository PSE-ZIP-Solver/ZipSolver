import io
import pytest
import sys
from unittest.mock import MagicMock, patch

# Import the class under test. Since ImageLoader lazy-imports its dependencies, 
# this top-level import will NOT crash in a CI/CD environment missing cv2/numpy.
from image_loader import ImageLoader


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Safe Mocking [THE "DANGER ZONE"]:
    Prevents Pytest from globally polluting sys.modules or attempting to load 
    heavy ML/CV dependencies during test collection.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()
    mock_pil = MagicMock()
    mock_pil_image = MagicMock()
    mock_pil_imageops = MagicMock()

    # Link the PIL mock structure so PIL.Image.open and PIL.ImageOps.exif_transpose work
    mock_pil.Image = mock_pil_image
    mock_pil.ImageOps = mock_pil_imageops

    # Safely patch sys.modules
    with patch.dict(sys.modules, {
        "numpy": mock_numpy,
        "cv2": mock_cv2,
        "PIL": mock_pil,
        "PIL.Image": mock_pil_image,
        "PIL.ImageOps": mock_pil_imageops
    }):
        # Yield a dictionary of mocks so individual tests can assert against them
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2,
            "PIL.Image": mock_pil_image,
            "PIL.ImageOps": mock_pil_imageops
        }


class TestImageLoader:
    
    def setup_method(self):
        """Instantiate a fresh ImageLoader for each test."""
        self.loader = ImageLoader()
        self.MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # Assuming 10MB limit

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_bytes(self):
        """Edge Case: Defensively short-circuit on None input."""
        with pytest.raises(ValueError, match="Image bytes cannot be None or empty"):
            self.loader.load_and_preprocess(None)

    def test_fast_fail_on_empty_bytes(self):
        """Edge Case: Defensively short-circuit on empty byte string."""
        with pytest.raises(ValueError, match="Image bytes cannot be None or empty"):
            self.loader.load_and_preprocess(b"")

    def test_fast_fail_on_exceeds_size_limit(self):
        """Edge Case: Prevent memory exhaustion from massive file payloads."""
        oversized_payload = b"0" * (self.MAX_FILE_SIZE_BYTES + 1)
        with pytest.raises(ValueError, match="Image file size exceeds the maximum allowed"):
            self.loader.load_and_preprocess(oversized_payload)

    def test_fast_fail_on_corrupt_image_data(self, mock_heavy_dependencies):
        """Edge Case: Gracefully handle Exception when PIL fails to read the bytes."""
        mock_pil_image = mock_heavy_dependencies["PIL.Image"]
        # Simulate PIL raising an UnidentifiedImageError for garbage bytes
        mock_pil_image.open.side_effect = Exception("Unidentified image")
        
        garbage_bytes = b"definitely_not_a_valid_image_header"
        with pytest.raises(ValueError, match="Failed to decode image data"):
            self.loader.load_and_preprocess(garbage_bytes)

    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    def test_successful_load_and_exif_rotation(self, mock_heavy_dependencies):
        """
        Orchestration Test: Validates that PIL.Image.open, ImageOps.exif_transpose, 
        and numpy/cv2 conversions are routed correctly.
        """
        # 1. Arrange Mocks
        mock_pil_image = mock_heavy_dependencies["PIL.Image"]
        mock_pil_imageops = mock_heavy_dependencies["PIL.ImageOps"]
        mock_numpy = mock_heavy_dependencies["numpy"]
        mock_cv2 = mock_heavy_dependencies["cv2"]
        
        # Mock the opened image and the EXIF transposed image
        mock_opened_image = MagicMock()
        mock_transposed_image = MagicMock()
        mock_transposed_image.size = (800, 600)  # Under the max resolution cap
        mock_transposed_image.convert.return_value = mock_transposed_image
        
        mock_pil_image.open.return_value = mock_opened_image
        mock_pil_imageops.exif_transpose.return_value = mock_transposed_image
        
        # Mock numpy array creation and cv2 BGR conversion
        mock_np_array_instance = MagicMock()
        mock_bgr_array_instance = MagicMock()
        mock_numpy.array.return_value = mock_np_array_instance
        mock_cv2.cvtColor.return_value = mock_bgr_array_instance
        
        # 2. Act
        valid_bytes = b"fake_image_data_here"
        result = self.loader.load_and_preprocess(valid_bytes)
        
        # 3. Assert Routing (Orchestration Testing)
        # Ensure bytes were wrapped in io.BytesIO and passed to PIL
        mock_pil_image.open.assert_called_once()
        args, _ = mock_pil_image.open.call_args
        assert isinstance(args[0], io.BytesIO)
        assert args[0].read() == valid_bytes
        
        # Ensure EXIF transpose was called on the raw opened image
        mock_pil_imageops.exif_transpose.assert_called_once_with(mock_opened_image)
        
        # Ensure it was converted to RGB to strip alpha channels, then to numpy
        mock_transposed_image.convert.assert_called_once_with("RGB")
        mock_numpy.array.assert_called_once_with(mock_transposed_image)
        
        # Ensure cv2 converted RGB to BGR
        mock_cv2.cvtColor.assert_called_once_with(mock_np_array_instance, mock_cv2.COLOR_RGB2BGR)
        
        # Ensure final result matches the BGR array
        assert result == mock_bgr_array_instance

    def test_resizes_if_exceeds_resolution_cap(self, mock_heavy_dependencies):
        """
        Behavioral Test: Validates that high-resolution images are scaled down 
        to prevent downstream ML bottlenecks.
        """
        mock_pil_image = mock_heavy_dependencies["PIL.Image"]
        mock_pil_imageops = mock_heavy_dependencies["PIL.ImageOps"]
        
        mock_opened_image = MagicMock()
        mock_transposed_image = MagicMock()
        
        # Simulate a massive 4K image
        mock_transposed_image.size = (3840, 2160) 
        
        mock_pil_image.open.return_value = mock_opened_image
        mock_pil_imageops.exif_transpose.return_value = mock_transposed_image
        
        valid_bytes = b"fake_4k_image_data"
        self.loader.load_and_preprocess(valid_bytes)
        
        # Assert thumbnail was called to scale down the image safely while maintaining aspect ratio
        mock_transposed_image.thumbnail.assert_called_once()
        
        # Assuming max cap is 1024x1024
        args, kwargs = mock_transposed_image.thumbnail.call_args
        assert args[0][0] <= 1024 and args[0][1] <= 1024
        
        # Assert Resampling filter was used (PIL.Image.Resampling.LANCZOS)
        assert "resample" in kwargs