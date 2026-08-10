from typing import TYPE_CHECKING, Dict, Optional, Tuple

from backend.input_validation.screenshot.errors import (
    AmbiguousBoardError,
    NoBoardDetectedError,
    UnreadableImageError,
)

if TYPE_CHECKING:
    import numpy as np

ALLOWED_SIZES = (6, 7, 8)


class GridLocalizer:
    """Finds and isolates the n x n puzzle grid within the overall screenshot.

    Two modes:
      - board_size provided (production path): the frontend already knows which size the
        user selected, so it is passed straight through. Geometry then reduces to finding
        the board's square bounds and dividing by n — reliable, no fragile size guessing.
      - board_size omitted (legacy / unit-test path): falls back to edge-based size
        estimation. Kept so the existing localizer tests, which mock all CV, still exercise
        the same routing.

    Localization is anchored on the orange waypoint discs, which are the highest-saturation
    features on the board and therefore the most reliable landmark. Their spacing and the
    bright board panel together fix the grid origin and cell pitch. See the screenshot
    corpus work for why line-based detection alone was insufficient on the app's own
    low-contrast rendering.
    """

    def localize_grid(
        self,
        image_data: "np.ndarray",
        board_size: Optional[int] = None,
    ) -> Tuple[int, Dict[Tuple[int, int], Tuple[int, int, int, int]]]:
        """
        Detects the board and segments the individual cells.

        Args:
            image_data: normalised BGR screenshot.
            board_size: the known grid size (6, 7, or 8) supplied by the frontend. When
                given it is authoritative; when None the size is estimated from the image.

        Returns:
            (grid_size, cell_bounds) where cell_bounds maps (grid_x, grid_y) ->
            (pixel_x, pixel_y, width, height).
        """
        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")

        import cv2  # noqa: F401  (lazy import; used by helpers)
        import numpy as np

        self.last_waypoint_cells: Dict[Tuple[int, int], Tuple[float, float, float]] = {}

        if board_size is not None:
            if board_size not in ALLOWED_SIZES:
                raise AmbiguousBoardError(
                    f"Unsupported board size {board_size}; expected 6, 7, or 8."
                )
            origin_x, origin_y, pitch = self._solve_geometry(image_data, board_size)
            return board_size, self._cell_bounds(board_size, origin_x, origin_y, pitch)

        # ── Legacy size-estimation path (no size hint) ───────────────────────
        n = self._estimate_size_from_edges(image_data)
        if n not in ALLOWED_SIZES:
            raise AmbiguousBoardError(
                "A grid was found but its size could not be resolved to 6x6, 7x7, or "
                f"8x8 (estimated {n}). Provide the board size or use a clearer screenshot."
            )
        origin_x, origin_y, pitch = self._solve_geometry(image_data, n)
        return n, self._cell_bounds(n, origin_x, origin_y, pitch)

    # ── Geometry ─────────────────────────────────────────────────────────────

    def _solve_geometry(self, image_data, n: int) -> Tuple[float, float, float]:
        """Return (origin_x, origin_y, pitch) for an n x n board.

        Strategy (validated against the real-screenshot corpus):
          1. Detect orange waypoint discs.
          2. Find the bright square board panel; when found its side / n is the pitch and
             its centre fixes the origin.
          3. When no panel is found (board fills the crop) but there are enough discs,
             derive the pitch from the median nearest-neighbour disc gap.
          4. Refine the origin so disc centres land on cell centres.
        """
        import numpy as np

        circles = self._detect_circles(image_data)
        panel = self._panel_bounds(image_data, circles)

        # Discs sit at cell centres, so the spacing between distinct disc columns/rows is a
        # direct, reliable pitch measurement — more trustworthy than the panel bounds, which
        # can be over-sized by surrounding chrome. When enough discs are present, use their
        # spacing; otherwise fall back to the panel, then to disc radius.
        board_circles = [c for c in circles if c[2] < 40]  # drop oversized UI blobs
        disc_pitch = self._disc_spacing_pitch(board_circles) if len(board_circles) >= 6 else None

        if disc_pitch is not None:
            pitch = disc_pitch
            # Origin from the discs themselves: the smallest disc coordinate is a cell
            # centre, so the board origin is that minus half a pitch, snapped so all discs
            # land on integer cells. Using the panel centre here is unreliable because the
            # panel can be mis-sized; the discs are the ground truth for cell positions.
            min_cx = min(c[0] for c in board_circles)
            min_cy = min(c[1] for c in board_circles)
            origin_x = min_cx - pitch / 2.0
            origin_y = min_cy - pitch / 2.0
        elif panel is not None:
            px, py, pw, ph = panel
            centre_x = px + pw / 2.0
            centre_y = py + ph / 2.0
            pitch = (pw + ph) / 2.0 / n
            origin_x = centre_x - n * pitch / 2.0
            origin_y = centre_y - n * pitch / 2.0
        elif len(circles) >= 4:
            pitch = self._nearest_neighbour_pitch(circles)
            origin_x = min(c[0] for c in circles) - pitch / 2.0
            origin_y = min(c[1] for c in circles) - pitch / 2.0
        elif circles:
            # A disc nearly fills a cell; ~0.72 of the pitch is a measured constant.
            pitch = 2.0 * float(np.median([c[2] for c in circles])) / 0.72
            origin_x = min(c[0] for c in circles) - pitch / 2.0
            origin_y = min(c[1] for c in circles) - pitch / 2.0
        else:
            raise NoBoardDetectedError(
                "No board detected. Point the camera at a Zip puzzle grid, "
                "or crop the screenshot closer to the board."
            )

        # Refine origin using discs that fall within the board footprint (drops UI
        # false-positives such as an orange button in the surrounding chrome).
        board = [
            (cx, cy, r)
            for (cx, cy, r) in circles
            if origin_x - pitch * 0.3 <= cx <= origin_x + pitch * (n + 0.3)
            and origin_y - pitch * 0.3 <= cy <= origin_y + pitch * (n + 0.3)
        ]
        if board:
            cxs = np.array([c[0] for c in board])
            cys = np.array([c[1] for c in board])
            rx = (cxs - origin_x) / pitch - 0.5
            ry = (cys - origin_y) / pitch - 0.5
            origin_x += float(np.median(rx - np.round(rx))) * pitch
            origin_y += float(np.median(ry - np.round(ry))) * pitch

        # Record the reliable disc -> cell mapping from GLOBAL circle detection, using the
        # final origin/pitch. The per-cell re-detection in the waypoint detector misses
        # discs that straddle cell boundaries; these globally-detected centres do not, so
        # the extractor prefers them. Map each disc centre to its cell and keep the pixel
        # centre so the digit reader can crop precisely around the disc.
        self.last_waypoint_cells: Dict[Tuple[int, int], Tuple[float, float, float]] = {}
        for (cx, cy, r) in board:
            col = int(round((cx - origin_x) / pitch - 0.5))
            row = int(round((cy - origin_y) / pitch - 0.5))
            if 0 <= col < n and 0 <= row < n:
                self.last_waypoint_cells[(col, row)] = (cx, cy, r)

        return origin_x, origin_y, pitch

    def _detect_circles(self, image_data):
        """Detect orange waypoint discs. Returns list of (cx, cy, radius)."""
        import cv2
        import numpy as np

        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        mask = ((hue > 5) & (hue < 30) & (sat > 120) & (val > 120)).astype(np.uint8) * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 300:
                continue
            (cx, cy), r = cv2.minEnclosingCircle(c)
            if area / (np.pi * r * r) > 0.6:  # reasonably circular
                out.append((float(cx), float(cy), float(r)))
        return out

    def _panel_bounds(self, image_data, circles):
        """Largest bright, near-square region that contains the discs' centroid."""
        import cv2
        import numpy as np

        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        bright = (gray >= 244).astype(np.uint8) * 255
        bright = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
        bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((31, 31), np.uint8))
        contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        ccx = float(np.median([c[0] for c in circles])) if circles else None
        ccy = float(np.median([c[1] for c in circles])) if circles else None

        best = None
        for c in contours:
            x, y, ww, hh = cv2.boundingRect(c)
            if ww * hh < w * h * 0.04:
                continue
            if not (0.8 < ww / hh < 1.25):
                continue
            if (
                ccx is not None
                and ccy is not None
                and not (x <= ccx <= x + ww and y <= ccy <= y + hh)
            ):
                continue
            if best is None or ww * hh > best[0]:
                best = (ww * hh, x, y, ww, hh)
        return best[1:] if best else None

    def _disc_spacing_pitch(self, circles):
        """Pitch from the spacing of distinct disc columns and rows.

        Discs sit at cell centres, so clustering their x (and y) coordinates into columns
        (rows) and taking the smallest consistent gap yields the cell pitch directly. This
        is robust even when discs are one, two, or more cells apart, because the *smallest*
        gap between distinct columns is one pitch. Returns None if it can't be determined.
        """
        import numpy as np

        if len(circles) < 2:
            return None

        def base_gap(values):
            vals = sorted(values)
            tol = 15.0
            clusters = [vals[0]]
            for v in vals[1:]:
                if v - clusters[-1] > tol:
                    clusters.append(v)
                else:
                    clusters[-1] = (clusters[-1] + v) / 2.0
            if len(clusters) < 2:
                return None
            gaps = np.diff(clusters)
            gaps = gaps[gaps > tol]
            if len(gaps) == 0:
                return None
            base = float(np.min(gaps))
            near = gaps[gaps < base * 1.5]
            return float(np.mean(near)) if len(near) else base

        gx = base_gap([c[0] for c in circles])
        gy = base_gap([c[1] for c in circles])
        candidates = [g for g in (gx, gy) if g is not None]
        if not candidates:
            return None
        return float(np.median(candidates))

    def _nearest_neighbour_pitch(self, circles) -> float:
        """Median nearest-neighbour disc gap — the cell pitch when discs are dense."""
        import numpy as np

        pts = np.array([(c[0], c[1]) for c in circles])
        nn = []
        for i, p in enumerate(pts):
            d = np.hypot(pts[:, 0] - p[0], pts[:, 1] - p[1])
            d[i] = 1e9
            nn.append(d.min())
        nn = np.array(nn)
        adjacent = nn[nn < np.median(nn) * 1.4]  # reject diagonal / multi-cell gaps
        return float(np.median(adjacent))

    def _cell_bounds(self, n: int, origin_x: float, origin_y: float, pitch: float):
        """Build the (col,row) -> (px,py,w,h) map from origin + pitch."""
        cell = int(round(pitch))
        bounds: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}
        for row in range(n):
            for col in range(n):
                px = int(round(origin_x + col * pitch))
                py = int(round(origin_y + row * pitch))
                bounds[(col, row)] = (px, py, cell, cell)
        return bounds

    # ── Legacy edge-based size estimation (no size hint) ─────────────────────

    def _estimate_size_from_edges(self, image_data) -> int:
        """Fallback size estimate. Patched out in unit tests, which mock all CV."""
        import cv2
        import numpy as np

        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        def count_lines(projection) -> int:
            threshold = projection.max() * 0.4 if projection.max() > 0 else 0
            peaks, in_peak = 0, False
            for value in projection:
                if value > threshold and not in_peak:
                    peaks += 1
                    in_peak = True
                elif value <= threshold:
                    in_peak = False
            return peaks

        vertical = count_lines(edges.sum(axis=0))
        horizontal = count_lines(edges.sum(axis=1))
        return int(round((vertical + horizontal) / 2) - 1)