from typing import TYPE_CHECKING

from backend.input_validation.screenshot.screenshot_errors import UnreadableImageError
from backend.input_validation.screenshot.theme_mode import ThemeMode

if TYPE_CHECKING:
    import numpy as np

# Border thickness (px) sampled to estimate the page colour.
BORDER_SAMPLE = 10
# Midpoint of the 0-255 luminance range; above this the background is light.
LUMINANCE_THRESHOLD = 127.5


class PaletteDetector:
    """Determines the color scheme of the puzzle to adjust downstream thresholds."""

    def detect_theme(self, image_data: "np.ndarray") -> ThemeMode:
        """
        Detects if the screenshot is in Light Mode or Dark Mode.

        HOW IT WORKS:
        1. Lazily imports `cv2` and `numpy`.
        2. Samples the background color (typically the border edges of the image).
        3. Calculates the average luminance of the sampled pixels.
        4. Compares luminance against a predefined threshold to map to ThemeMode.

        Args:
            image_data (np.ndarray): The normalized screenshot array.

        Returns:
            ThemeMode: Enum indicating the detected theme.
        """
        # Fast-fail before importing anything heavy.
        if image_data is None:
            raise UnreadableImageError("Image data cannot be None.")
        if image_data.size == 0:
            raise UnreadableImageError("Invalid image data (empty array).")
        if len(image_data.shape) < 2:
            raise UnreadableImageError("Image data must be at least 2D.")

        # LAZY_IMPORT_CV2_AND_NUMPY
        import cv2
        import numpy as np

        # Convert the whole image to grayscale once; luminance is a brightness question,
        # so colour is not needed past this point.
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)

        # CALCULATE_LUMINANCE from the border, where the page background shows through and
        # the board does not intrude. On an image too small to carve a border out of, fall
        # back to averaging the whole thing rather than indexing out of bounds.
        height = image_data.shape[0]
        width = image_data.shape[1]
        if height <= 2 * BORDER_SAMPLE or width <= 2 * BORDER_SAMPLE:
            luminance = np.mean(gray)
        else:
            border_values = np.concatenate((
                gray[:BORDER_SAMPLE, :].reshape(-1),
                gray[-BORDER_SAMPLE:, :].reshape(-1),
                gray[:, :BORDER_SAMPLE].reshape(-1),
                gray[:, -BORDER_SAMPLE:].reshape(-1),
            ))
            luminance = np.mean(border_values)

        # RETURN_THEME_BASED_ON_THRESHOLD
        if luminance > LUMINANCE_THRESHOLD:
            return ThemeMode.LIGHT
        return ThemeMode.DARK