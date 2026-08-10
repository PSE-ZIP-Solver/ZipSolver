from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from backend.input_validation.screenshot.errors import ScreenshotError
from backend.input_validation.screenshot.errors import UnreadableImageError
from backend.input_validation.screenshot.theme_mode import ThemeMode

if TYPE_CHECKING:
    import numpy as np


class WaypointDetectionError(ScreenshotError):
    """Raised when waypoints cannot be fully or sequentially resolved.

    A board was located and sized, but its numerals are inconsistent — an unreadable
    marker, a gap in the sequence, or a duplicate. 422 with INVALID_WAYPOINTS, matching
    the semantic-waypoint failures the validator raises, so the frontend handles both the
    same way.
    """

    code = "INVALID_WAYPOINTS"
    http_status = 422


class WaypointDetector:
    """Identifies and reads the numerals inside grid cells (Waypoints)."""

    def detect_waypoints(
        self,
        image_data: "np.ndarray",
        cell_bounds: Dict[Tuple[int, int], Tuple[int, int, int, int]],
        theme: ThemeMode,
    ) -> List[List[int]]:
        """
        Scans all localized cells to detect markers and reads their sequential numbers.
        Formats the return exactly to the JSON schema: ordered List[[x, y]].

        Returns:
            List[List[int]]: A list of [x, y] coordinates, where the index in the list
                             represents the strict sequential visit order.

        Raises:
            WaypointDetectionError: If OCR fails on a marker or if a sequence number is missing.
        """
        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")
        if not cell_bounds:
            raise ValueError("Cell bounds dictionary cannot be empty or None.")

        # ITERATE_CELLS_AND_MASK_MARKERS — read every cell; a cell with no marker returns
        # None and is skipped. numeral -> the cell that carried it.
        numeral_to_cell: Dict[int, Tuple[int, int]] = {}
        for (grid_x, grid_y), bbox in cell_bounds.items():
            raw = self._detect_marker_and_read(image_data, bbox, theme)
            if raw is None:
                continue

            # RAISE_EXCEPTION_IF_OCR_FAILS_ON_DETECTED_MARKER — a detected-but-unreadable
            # marker (OCR returned '?' or something non-numeric) is a hard error: the board
            # cannot be trusted, so we refuse rather than silently drop a waypoint.
            numeral = self._unbox_numeral(raw)
            if numeral is None:
                raise WaypointDetectionError(
                    f"Failed to read an invalid numeral at cell ({grid_x}, {grid_y})."
                )

            # RAISE on duplicates — two cells reading the same number means a misread.
            if numeral in numeral_to_cell:
                raise WaypointDetectionError(
                    f"Duplicate waypoint numeral detected: {numeral}."
                )
            numeral_to_cell[numeral] = (int(grid_x), int(grid_y))

        if not numeral_to_cell:
            return []

        # RAISE_EXCEPTION_IF_SEQUENCE_IS_BROKEN_OR_MISSING — numerals must be exactly
        # 1..k with no gaps, since the list index encodes visit order downstream.
        numerals = sorted(numeral_to_cell)
        expected = list(range(1, len(numerals) + 1))
        if numerals != expected:
            missing = sorted(set(expected) - set(numerals))
            raise WaypointDetectionError(
                "Missing waypoint in sequence (gap detected): "
                f"expected 1..{len(numerals)}, missing {missing}."
            )

        # SORT_COORDINATES_BY_NUMERAL then RETURN_ORDERED_LIST_OF_LISTS with the numerals
        # stripped — pure Python ints so json.dumps cannot choke on a boxed scalar.
        return [
            [int(numeral_to_cell[n][0]), int(numeral_to_cell[n][1])] for n in numerals
        ]

    # ── Private helpers ──────────────────────────────────────────────────────

    def _detect_marker_and_read(
        self,
        image_data: "np.ndarray",
        bbox: Tuple[int, int, int, int],
        theme: ThemeMode,
    ):
        """Detect a marker in one cell and OCR its numeral.

        Patched out in unit tests, so its exact signature (image, bbox, theme) is the
        contract. In production it lazily loads the OCR stack, crops the cell, isolates the
        marker using ``theme`` to pick contrast direction, and returns the raw OCR result
        (which the caller unboxes). Returns None when the cell has no marker.
        """
        # LAZY_IMPORT_ML_OCR_MODELS — never at module top level.
        import cv2
        import numpy as np

        px, py, w, h = bbox
        cell = image_data[py:py + h, px:px + w]
        if cell is None or getattr(cell, "size", 0) == 0:
            return None

        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        # Dark numerals on a light marker, or the reverse in dark mode: invert so the glyph
        # is always bright for the OCR pass.
        thresh_type = cv2.THRESH_BINARY_INV if theme.isLight else cv2.THRESH_BINARY
        _, binary = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)

        if cv2.countNonZero(binary) == 0:
            return None  # no marker ink in this cell

        try:
            import pytesseract

            text = pytesseract.image_to_string(
                binary,
                config="--psm 10 -c tessedit_char_whitelist=0123456789",
            ).strip()
        except Exception:  # noqa: BLE001 - OCR backend unavailable or failed
            return "?"

        return text if text else None

    def _unbox_numeral(self, raw) -> Optional[int]:
        """Cast an OCR/ML result to a pure Python int, or None if it is not a numeral.

        Handles boxed tensor/scalar types (``.item()``), objects castable via ``int()``,
        and numeric strings. Anything else (notably '?') returns None so the caller raises.
        """
        if raw is None:
            return None
        if isinstance(raw, bool):
            return None

        # Boxed scalar/tensor with .item()
        item = getattr(raw, "item", None)
        if callable(item):
            try:
                value = item()
                if value is raw:
                 return None
                return self._unbox_numeral(value)
            except (TypeError, ValueError):
                return None

        if isinstance(raw, int):
            return int(raw)

        if isinstance(raw, str):
            stripped = raw.strip()
            if stripped.isdigit():
                return int(stripped)
            return None

        # Custom objects implementing __int__ (e.g. numpy scalars, MockTensor)
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None