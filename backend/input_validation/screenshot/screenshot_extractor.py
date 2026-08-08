import json
from typing import Any, Dict

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

    def extract_to_dict(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Runs the pipeline and returns a dict matching the Board Configuration Schema.

        Designed to feed straight into ``JsonInterpreter.buildBoard(...)``; returning a
        dict avoids a redundant serialize/deserialize round-trip at the integration point.

        Sequence: image load -> theme -> grid -> waypoints -> walls. Any exception raised
        by a sub-component (ValueError, WaypointDetectionError) bubbles up unchanged and
        halts the remaining stages.
        """
        # FAST_FAIL_IF_BYTES_NONE_OR_EMPTY — before any component runs.
        if image_bytes is None or len(image_bytes) == 0:
            raise ValueError("Image bytes cannot be None or empty.")

        image = self._image_loader.load_and_preprocess(image_bytes)
        theme = self._palette_detector.detect_theme(image)
        board_size, cell_bounds = self._grid_localizer.localize_grid(image)

        # Waypoint errors (gap/duplicate/unreadable) are allowed to bubble; the wall stage
        # below must not run on a board we could not read waypoints from.
        waypoints = self._waypoint_detector.detect_waypoints(image, cell_bounds, theme)
        walls = self._wall_detector.detect_walls(image, cell_bounds, theme)

        return {
            "boardSize": int(board_size),
            "waypoints": waypoints,
            "walls": walls,
        }

    def extract_to_json(self, image_bytes: bytes) -> str:
        """Same pipeline as :meth:`extract_to_dict`, returned as a JSON string.

        Provided for callers that want the serialized schema directly (e.g. an HTTP layer
        that forwards the raw JSON). Internally delegates so the two entry points can never
        diverge.
        """
        return json.dumps(self.extract_to_dict(image_bytes))