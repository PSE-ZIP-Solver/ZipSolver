from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

class ImageLoader:
    """Handles safe decoding and normalization of uploaded image bytes."""
    
    def load_and_preprocess(self, image_bytes: bytes) -> "np.ndarray":
        """
        Decodes raw bytes into a usable image array.
        
        HOW IT WORKS:
        1. Fast-Fails if image_bytes is None, empty, or exceeds a strict megabyte limit.
        2. Lazily imports `cv2` and `PIL`.
        3. Uses PIL to safely parse EXIF data and apply rotation corrections.
        4. Decodes to a numpy array, capping the maximum resolution to prevent ML bottlenecks.
           
        Args:
            image_bytes (bytes): Raw uploaded multipart/form-data payload.
            
        Returns:
            np.ndarray: Preprocessed, scaled, and correctly rotated BGR image.
        """
        # MACRO: FAST_FAIL_IF_BYTES_INVALID
        # MACRO: LAZY_IMPORT_CV2_AND_PIL
        # MACRO: PARSE_EXIF_AND_ROTATE
        # MACRO: RESIZE_IF_EXCEEDS_RESOLUTION_CAP
        raise NotImplementedError