"""
Typed error hierarchy strictly delineating external screenshot import failures.

Responsibility:
    Functions as a strongly typed domain vocabulary permitting external routing proxies
    to reliably transform nested graphical interpretation failures directly into actionable
    HTTP API mappings. Segregates physical unreadability from localized missing topologies
    to supply the front-end interface with nuanced, resolvable error dialogs.

Implementation Details:
    Structurally segregates error conditions based on distinct resolution steps.
    Defines generic base wrappers preserving standard exception behaviors before explicitly
    overriding internal HTTP bindings upon specific semantic faults (e.g., separating
    un-parseable structures from missing board elements) rather than passing flattened
    strings which APIs cannot inherently categorize.
"""

from __future__ import annotations


class ScreenshotError(ValueError):
    """
    Base structural exception encapsulating all recoverable graphical processing traps.

    Responsibility:
        Serves as the root polymorphic type enforcing safe backward-compatible behaviors
        for system architectures reliant exclusively on generic standard exceptions.

    Implementation Details:
        Subclasses `ValueError` explicitly to maintain catch-block compatibility across
        older testing environments while forcefully defining strict class-level metadata
        attributes detailing external translation mappings for immediate API integration.
    """

    code: str = "SCREENSHOT_ERROR"
    http_status: int = 422

    def __init__(self, message: str) -> None:
        """
        Initializes the foundational exception with standard contextual logging.

        Args:
            message: The raw human-readable explanation mapping exactly what failed.

        Implementation Details:
            Delegates message formatting explicitly into the primary standard Python
            Exception chain to preserve exact stacktrace contexts.
        """
        super().__init__(message)


class UnreadableImageError(ScreenshotError):
    """
    Indicates raw input payloads completely bypass structural boundaries or format limits.

    Responsibility:
        Distinguishes fatal client-level uploading issues (such as sending corrupt bytes
        or extreme volumes) from valid image payloads completely devoid of targeted UI.

    Implementation Details:
        Hardcodes static HTTP responses to 400 bad requests explicitly preventing
        subsequent logical blocks from trying to process undefined buffer architectures.
    """

    code = "MALFORMED_REQUEST"
    http_status = 400


class NoBoardDetectedError(ScreenshotError):
    """
    Indicates functional, uncorrupted input graphics thoroughly lacking gameplay structures.

    Responsibility:
        Signals to front-end clients that spatial bounds generation correctly resolved,
        yet utterly failed to unearth topological landmarks dictating viable execution geometry.

    Implementation Details:
        Overrides structural identifiers mapped cleanly back into 422 statuses specifying
        clear, actionable UI resolutions (e.g., instructing users to photograph specific
        layouts rather than resizing image properties).
    """

    code = "NO_BOARD_DETECTED"
    http_status = 422


class AmbiguousBoardError(ScreenshotError):
    """
    Indicates successfully located graphics generating un-mappable scaling measurements.

    Responsibility:
        Informs the execution pipeline that while structural bounds were explicitly discovered,
        overall dimension constraints wildly contradicted supported puzzle mathematical profiles.

    Implementation Details:
        Generates distinct 422 markers dictating specific user action separating layout
        failures away from general absence logic, pushing users toward clearer crops over
        entirely different images.
    """

    code = "AMBIGUOUS_BOARD"
    http_status = 422
