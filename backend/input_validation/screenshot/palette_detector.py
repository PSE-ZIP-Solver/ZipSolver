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
    """
    Evaluates global pixel contrast maps to dictate subsequent mathematical vision bounds.

    Responsibility:
        Establishes the foundational lighting model to inform adaptive vision algorithms,
        ensuring downstream thresholding operations accurately isolate markers irrespective
        of internal application color swaps.

    Implementation Details:
        Acts statelessly. Identifies structural themes implicitly relying purely upon luminance
        sums sampled strategically from external boundary margins, completely stripping color
        spaces before executing to minimize array processing.
    """

    def detect_theme(self, image_data: "np.ndarray") -> ThemeMode:
        """
        Determines the dominant brightness baseline to establish structural color themes.

        Args:
            image_data: The absolute targeted matrix representing normalized pixel values.

        Returns:
            The structured enumeration flagging the definitively matched color environment.

        Raises:
            UnreadableImageError: If the evaluated payload strictly lacks multidimensional boundaries.

        Implementation Details:
            Flattens incoming data directly to single-channel grayscale scales immediately to
            slash evaluation dimensions. Truncates internal slices from boundary edges directly
            calculating overarching luminance via statistical means. Compares absolute luminance
            sums against localized thresholds yielding distinct execution states.
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
            border_values = np.concatenate(
                (
                    gray[:BORDER_SAMPLE, :].reshape(-1),
                    gray[-BORDER_SAMPLE:, :].reshape(-1),
                    gray[:, :BORDER_SAMPLE].reshape(-1),
                    gray[:, -BORDER_SAMPLE:].reshape(-1),
                )
            )
            luminance = np.mean(border_values)

        # RETURN_THEME_BASED_ON_THRESHOLD
        if luminance > LUMINANCE_THRESHOLD:
            return ThemeMode.LIGHT
        return ThemeMode.DARK
