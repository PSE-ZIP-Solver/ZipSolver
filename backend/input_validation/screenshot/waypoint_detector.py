from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from backend.input_validation.screenshot.screenshot_errors import ScreenshotError
from backend.input_validation.screenshot.screenshot_errors import UnreadableImageError
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

    def _disc_bbox(self, center, fallback_bbox):
        """Build a square bbox centred on a disc (cx, cy, r) for precise digit cropping.

        Falls back to the cell bbox if the centre is missing. Using the disc's own centre
        (rather than the cell box) keeps the numeral centred even when the disc straddles a
        cell boundary — the exact case per-cell detection got wrong.
        """
        if center is None:
            return fallback_bbox
        cx, cy, r = center
        side = int(round(r * 2.0))
        x = int(round(cx - r))
        y = int(round(cy - r))
        return (x, y, side, side)

    def detect_waypoints(
        self,
        image_data: "np.ndarray",
        cell_bounds: Dict[Tuple[int, int], Tuple[int, int, int, int]],
        theme: ThemeMode,
        disc_cells: "Optional[Dict[Tuple[int, int], Tuple[float, float, float]]]" = None,
    ) -> List[List[int]]:
        """
        Scans the localized cells to detect markers and reads their sequential numbers.
        Formats the return exactly to the JSON schema: ordered List[[x, y]].

        Best-effort contract: waypoint *positions* are detected reliably, but the printed
        numbers are read with OCR that can misfire on real screenshots. Rather than reject
        the whole board when the read is imperfect, the numbers are trusted only when they
        form a clean 1..k permutation; otherwise the waypoints are ordered deterministically
        (reading order) and a warning is recorded via ``self.last_warnings`` for the caller
        to surface. This keeps a slightly-misread board usable (the user can fix the order
        in the editor) instead of failing the import outright.

        ``disc_cells`` (optional): a {(col,row): (cx, cy, r)} map of discs the localizer
        already found by GLOBAL circle detection. When present it is the authoritative set
        of waypoint POSITIONS — it does not miss discs that straddle a cell boundary, which
        per-cell re-detection does — and the digit reader crops precisely around each disc
        centre. When absent, falls back to scanning every cell (the original contract the
        unit tests patch).

        Returns:
            List[List[int]]: [x, y] coordinates in visit order (index 0 == waypoint 1).
        """
        self.last_warnings: List[Dict[str, Any]] = []

        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")
        if not cell_bounds:
            raise ValueError("Cell bounds dictionary cannot be empty or None.")

        # ITERATE — prefer the localizer's globally-detected discs (reliable positions). If
        # none were supplied, fall back to per-cell marker detection over every cell.
        marked_cells: List[Tuple[int, int]] = []          # every cell that HAS a marker
        numeral_to_cell: Dict[int, Tuple[int, int]] = {}  # confidently-read numerals

        # One flag drives both decisions below. Previously the branch used truthiness
        # (`if disc_cells:`) while the "trust the position" guard used identity
        # (`disc_cells is not None`). An EMPTY dict — what GridLocalizer returns when it
        # finds no discs at all — satisfied the second but not the first, so every cell on
        # the board was scanned AND every miss was promoted to a detected marker. A
        # board-less screenshot came back as n^2 phantom waypoints.
        has_disc_positions = bool(disc_cells)

        if has_disc_positions:
            iterator = [
                (cell, self._disc_bbox(center, cell_bounds.get(cell)))
                for cell, center in disc_cells.items()
            ]
        else:
            iterator = list(cell_bounds.items())

        for (grid_x, grid_y), bbox in iterator:
            raw = self._detect_marker_and_read(image_data, bbox, theme)
            if has_disc_positions and raw is None:
                # Position is trusted (came from global detection); only the number failed.
                raw = "?"
            if raw is None:
                continue

            marked_cells.append((int(grid_x), int(grid_y)))
            numeral = self._unbox_numeral(raw)
            if numeral is None:
                # A detected-but-unreadable marker ('?') is not fatal under best-effort:
                # the position still counts, we just couldn't read its number.
                self.last_warnings.append({
                    "code": "WAYPOINT_NUMBER_UNREADABLE",
                    "message": (
                        f"Marker at cell ({grid_x}, {grid_y}) could not be read; "
                        "using detected order."
                    ),
                    "cell": [int(grid_x), int(grid_y)],
                })
                continue

            if numeral in numeral_to_cell:
                # Duplicate read -> low confidence in numbering, not a fatal error.
                self.last_warnings.append({
                    "code": "WAYPOINT_NUMBER_DUPLICATE",
                    "message": (
                        f"Waypoint number {numeral} was read more than once; "
                        "numbering may be wrong — please verify the order."
                    ),
                    "cell": [int(grid_x), int(grid_y)],
                })
                continue
            numeral_to_cell[numeral] = (int(grid_x), int(grid_y))

        if not marked_cells:
            return []

        # DECIDE CONFIDENCE. Trust the read numbers only if every marked cell was read AND
        # the numbers are exactly 1..k with no gaps or duplicates. Otherwise fall back to a
        # deterministic reading order (top-to-bottom, then left-to-right) and warn.
        k = len(marked_cells)
        read_is_clean = (
            len(numeral_to_cell) == k
            and sorted(numeral_to_cell) == list(range(1, k + 1))
        )

        if read_is_clean:
            return [
                [numeral_to_cell[n][0], numeral_to_cell[n][1]]
                for n in range(1, k + 1)
            ]

        # Fallback: order the detected positions deterministically. This preserves all
        # waypoint POSITIONS (which are reliable) and gives a stable, if possibly-wrong,
        # visit order for the user to correct.
        if not self.last_warnings:
            self.last_warnings.append({
                "code": "WAYPOINT_ORDER_INFERRED",
                "message": (
                    "Waypoint numbers could not be read confidently; "
                    "order was inferred — please verify."
                ),
                "cell": None,
            })
        ordered = sorted(marked_cells, key=lambda c: (c[1], c[0]))  # row-major
        return [[x, y] for (x, y) in ordered]

    # ── Private helpers ──────────────────────────────────────────────────────

    def _detect_marker_and_read(
        self,
        image_data: "np.ndarray",
        bbox: Tuple[int, int, int, int],
        theme: ThemeMode,
    ):
        """Detect an orange waypoint disc in one cell and read its numeral.

        Patched out in unit tests, so its (image, bbox, theme) signature is the contract.
        In production it: crops the cell, finds the saturated orange disc (returns None when
        the cell has none — that is how empty cells are skipped), isolates the white numeral
        as a low-saturation blob in the disc core, segments it into digit glyphs, and reads
        each by template matching. Returns the integer, or '?' if a disc is present but its
        number could not be read.
        """
        import cv2
        import numpy as np

        px, py, w, h = bbox
        cell = image_data[py:py + h, px:px + w]
        if cell is None or getattr(cell, "size", 0) == 0:
            return None

        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        # Is there an orange disc in this cell? (saturated orange covering a real fraction.)
        disc = ((hue > 5) & (hue < 30) & (sat > 120) & (val > 120))
        if disc.sum() < (w * h) * 0.12:
            return None  # no marker here

        # Isolate the white numeral: low-saturation, high-value pixels in the disc core.
        # Restrict to the central region to avoid the disc's anti-aliased rim.
        cy0, cy1 = int(h * 0.18), int(h * 0.82)
        cx0, cx1 = int(w * 0.18), int(w * 0.82)
        core = hsv[cy0:cy1, cx0:cx1]
        white = ((core[:, :, 1] < 70) & (core[:, :, 2] > 190)).astype(np.uint8) * 255
        # Threshold relative to cell area so this works whether the image was downscaled to
        # ~1024px (pipeline default) or left full-res.
        min_glyph_px = max(6, int(w * h * 0.004))
        if cv2.countNonZero(white) < min_glyph_px:
            return "?"  # disc present but no legible glyph

        number = self._read_number(white)
        return number if number is not None else "?"

    def _read_number(self, white_mask):
        """Segment a white-on-black numeral mask into digits and classify each.

        Returns the integer, or None if nothing legible. Digit templates are rendered once
        and cached; matching uses aspect-normalised pixel disagreement (ink-unbiased).
        """
        import cv2
        import numpy as np

        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(white_mask, connectivity =8)
        height, width = white_mask.shape
        min_area = max(6, int(height * width * 0.01))
        boxes = []
        for i in range(1, num_labels):
            x, y, bw, bh, area = stats[i]
            if area < min_area or bh < height * 0.35:  # drop specks / partial rim
                continue
            boxes.append((x, white_mask[y:y + bh, x:x + bw]))
        if not boxes:
            return None
        boxes.sort(key=lambda b: b[0])  # left-to-right

        digits = []
        for _, glyph in boxes:
            d = self._classify_digit(glyph)
            if d is None:
                return None
            digits.append(str(d))
        try:
            return int("".join(digits))
        except ValueError:
            return None

    def _classify_digit(self, glyph) -> Optional[int]:
        """Classify a single-digit glyph (0-9) by nearest normalised template."""
        import numpy as np

        templates = self._digit_templates()
        g = self._normalise_glyph(glyph)
        best, best_dist = None, 1e9
        for digit, variants in templates.items():
            for t in variants:
                dist = float(np.mean((g - t) ** 2))
                if dist < best_dist:
                    best_dist, best = dist, digit
        return best

    def _normalise_glyph(self, glyph, box: int = 40):
        """Scale a glyph into a fixed box preserving aspect, as a float {0,1} mask."""
        import cv2
        import numpy as np

        gh, gw = glyph.shape
        span = box - 6
        if gh >= gw:
            nh, nw = span, max(1, int(round(gw * span / gh)))
        else:
            nw, nh = span, max(1, int(round(gh * span / gw)))
        resized = cv2.resize(glyph, (nw, nh), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((box, box), np.float32)
        oy, ox = (box - nh) // 2, (box - nw) // 2
        canvas[oy:oy + nh, ox:ox + nw] = (resized > 60)
        return canvas

    def _digit_templates(self):
        """Render and cache 0-9 glyph templates from bundled sans-bold fonts."""
        cache = getattr(self, "_digit_template_cache", None)
        if cache is not None:
            return cache

        import os

        import numpy as np
        from PIL import Image, ImageDraw, ImageFont

        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        fonts = [p for p in font_paths if os.path.exists(p)]

        def render(digit: int, font_path: str, size: int = 80):
            img = Image.new("L", (120, 140), 0)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, size)
            s = str(digit)
            bb = draw.textbbox((0, 0), s, font=font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            draw.text(((120 - tw) / 2 - bb[0], (140 - th) / 2 - bb[1]), s, fill=255, font=font)
            arr = np.array(img)
            ys, xs = np.where(arr > 0)
            return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

        cache = {}
        for digit in range(10):
            cache[digit] = [self._normalise_glyph(render(digit, fp)) for fp in fonts]
        self._digit_template_cache = cache
        return cache

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