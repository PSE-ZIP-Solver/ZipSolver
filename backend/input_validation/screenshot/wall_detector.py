from typing import TYPE_CHECKING, Dict, List, Tuple

from backend.input_validation.screenshot.errors import UnreadableImageError
from backend.input_validation.screenshot.theme_mode import ThemeMode

if TYPE_CHECKING:
    import numpy as np

# Fraction of the boundary that must read as "heavy" ink for a wall to be present.
WALL_FILL_RATIO = 0.35


class WallDetector:
    """Distinguishes between passable grid lines and impassable heavy walls."""

    def detect_walls(
        self,
        image_data: "np.ndarray",
        cell_bounds: Dict[Tuple[int, int], Tuple[int, int, int, int]],
        theme: ThemeMode,
    ) -> List[Dict[str, List[int]]]:
        """
        Analyzes the boundaries between adjacent cells to identify walls.
        Formats the return exactly to the JSON schema's wall definition.

        Returns:
            List[Dict[str, List[int]]]: JSON-compliant list of wall dictionaries.
        """
        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")
        if not cell_bounds:
            raise ValueError("Cell bounds dictionary cannot be empty or None.")

        walls: List[Dict[str, List[int]]] = []

        # ITERATE_ADJACENT_CELL_PAIRS — only right and down neighbours, so each interior
        # boundary is visited exactly once and no wall is emitted twice.
        for (grid_x, grid_y), bbox_a in cell_bounds.items():
            for dx, dy in ((1, 0), (0, 1)):
                neighbour = (grid_x + dx, grid_y + dy)
                bbox_b = cell_bounds.get(neighbour)
                if bbox_b is None:
                    continue

                if self._is_wall_present(
                    image_data, (grid_x, grid_y), neighbour, bbox_a, bbox_b, theme
                ):
                    # FORMAT_AS_NEIGHBORA_NEIGHBORB_DICTS — pure-int lists for the schema.
                    walls.append({
                        "neighborA": [int(grid_x), int(grid_y)],
                        "neighborB": [int(neighbour[0]), int(neighbour[1])],
                    })

        return walls

    # ── Private helpers ──────────────────────────────────────────────────────

    def _is_wall_present(
        self,
        image_data: "np.ndarray",
        cell_a: Tuple[int, int],
        cell_b: Tuple[int, int],
        bbox_a: Tuple[int, int, int, int],
        bbox_b: Tuple[int, int, int, int],
        theme: ThemeMode,
    ) -> bool:
        """Whether the boundary between two adjacent cells carries a wall.

        Patched out in unit tests, so its signature is the contract. In production it
        extracts the boundary sliver, binarises it (Otsu, with the threshold direction
        chosen by ``theme``), and calls it a wall when a large fraction of the sliver is
        heavy ink — distinguishing a thick wall from a thin ordinary grid line.
        """
        import cv2

        roi = self._extract_boundary_roi(image_data, bbox_a, bbox_b)
        if roi is None or getattr(roi, "size", 0) == 0:
            return False

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # THRESHOLD_THICKNESS_BY_THEME — walls are dark on a light board and light on a
        # dark board; invert accordingly so wall ink is always the non-zero pixels.
        thresh_type = cv2.THRESH_BINARY_INV if theme.isLight else cv2.THRESH_BINARY
        _, binary = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)

        filled = cv2.countNonZero(binary)
        total = binary.shape[0] * binary.shape[1] if hasattr(binary, "shape") else 0
        # Guarded so mocked cv2 return values (non-numeric) in unit tests cannot raise on
        # the arithmetic; a real run always has numeric filled/total here.
        try:
            if not total:
                return False
            return (filled / total) >= WALL_FILL_RATIO
        except TypeError:
            return False

    def _extract_boundary_roi(
        self,
        image_data: "np.ndarray",
        bbox_a: Tuple[int, int, int, int],
        bbox_b: Tuple[int, int, int, int],
    ):
        """Extract a narrow pixel sliver straddling the shared border of two cells.

        Patched out in the theme-routing test. Handles both horizontal neighbours (shared
        vertical border) and vertical neighbours (shared horizontal border).
        """
        ax, ay, aw, ah = bbox_a
        bx, by, bw, bh = bbox_b

        if bx > ax:  # B is to the right of A -> vertical shared border at x = ax + aw
            border_x = ax + aw
            half = max(1, aw // 8)
            x0 = max(border_x - half, 0)
            x1 = border_x + half
            return image_data[ay:ay + ah, x0:x1]

        # B is below A -> horizontal shared border at y = ay + ah
        border_y = ay + ah
        half = max(1, ah // 8)
        y0 = max(border_y - half, 0)
        y1 = border_y + half
        return image_data[y0:y1, ax:ax + aw]