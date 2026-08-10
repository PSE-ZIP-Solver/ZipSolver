from typing import TYPE_CHECKING

from backend.input_validation.screenshot.errors import UnreadableImageError

if TYPE_CHECKING:
    import numpy as np

# 10 MB. Screenshots of a puzzle board are small; anything larger is either a mistake
# or an attempt to exhaust memory, so it is rejected before any decode work happens.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Longest edge fed downstream. A board only needs a few hundred pixels per cell to read
# cleanly, so a 4K/5K monitor capture is scaled down first — smaller images make every
# later CV stage faster without costing OCR accuracy at these grid sizes.
MAX_DIMENSION = 2048


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
        # FAST_FAIL_IF_BYTES_INVALID — before importing anything heavy.
        if image_bytes is None or len(image_bytes) == 0:
            raise UnreadableImageError("Image bytes cannot be None or empty.")
        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            raise UnreadableImageError("Image file size exceeds the maximum allowed.")

        # LAZY_IMPORT_CV2_AND_PIL — kept inside the method so importing this module (e.g.
        # during test collection) never drags in cv2/PIL. See the "danger zone" rules.
        import io

        import cv2
        import numpy as np
        from PIL import Image, ImageOps

        # PARSE_EXIF_AND_ROTATE — phone photos store orientation as an EXIF tag rather
        # than rotated pixels; exif_transpose bakes that rotation in so the board is
        # upright before any geometry is measured.
        try:
            opened = Image.open(io.BytesIO(image_bytes))
            transposed = ImageOps.exif_transpose(opened)

            # RESIZE_IF_EXCEEDS_RESOLUTION_CAP — done on the oriented image, before the
            # RGB conversion, so the expensive convert/array steps operate on the smaller
            # image. thumbnail preserves aspect ratio and only ever shrinks, so images
            # already under the cap pass through untouched.
            width, height = transposed.size
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                transposed.thumbnail(
                    (MAX_DIMENSION, MAX_DIMENSION), resample=Image.Resampling.LANCZOS
                )

            rgb = transposed.convert("RGB")
        except UnreadableImageError:
            raise
        except Exception as exc:  # noqa: BLE001 - any decode failure maps to one message
            raise UnreadableImageError("Failed to decode image data.") from exc

        rgb_array = np.array(rgb)
        bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return bgr