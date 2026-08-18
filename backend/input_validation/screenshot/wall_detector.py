from typing import TYPE_CHECKING, Dict, List, Tuple

from backend.input_validation.screenshot.screenshot_errors import UnreadableImageError
from backend.input_validation.screenshot.theme_mode import ThemeMode

if TYPE_CHECKING:
    import numpy as np

# Fraction of the boundary that must read as "heavy" ink for a wall to be present.
WALL_FILL_RATIO = 0.15

# How far a boundary pixel must differ from the adjacent cell interior to count as wall
# ink. Measured: a wall bar differs by ~150 levels, an ordinary grid line by only ~40.
WALL_CONTRAST_DELTA = 80


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
        import numpy as np

        roi = self._extract_boundary_roi(image_data, bbox_a, bbox_b)
        if roi is None or getattr(roi, "size", 0) == 0:
            return False

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Compare the boundary against the two cells it separates rather than against an
        # absolute level or an Otsu split. Otsu always divides a blank sliver into two
        # classes, so every edge looked like a wall; an absolute cut instead depends on
        # theme detection being right, and a misdetected theme inverts the test. The local
        # contrast test is immune to both: a wall bar differs strongly from the cell
        # interior (measured ~150 levels) while the ordinary grid line differs by only ~40.
        try:
            ref = self._cell_reference_level(image_data, bbox_a, bbox_b)
            if ref is None:
                return False
            ink = (int(ref) - gray.astype(np.int16)) > WALL_CONTRAST_DELTA
            filled = int(np.count_nonzero(ink))
            total = int(gray.shape[0] * gray.shape[1])
            if not total:
                return False
            return (filled / total) >= WALL_FILL_RATIO
        except (TypeError, AttributeError, ValueError):
            # Mocked cv2/numpy in unit tests can return non-numeric values.
            return False

    def _cell_reference_level(self, image_data, bbox_a, bbox_b):
        """Median gray of the two cells' interiors — the 'no wall here' baseline."""
        import cv2
        import numpy as np

        samples = []
        for (px, py, w, h) in (bbox_a, bbox_b):
            # Inner core only, so the cell border and any waypoint disc are excluded.
            y0, y1 = int(py + h * 0.3), int(py + h * 0.7)
            x0, x1 = int(px + w * 0.3), int(px + w * 0.7)
            patch = image_data[max(0, y0):y1, max(0, x0):x1]
            if patch is None or getattr(patch, "size", 0) == 0:
                continue
            samples.append(float(np.median(cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY))))
        if not samples:
            return None
        return float(np.median(samples))

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
            half = max(1, aw // 16)
            x0 = max(border_x - half, 0)
            x1 = border_x + half
            return image_data[ay:ay + ah, x0:x1]

        # B is below A -> horizontal shared border at y = ay + ah
        border_y = ay + ah
        half = max(1, ah // 16)
        y0 = max(border_y - half, 0)
        y1 = border_y + half
        return image_data[y0:y1, ax:ax + aw]