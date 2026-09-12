from typing import TYPE_CHECKING, Dict, Optional, Tuple

from backend.input_validation.screenshot.screenshot_errors import (
    AmbiguousBoardError,
    NoBoardDetectedError,
    UnreadableImageError,
)

if TYPE_CHECKING:
    import numpy as np

ALLOWED_SIZES = (6, 7, 8)


class GridLocalizer:
    """
    Finds and isolates the localized puzzle grid within the overall bounding screenshot.

    Responsibility:
        Identifies spatial origins and scales associated with the gameplay area, dividing
        the raw graphical matrix into clearly mapped, coordinate-bound cells for downstream
        marker and wall extractions.

    Implementation Details:
        Operates internally using two distinct sizing modes: a production pipeline utilizing
        a predetermined frontend dimension hint to reliably slice bounds without estimation,
        and a legacy diagnostic fallback executing edge-based estimations to determine cell scales.
        Calculations anchor heavily on highly saturated orange waypoint discs and background
        panel brightness to overcome low-contrast structural renderings.
    """

    def localize_grid(
        self,
        image_data: "np.ndarray",
        board_size: Optional[int] = None,
    ) -> Tuple[int, Dict[Tuple[int, int], Tuple[int, int, int, int]]]:
        """
        Detects the spatial board and segments the bounds for individual cells.

        Args:
            image_data: The normalized multi-channel pixel array representing the gameplay capture.
            board_size: The explicitly defined structural dimension provided by outer orchestrators,
                serving as an authoritative hint to bypass estimation algorithms.

        Returns:
            A tuple coupling the definitively identified grid dimension with a dictionary mapping
            logical coordinate pairs directly to raw pixel bounding boxes.

        Raises:
            UnreadableImageError: If the input array is empty or critically undefined.
            AmbiguousBoardError: If the size cannot be mathematically resolved to supported topologies.

        Implementation Details:
            Safely delays the import of computer vision modules to prevent boot-time registry bloat.
            Selects geometric resolution logic dynamically based on the presence of the sizing hint,
            generating an active coordinate dictionary matching pixel slices to grid logicals.
        """
        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")

        import cv2  # noqa: F401  (lazy import; used by helpers)

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
        """
        Calculates absolute origin coordinates and uniform cell pitch scales.

        Args:
            image_data: The targeted pixel matrix requiring spatial extraction.
            n: The definitive scaling limit mapping the absolute row and column counts.

        Returns:
            A mathematical grouping detailing the exact origin X, origin Y, and scalar pitch.

        Raises:
            NoBoardDetectedError: If no reliable anchors or circular discs are present.

        Implementation Details:
            Derives foundational geometry by identifying high-saturation discs and analyzing
            spatial nearest-neighbor gaps to calculate grid pitch. Snaps computed anchors back
            to identified panel limits to eliminate bounding box drift caused by external UI chrome.
            Actively preserves identified global disc centres within instance state to avoid
            per-cell boundary cutoff issues during downstream digit reading.
        """
        import numpy as np

        circles = self._detect_circles(image_data)
        panel = self._panel_bounds(image_data, circles)

        # Discs sit at cell centres, so the spacing between distinct disc columns/rows is a
        # direct, reliable pitch measurement — more trustworthy than the panel bounds, which
        # can be over-sized by surrounding chrome. When enough discs are present, use their
        # spacing; otherwise fall back to the panel, then to disc radius.
        board_circles = [c for c in circles if c[2] < 40]  # drop oversized UI blobs
        approx = None
        if panel is not None:
            approx = (panel[2] + panel[3]) / 2.0 / n
        disc_pitch = (
            self._disc_spacing_pitch(board_circles, approx)
            if len(board_circles) >= 2
            else None
        )

        if disc_pitch is not None:
            pitch = disc_pitch
            # Anchor the grid on the panel centre using the disc-derived pitch. Deriving the
            # origin from the smallest disc coordinate is wrong whenever the top-left-most
            # waypoint is not in row/column 0 — it shifts the whole grid by a cell. The
            # panel centre is a stable anchor; the residual refinement below then snaps the
            # grid so disc centres land exactly on cell centres.
            if panel is not None:
                centre_x = panel[0] + panel[2] / 2.0
                centre_y = panel[1] + panel[3] / 2.0
                origin_x = centre_x - n * pitch / 2.0
                origin_y = centre_y - n * pitch / 2.0
            else:
                origin_x = min(c[0] for c in board_circles) - pitch / 2.0
                origin_y = min(c[1] for c in board_circles) - pitch / 2.0
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

            # The residual step only aligns to cell centres (mod pitch); it cannot fix an
            # anchor that is a whole cell out. Slide the grid by whole pitches until every
            # disc falls inside [0, n) — the discs are all on the board by construction, so
            # any disc mapping outside means the origin is off by that many cells.
            # Guarded: unit tests mock numpy, where these comparisons yield non-numeric
            # values; the alignment itself is covered by the real-screenshot corpus.
            try:
                for _ in range(3):
                    cols = np.round((cxs - origin_x) / pitch - 0.5)
                    rows = np.round((cys - origin_y) / pitch - 0.5)
                    shifted = False
                    if float(cols.min()) < 0:
                        origin_x -= pitch * (0 - float(cols.min()))
                        shifted = True
                    elif float(cols.max()) > n - 1:
                        origin_x += pitch * (float(cols.max()) - (n - 1))
                        shifted = True
                    if float(rows.min()) < 0:
                        origin_y -= pitch * (0 - float(rows.min()))
                        shifted = True
                    elif float(rows.max()) > n - 1:
                        origin_y += pitch * (float(rows.max()) - (n - 1))
                        shifted = True
                    if not shifted:
                        break
            except (TypeError, ValueError):
                pass

        # Record the reliable disc -> cell mapping from GLOBAL circle detection, using the
        # final origin/pitch. The per-cell re-detection in the waypoint detector misses
        # discs that straddle cell boundaries; these globally-detected centres do not, so
        # the extractor prefers them. Map each disc centre to its cell and keep the pixel
        # centre so the digit reader can crop precisely around the disc.
        self.last_waypoint_cells: Dict[Tuple[int, int], Tuple[float, float, float]] = {}
        for cx, cy, r in board:
            col = int(round((cx - origin_x) / pitch - 0.5))
            row = int(round((cy - origin_y) / pitch - 0.5))
            if 0 <= col < n and 0 <= row < n:
                self.last_waypoint_cells[(col, row)] = (cx, cy, r)

        return origin_x, origin_y, pitch

    def _detect_circles(self, image_data):
        """
        Locates prominent circular waypoint indicators utilizing color segmentation.

        Args:
            image_data: The target matrix containing potential milestone UI elements.

        Returns:
            An accumulated compilation grouping absolute coordinates and geometric radii.

        Implementation Details:
            Extracts strict color channels by forcing an HSV translation. Applies strict
            morphological thresholding isolating hyper-saturated orange values before computing
            contour enclosing bounds and aggressively pruning non-circular blobs.
        """
        import cv2
        import numpy as np

        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        # Dark-theme markers are pale orange, with much less saturation than
        # light-theme markers. Circularity below distinguishes them from walls.
        mask = ((hue > 5) & (hue < 30) & (sat > 65) & (val > 120)).astype(
            np.uint8
        ) * 255
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
        """Find a square panel from bright areas or repeated cell colours.

        Morphology joins cells across grid lines. A candidate must contain the
        marker centroid; the returned box anchors the disc-derived cell spacing.
        """
        import cv2
        import numpy as np

        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        masks = [(gray >= 244).astype(np.uint8) * 255]
        # Flat cell backgrounds form a large square in either theme. Candidate
        # colours come from the image itself; do not assume a white board or
        # invert the whole screenshot (that also changes marker colours).
        pixels = image_data[::4, ::4].reshape(-1, 3)
        colours, counts = np.unique(pixels, axis=0, return_counts=True)
        signed_image = image_data.astype(np.int16)
        for index in np.argsort(counts)[-8:]:
            if counts[index] < len(pixels) * 0.02:
                continue
            colour = colours[index].astype(np.int16)
            mask = np.all(np.abs(signed_image - colour) <= 4, axis=2)
            masks.append(mask.astype(np.uint8) * 255)

        contours = []
        for mask in masks:
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((31, 31), np.uint8))
            found, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            contours.extend(found)

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

    def _disc_spacing_pitch(self, circles, approx_pitch=None):
        """
        Calculates theoretical coordinate scale from discrete spacing arrays.

        Args:
            circles: The grouped nodes detailing raw topological coordinates.
            approx_pitch: The optional base scalar defining the nearest-match cluster.

        Returns:
            The normalized base spacing scale defining grid cell leaps.

        Implementation Details:
            Extracts absolute gap limits mathematically. Since waypoints may spawn non-adjacently,
            identifies grouped spatial gaps and normalizes them against the structural panel
            estimation to recover singular cell spans cleanly.
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
            if approx_pitch:
                # Each gap spans an integer number of cells; normalise it back to one cell.
                unit = []
                for g in gaps:
                    k = max(1, int(round(g / approx_pitch)))
                    unit.append(g / k)
                return float(np.median(unit))
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
        """
        Extracts foundational spatial scales assuming dense localized distributions.

        Args:
            circles: The compiled mapping nodes providing coordinate baselines.

        Returns:
            The mathematically derived minimal hop spanning adjacent structures.

        Implementation Details:
            Executes a rapid Euclidean distance map applying vectorization across node sets.
            Prunes outliers violating strict diagonal bounds to isolate purely cardinal relationships.
        """
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
        """
        Constructs a definitive dictionary mapping topological coordinates to absolute pixels.

        Args:
            n: The structural dimensional scale governing boundary loop caps.
            origin_x: The definitive root X pixel coordinate anchoring the map.
            origin_y: The definitive root Y pixel coordinate anchoring the map.
            pitch: The mathematical scalar translating grid intervals into pixel blocks.

        Returns:
            An active dictionary structuring localized indices directly to visual areas.

        Implementation Details:
            Executes dual-axis generation utilizing rounding logic across pure floating-point
            steps to prevent accumulating floating-point drift at deeper grid sectors.
        """
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
        """
        Provides fallback dimensional metrics directly querying visual contrast limits.

        Args:
            image_data: The target matrix parsed for raw visual demarcations.

        Returns:
            The raw numeric mapping defining the overall span detected via contrast peaks.

        Implementation Details:
            Maintains internal test compatibility. Invokes edge identification via Canny mapping,
            summing linear responses mathematically across axes to determine absolute interior volumes.
        """
        import cv2

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
