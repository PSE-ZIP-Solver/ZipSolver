"""Typed error hierarchy for screenshot import.

Each failure mode carries its own stable ``code`` and ``http_status`` so the API layer
maps errors by *type*, not by sniffing a message string. The three axes the frontend
needs to tell apart:

  - "this isn't a board at all"     -> NoBoardDetectedError        (422, NO_BOARD_DETECTED)
  - "a board, but I can't size it"  -> AmbiguousBoardError         (422, AMBIGUOUS_BOARD)
  - "the file isn't a usable image" -> UnreadableImageError        (400, MALFORMED_REQUEST)
  - "a board, but waypoints break"  -> WaypointDetectionError      (422, INVALID_WAYPOINTS)

The distinction that matters most for UX: NO_BOARD_DETECTED means "point the camera at a
Zip puzzle" — a user-actionable retry — whereas MALFORMED_REQUEST means "that file was
corrupt or not an image". Collapsing them into one 400, as the old flat ValueError did,
made both indistinguishable to the frontend.
"""

from __future__ import annotations


class ScreenshotError(ValueError):
    """Base for every recoverable screenshot-import failure.

    Subclasses ``ValueError`` (these are all bad-input conditions), so existing callers and
    tests that expect a ``ValueError`` keep working, while the added ``code`` and
    ``http_status`` let the API map each failure mode to its own response. ``code`` is a
    stable string the frontend switches on; ``http_status`` is the status the API applies.
    """

    code: str = "SCREENSHOT_ERROR"
    http_status: int = 422

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnreadableImageError(ScreenshotError):
    """The upload could not be decoded, was empty, oversized, or not a real image.

    A client problem (bad file), hence 400 — distinct from a valid image that simply does
    not contain a board.
    """

    code = "MALFORMED_REQUEST"
    http_status = 400


class NoBoardDetectedError(ScreenshotError):
    """A valid image was decoded, but no puzzle grid could be found in it.

    The headline guardrail: a photo of a cat, a blank screenshot, or a page with no grid
    lands here and gets a clear "No board detected" rather than a confusing size error.
    """

    code = "NO_BOARD_DETECTED"
    http_status = 422


class AmbiguousBoardError(ScreenshotError):
    """A grid-like region was found, but its size could not be resolved to 6, 7, or 8.

    Separate from NoBoardDetectedError because the user action differs: here the advice is
    "use a sharper / less cropped screenshot", not "point at a board".
    """

    code = "AMBIGUOUS_BOARD"
    http_status = 422