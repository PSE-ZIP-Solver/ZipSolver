from typing import TYPE_CHECKING

from backend.input_validation.screenshot.screenshot_errors import UnreadableImageError

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
    """
    Handles safe decoding, orientation correction, and normalization of graphic bytes.

    Responsibility:
        Serves as the secure entry gateway for volatile user-provided payloads, translating 
        multipart forms securely into deterministic mathematical arrays ready for internal 
        vision mapping while preventing memory exhaustion.

    Implementation Details:
        Functions statelessly, applying hard temporal file size and resolution limits directly. 
        Explicitly defers the import of heavy machine learning and graphic libraries directly 
        into execution methods, heavily suppressing application initialization overhead and 
        blocking fatal pipeline exceptions triggered by test discovery tools.
    """

    def load_and_preprocess(self, image_bytes: bytes) -> "np.ndarray":
        """
        Decodes raw transport bytes into a spatially corrected mathematical image structure.

        Args:
            image_bytes: The raw unstructured byte stream extracted from the remote payload.

        Returns:
            A mathematically constrained multi-dimensional array mapping BGR color space.

        Raises:
            UnreadableImageError: If the payload violates absolute volume restrictions, is missing, 
                or fundamentally fails structural pixel decoding protocols.

        Implementation Details:
            Executes defensive volume assertions instantly, halting execution before launching 
            expensive IO interpreters. Translates raw phone camera inputs referencing embedded 
            EXIF metadata to structurally rotate the image into absolute mathematical planes. 
            Resamples massive dimensions iteratively maintaining physical ratios prior to 
            channeling colors back to BGR formatting standard required by internal vision tools.
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