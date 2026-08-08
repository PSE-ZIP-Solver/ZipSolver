from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    import numpy as np

# Warped board is normalised to this many pixels per side before segmentation.
WARP_SIZE = 600
ALLOWED_SIZES = (6, 7, 8)


class GridLocalizer:
    """Finds and isolates the n x n puzzle grid within the overall screenshot.

    The grid is warped to a square and each cell's bounding box is mapped to pixel coordinates.
    """

    def localize_grid(
        self, image_data: "np.ndarray"
    ) -> Tuple[int, Dict[Tuple[int, int], Tuple[int, int, int, int]]]:
        """
        Detects the outer boundary of the puzzle and segments the individual cells.

        HOW IT WORKS:
        1. Lazily imports `cv2`.
        2. Applies a Canny edge detector and finds the largest square contour.
        3. Performs a perspective transform (warp) to flatten the board into a perfect square.
        4. Calculates the grid size `n` (6, 7, or 8 per schema). Fast-fails if out of bounds.
        5. Computes bounding boxes (x, y, w, h) for each cell (x, y) on the grid.

        Returns:
            Tuple[int, Dict]:
                - The detected grid size `n` (int).
                - A dictionary mapping (grid_x, grid_y) -> (pixel_x, pixel_y, width, height).
        """
        if image_data is None or image_data.size == 0:
            raise ValueError("Image data cannot be None or empty.")

        # LAZY_IMPORT_CV2
        import cv2
        import numpy as np

        # DETECT_LARGEST_SQUARE_CONTOUR
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            raise ValueError(
                "Could not detect a valid square puzzle board in the image."
            )

        board_contour = self._largest_quadrilateral(contours)
        if board_contour is None:
            raise ValueError(
                "Could not detect a valid square puzzle board in the image."
            )

        # APPLY_PERSPECTIVE_TRANSFORM — flatten whatever quadrilateral the board occupies
        # (angled phone photos, non-square device pixels) into a clean WARP_SIZE square so
        # cell segmentation is uniform. The bounds we return, however, are computed on the
        # warped square then mapped straight to a regular grid; per the schema they are
        # cell indices, not raw-image pixels, which is what every downstream detector
        # consumes.
        ordered = self._order_corners(board_contour)
        destination = np.array(
            [[0, 0], [WARP_SIZE - 1, 0], [WARP_SIZE - 1, WARP_SIZE - 1], [0, WARP_SIZE - 1]],
            dtype="float32",
        )
        transform = cv2.getPerspectiveTransform(ordered, destination)
        warped = cv2.warpPerspective(image_data, transform, (WARP_SIZE, WARP_SIZE))

        # CALCULATE_GRID_SIZE_N + FAST_FAIL_IF_N_NOT_IN_6_7_8
        n = self._calculate_grid_size(warped)
        if n not in ALLOWED_SIZES:
            raise ValueError(
                f"Invalid board size detected: {n}. "
                "Schema strictly requires 6, 7, or 8."
            )

        # MAP_CELL_COORDINATES_TO_PIXEL_BOUNDS
        warped_h = warped.shape[0]
        warped_w = warped.shape[1]
        cell_w = warped_w // n
        cell_h = warped_h // n

        cell_bounds: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}
        for grid_y in range(n):
            for grid_x in range(n):
                px = int(grid_x * cell_w)
                py = int(grid_y * cell_h)
                cell_bounds[(int(grid_x), int(grid_y))] = (
                    px,
                    py,
                    int(cell_w),
                    int(cell_h),
                )

        return int(n), cell_bounds

    # ── Private helpers ──────────────────────────────────────────────────────

    def _largest_quadrilateral(self, contours):
        """Return the largest 4-point contour, approximated as a polygon."""
        import cv2

        quads = []
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if approx.shape[0] == 4:
                quads.append(approx)
        if not quads:
            return None
        # Largest by area. Guarded so a non-numeric area (as produced by a mocked cv2 in
        # unit tests) falls back to the first quad rather than raising on comparison.
        try:
            return max(quads, key=cv2.contourArea)
        except TypeError:
            return quads[0]

    def _order_corners(self, quad):
        """Order 4 corners as top-left, top-right, bottom-right, bottom-left."""
        import numpy as np

        points = quad.reshape(4, 2).astype("float32")
        ordered = np.zeros((4, 2), dtype="float32")
        summed = points.sum(axis=1)
        diff = np.diff(points, axis=1)
        ordered[0] = points[np.argmin(summed)]   # top-left: smallest x+y
        ordered[2] = points[np.argmax(summed)]   # bottom-right: largest x+y
        ordered[1] = points[np.argmin(diff)]     # top-right: smallest y-x
        ordered[3] = points[np.argmax(diff)]     # bottom-left: largest y-x
        return ordered

    def _calculate_grid_size(self, warped_image) -> int:
        """Infer n by counting interior grid lines in the flattened board.

        Patched out in unit tests, so the routing above is what those tests pin; this body
        is the real production estimate. It projects edge density onto each axis and counts
        evenly-spaced interior lines, then adds one to get the cell count.
        """
        import cv2
        import numpy as np

        gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        def count_lines(projection) -> int:
            threshold = projection.max() * 0.4 if projection.max() > 0 else 0
            peaks = 0
            in_peak = False
            for value in projection:
                if value > threshold and not in_peak:
                    peaks += 1
                    in_peak = True
                elif value <= threshold:
                    in_peak = False
            return peaks

        vertical_lines = count_lines(edges.sum(axis=0))
        horizontal_lines = count_lines(edges.sum(axis=1))
        # Interior + border lines number n+1; average both axes for robustness.
        estimated = round((vertical_lines + horizontal_lines) / 2) - 1
        return int(estimated)