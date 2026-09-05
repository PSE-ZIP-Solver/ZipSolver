from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from backend.input_validation.screenshot.screenshot_errors import ScreenshotError
from backend.input_validation.screenshot.screenshot_errors import UnreadableImageError
from backend.input_validation.screenshot.theme_mode import ThemeMode

if TYPE_CHECKING:
    import numpy as np


class WaypointDetectionError(ScreenshotError):
    """
    Identifies localized sequence breaks occurring explicitly across parsed marker digits.

    Responsibility:
        Informs the execution lifecycle when recognized markers mathematically contradict
        strict serialization rules, signaling missing links, impossible duplicates, or entirely
        illegible milestone glyphs.

    Implementation Details:
        Assigns standard 422 HTTP outputs mirroring identical failures thrown by the deeper
        semantic validator matrix. Allows frontend operators to uniformly process topological
        reading crashes regardless of their origin layer.
    """

    code = "INVALID_WAYPOINTS"
    http_status = 422


class WaypointDetector:
    """
    Identifies, segments, and processes central digits defining sequence markers.

    Responsibility:
        Coordinates internal evaluation loops crossing pre-computed graphical grids scanning for
        specific saturation matrices before extracting bounded character shapes determining sequential
        traversal layouts.

    Implementation Details:
        Maintains an aggregated best-effort pipeline structure natively absorbing and reporting
        low-confidence detection states dynamically while safely falling back onto deterministic
        reading logic arrays explicitly minimizing generalized pipeline crashes caused by weak OCR mapping.
    """

    def _disc_bbox(self, center, fallback_bbox):
        """
        Maps targeted dimensional boxes prioritizing identified circle focal maps.

        Args:
            center: The discrete focal coordinate map indicating identified disk properties.
            fallback_bbox: The localized grid parameters deployed aggressively upon missed detections.

        Returns:
            The normalized spatial coordinate package definitively bounding the operational disk.

        Implementation Details:
            Extracts coordinates actively overriding generalized node blocks by centering strictly
            upon detected radius parameters ensuring cropped boundaries prevent severe glyph clipping
            especially along straddled boundaries.
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
        Scans localized bounds systematically interpreting mathematical layout markers.

        Args:
            image_data: The absolute overarching pixel payload.
            cell_bounds: The active dictionary explicitly mapping logical spaces onto physical crops.
            theme: The identified illumination mode actively adjusting evaluation thresholds.
            disc_cells: The pre-supplied bounding anchors actively preventing duplicate per-cell re-detections.

        Returns:
            A strictly formulated ordered sequence directly assigning layout progression steps.

        Raises:
            UnreadableImageError: If the source matrix evaluates empty.
            ValueError: If cell definitions are completely missing from the mapping bounds.

        Implementation Details:
            Executes targeted best-effort mapping looping exclusively utilizing cached disk anchors
            where present, mitigating extreme edge-case failure nodes. Integrates defensive loops
            preventing localized OCR skips from flatly halting operations, injecting aggregated
            warnings internally to preserve overarching coordinate configurations cleanly sorted
            utilizing standardized row-major sorting vectors natively.
        """
        self.last_warnings: List[Dict[str, Any]] = []

        if image_data is None or image_data.size == 0:
            raise UnreadableImageError("Image data cannot be None or empty.")
        if not cell_bounds:
            raise ValueError("Cell bounds dictionary cannot be empty or None.")

        # ITERATE — prefer the localizer's globally-detected discs (reliable positions). If
        # none were supplied, fall back to per-cell marker detection over every cell.
        marked_cells: List[Tuple[int, int]] = []  # every cell that HAS a marker
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
                self.last_warnings.append(
                    {
                        "code": "WAYPOINT_NUMBER_UNREADABLE",
                        "message": (
                            f"Marker at cell ({grid_x}, {grid_y}) could not be read; "
                            "using detected order."
                        ),
                        "cell": [int(grid_x), int(grid_y)],
                    }
                )
                continue

            if numeral in numeral_to_cell:
                # Duplicate read -> low confidence in numbering, not a fatal error.
                self.last_warnings.append(
                    {
                        "code": "WAYPOINT_NUMBER_DUPLICATE",
                        "message": (
                            f"Waypoint number {numeral} was read more than once; "
                            "numbering may be wrong — please verify the order."
                        ),
                        "cell": [int(grid_x), int(grid_y)],
                    }
                )
                continue
            numeral_to_cell[numeral] = (int(grid_x), int(grid_y))

        if not marked_cells:
            return []

        # DECIDE CONFIDENCE. Trust the read numbers only if every marked cell was read AND
        # the numbers are exactly 1..k with no gaps or duplicates. Otherwise fall back to a
        # deterministic reading order (top-to-bottom, then left-to-right) and warn.
        k = len(marked_cells)
        read_is_clean = len(numeral_to_cell) == k and sorted(numeral_to_cell) == list(
            range(1, k + 1)
        )

        if read_is_clean:
            return [
                [numeral_to_cell[n][0], numeral_to_cell[n][1]] for n in range(1, k + 1)
            ]

        # Fallback: order the detected positions deterministically. This preserves all
        # waypoint POSITIONS (which are reliable) and gives a stable, if possibly-wrong,
        # visit order for the user to correct.
        if not self.last_warnings:
            self.last_warnings.append(
                {
                    "code": "WAYPOINT_ORDER_INFERRED",
                    "message": (
                        "Waypoint numbers could not be read confidently; "
                        "order was inferred — please verify."
                    ),
                    "cell": None,
                }
            )
        ordered = sorted(marked_cells, key=lambda c: (c[1], c[0]))  # row-major
        return [[x, y] for (x, y) in ordered]

    # ── Private helpers ──────────────────────────────────────────────────────

    def _detect_marker_and_read(
        self,
        image_data: "np.ndarray",
        bbox: Tuple[int, int, int, int],
        theme: ThemeMode,
    ):
        """
        Segments localized blocks validating high saturation circular boundaries yielding read targets.

        Args:
            image_data: The absolute mapping array actively containing spatial layouts.
            bbox: The exact geometric node bounds extracting specific structural cell boundaries.
            theme: The identified illumination mode actively adjusting evaluation logic.

        Returns:
            The raw identified character metric or contextual symbols designating unreadable objects.

        Implementation Details:
            Extracts strict sub-matrices evaluating raw color thresholds targeting vivid orange
            markings aggressively skipping barren layouts completely. Utilizes constrained core
            selections identifying brilliant central digits strictly preventing heavy rim bleeding
            before actively channeling threshold arrays down specialized numeral interpretation lines.
        """
        import cv2
        import numpy as np

        px, py, w, h = bbox
        cell = image_data[py : py + h, px : px + w]
        if cell is None or getattr(cell, "size", 0) == 0:
            return None

        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        # Is there an orange disc in this cell? (saturated orange covering a real fraction.)
        disc = (hue > 5) & (hue < 30) & (sat > 65) & (val > 120)
        if disc.sum() < (w * h) * 0.12:
            return None  # no marker here

        # Restrict glyph detection to the core, away from the anti-aliased rim.
        cy0, cy1 = int(h * 0.18), int(h * 0.82)
        cx0, cx1 = int(w * 0.18), int(w * 0.82)
        core = hsv[cy0:cy1, cx0:cx1]
        # The glyph polarity is local to its disc: dark-theme ZipSolver uses
        # dark ink, while other sources may keep white ink on a dark page.
        # Inspect both polarities within the core, away from the disc edge.
        white = ((core[:, :, 1] < 70) & (core[:, :, 2] > 190)).astype(np.uint8) * 255
        dark = (core[:, :, 2] < 85).astype(np.uint8) * 255
        if cv2.countNonZero(dark) > cv2.countNonZero(white):
            white = dark
        # Threshold relative to cell area so this works whether the image was downscaled to
        # ~1024px (pipeline default) or left full-res.
        min_glyph_px = max(6, int(w * h * 0.004))
        if cv2.countNonZero(white) < min_glyph_px:
            return "?"  # disc present but no legible glyph

        number = self._read_number(white)
        return number if number is not None else "?"

    def _read_number(self, white_mask):
        """
        Segments localized glyph clusters mapping structural boundaries back to classification routines.

        Args:
            white_mask: The heavily constrained threshold array illuminating core digit patterns.

        Returns:
            The absolutely resolved mathematical integer representing active layout progression steps.

        Implementation Details:
            Parses connected component labels aggregating raw glyph geometries securely while
            eliminating speckle noise naturally scaling bounds horizontally identifying distinct
            multi-digit numbers iteratively against cached template definitions preserving layout order.
        """
        import cv2

        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(
            white_mask, connectivity=8
        )
        height, width = white_mask.shape
        min_area = max(6, int(height * width * 0.01))
        boxes = []
        for i in range(1, num_labels):
            x, y, bw, bh, area = stats[i]
            if area < min_area or bh < height * 0.35:  # drop specks / partial rim
                continue
            boxes.append((x, white_mask[y : y + bh, x : x + bw]))
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
        """
        Calculates mathematical nearest-neighbor variances matching isolated chunks into numbers.

        Args:
            glyph: The targeted geometric subset identifying a singular numerical shape.

        Returns:
            The raw identified evaluation metric mapping back onto standard integers.

        Implementation Details:
            Extracts fully normalized layout bounds crossing identical dimensions actively pulling
            compiled memory templates computing squared mathematical variances dictating optimal
            distance gaps dynamically mapping pure shape relationships strictly independent of ink weights.
        """
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
        """
        Interpolates dimensional structures forcefully centering localized objects symmetrically.

        Args:
            glyph: The explicit target pattern necessitating uniform scaling models.
            box: The defined scaling boundary applied uniformly dictating overarching maps.

        Returns:
            A rigorously scaled array structure formatted explicitly for template checks.

        Implementation Details:
            Determines structural aspect gaps dynamically resolving bounds evenly across maximum
            axes immediately projecting interpolation loops directly mapping onto entirely blank
            standardized geometric canvas floors securely locking shapes.
        """
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
        canvas[oy : oy + nh, ox : ox + nw] = resized > 60
        return canvas

    def _digit_templates(self):
        """Load the same pre-rendered digit shapes on Windows and Linux.

        Templates contain glyph masks, not a font file. Their generation is
        documented in scripts/build_screenshot_digit_templates.py. Loading
        numeric arrays with pickle disabled keeps this independent of host fonts.
        """
        cache = getattr(self, "_digit_template_cache", None)
        if cache is not None:
            return cache

        from pathlib import Path
        import numpy as np

        with np.load(
            Path(__file__).with_name("digit_templates.npz"), allow_pickle=False
        ) as data:
            cache = {digit: data[str(digit)].astype(np.float32) for digit in range(10)}
        self._digit_template_cache = cache
        return cache

    def _unbox_numeral(self, raw) -> Optional[int]:
        """
        Safely bridges complex return classes cleanly reverting ambiguous metrics natively.

        Args:
            raw: The dynamic interpretation value dictating varying underlying library types.

        Returns:
            The normalized pure Python integer representation, returning entirely null if invalid.

        Implementation Details:
            Extracts deeply boxed tensor matrices securely utilizing dynamic runtime assessments
            targeting exact resolution states directly. Handles custom type bindings safely bypassing
            internal unboxing errors preventing complete evaluation loop failures over erratic strings.
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
