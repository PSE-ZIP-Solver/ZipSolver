import json
from backend.input_validation.screenshot.errors import (
    NoBoardDetectedError,
    UnreadableImageError,
)
from typing import Any, Dict, Optional

from backend.input_validation.screenshot.image_loader import ImageLoader
from backend.input_validation.screenshot.palette_detector import PaletteDetector
from backend.input_validation.screenshot.grid_localizer import GridLocalizer
from backend.input_validation.screenshot.waypoint_detector import (
    WaypointDetector,
    WaypointDetectionError,
)
from backend.input_validation.screenshot.wall_detector import WallDetector

__all__ = ["ScreenshotExtractor", "WaypointDetectionError"]


class ScreenshotExtractor:
    """
    Main orchestration class for the screenshot extraction pipeline.
    Executes the detectors in sequence and outputs a schema-compliant result.
    """

    def __init__(self):
        # Strict encapsulation with protected attributes. Instantiated once; the heavy
        # libraries each component needs are imported lazily inside their methods, so
        # constructing the extractor stays cheap and import-safe.
        self._image_loader = ImageLoader()
        self._palette_detector = PaletteDetector()
        self._grid_localizer = GridLocalizer()
        self._waypoint_detector = WaypointDetector()
        self._wall_detector = WallDetector()

    # ── Public API ───────────────────────────────────────────────────────────

    def extract_to_dict(
        self, image_bytes: bytes, board_size: "Optional[int]" = None
    ) -> Dict[str, Any]:
        """
        Runs the pipeline and returns a dict matching the Board Configuration Schema.

        Designed to feed straight into ``JsonInterpreter.buildBoard(...)``; returning a
        dict avoids a redundant serialize/deserialize round-trip at the integration point.

        Args:
            image_bytes: the raw uploaded image.
            board_size: the grid size the user already selected in the frontend (6/7/8).
                When provided it is authoritative and removes the need to guess the size
                from the image; when None the localizer falls back to edge estimation.

        Sequence: image load -> theme -> grid -> waypoints -> walls. Any exception raised
        by a sub-component (ValueError, WaypointDetectionError) bubbles up unchanged and
        halts the remaining stages.
        """
        # FAST_FAIL_IF_BYTES_NONE_OR_EMPTY — before any component runs.
        if image_bytes is None or len(image_bytes) == 0:
            raise UnreadableImageError("Image bytes cannot be None or empty.")

        image = self._image_loader.load_and_preprocess(image_bytes)
        theme = self._palette_detector.detect_theme(image)
        detected_size, cell_bounds = self._grid_localizer.localize_grid(image, board_size)

        # Prefer the globally-detected disc positions the localizer already found (reliable
        # even for discs straddling a cell boundary) over per-cell re-detection.
        disc_cells = getattr(self._grid_localizer, "last_waypoint_cells", None)

        # Waypoint detection is best-effort: positions are reliable, numbers may not be.
        # It records any low-confidence reads on the detector; collect them to surface as
        # import warnings rather than failing.
        waypoints = self._waypoint_detector.detect_waypoints(
            image, cell_bounds, theme, disc_cells
        )
        warnings = list(getattr(self._waypoint_detector, "last_warnings", []) or [])

        # NO-BOARD GUARDRAIL. When the caller supplies board_size the localizer never has
        # to guess, so it also never raises NoBoardDetectedError — leaving zero-waypoint
        # output as the only remaining signal that the image contained no puzzle. A real
        # Zip board always carries at least a start and an end marker, so fewer than two
        # detected markers means "this is not a board", not "this is a board with no
        # waypoints" (which would misreport as a semantic 422 from InputValidator).
        if len(waypoints) < 2:
            raise NoBoardDetectedError(
                "No Zip puzzle board could be detected in this image. "
                "Upload a screenshot that shows the full grid with its numbered markers."
            )

        walls = self._wall_detector.detect_walls(image, cell_bounds, theme)

        return {
            "boardSize": int(detected_size),
            "waypoints": waypoints,
            "walls": walls,
            "_warnings": warnings,
        }

    def extract_to_json(self, image_bytes: bytes) -> str:
        """Same pipeline as :meth:`extract_to_dict`, returned as a JSON string.

        Provided for callers that want the serialized schema directly (e.g. an HTTP layer
        that forwards the raw JSON). The internal ``_warnings`` key (best-effort metadata,
        not part of the board schema) is stripped so the JSON matches the board contract.
        """
        data = dict(self.extract_to_dict(image_bytes))
        data.pop("_warnings", None)
        return json.dumps(data)