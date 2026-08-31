import json
from backend.input_validation.screenshot.screenshot_errors import (
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
    Overarching orchestrator managing the multi-stage visual recognition pipeline.

    Responsibility:
        Functions as the primary external gateway bridging unstructured graphic uploads 
        into precisely structured payload dictionaries suitable for mathematical generation 
        via downstream domain interpreters.

    Implementation Details:
        Maintains protected module references directly, establishing distinct responsibilities 
        across dedicated extraction subsystems. Chains complex execution loops asynchronously, 
        surfacing strict internal warnings or bubbling fatal pipeline halts upward transparently.
    """

    def __init__(self):
        """
        Initializes the protected execution handlers necessary for pipeline traversal.

        Implementation Details:
            Executes strictly isolated instantiations bounding internal dependencies safely 
            behind class encapsulation. Avoids overhead penalties by ensuring heavy 
            vision tools within these nested structures aren't invoked until explicit utilization.
        """
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
        Executes sequential visual processing converting inputs to native configurations.

        Args:
            image_bytes: The raw transport bytes comprising the user's targeted visual capture.
            board_size: The optional structural parameter manually fed into the evaluation to 
                accelerate geometric bounds detection and skip legacy scale estimations.

        Returns:
            The comprehensively assembled metadata structured seamlessly into standard 
            Python schema dicts.

        Raises:
            UnreadableImageError: If the provided mapping byte structure contains zero volume.
            NoBoardDetectedError: If the extraction pipeline securely detects valid bounds but 
                no requisite physical puzzle structures.

        Implementation Details:
            Evaluates boundaries immediately asserting input presence. Routes successful matrices 
            sequentially into specialized sub-components, retaining contextual properties 
            (like identified theme logic and coordinate arrays) explicitly passing them into 
            subsequent evaluations. Evaluates final numerical outcomes compiling internal warnings 
            while forcefully failing layouts reporting invalid marker populations.
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
        """
        Executes sequential visual processing directly serializing outcomes over transport.

        Args:
            image_bytes: The raw encoded graphic binary intended for architectural parsing.

        Returns:
            The finalized JSON string safely matching established payload schemas.

        Implementation Details:
            Delegates raw extraction directly to internal dictionary conversion loops. 
            Actively strips internal diagnostic metadata bounds (warnings) ensuring the 
            externalized payload complies absolutely with standard API serialization limits.
        """
        data = dict(self.extract_to_dict(image_bytes))
        data.pop("_warnings", None)
        return json.dumps(data)