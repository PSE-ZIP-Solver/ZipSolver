"""Typed error hierarchy for board parsing (§5.5.5).

``JsonInterpreter.buildBoard`` used to signal every failure with a bare ``ValueError``,
which the API could only render as ``400 MALFORMED_REQUEST``. That is correct for a
genuinely malformed payload, but wrong for the one semantic rule the interpreter is the
*only* component able to enforce: duplicate walls.

Why duplicates must be caught here. ``Board`` stores walls in a ``Set[Wall]`` whose
equality is order-independent, so ``{A,B}`` and ``{B,A}`` collapse into a single entry the
moment they are added. By the time ``InputValidator`` receives the ``Board``, the
duplicate is gone and unreportable — the rule is only observable against the ordered list
in the payload. Detecting it at parse time and carrying the taxonomy code on the exception
lets the API report the documented ``422 INVALID_WALLS`` without the interpreter having to
know anything about HTTP.

Mirrors the ``ScreenshotError`` hierarchy so the API maps parse failures by *type* rather
than by inspecting message strings.
"""

from __future__ import annotations


class BoardParseError(ValueError):
    """Base for every failure raised while turning a payload into a ``Board``.

    Subclasses ``ValueError`` so existing callers and tests that expect one keep working.
    ``code`` and ``http_status`` let the API map each failure mode onto the error taxonomy.
    """

    code: str = "MALFORMED_REQUEST"
    http_status: int = 400
    affected_field: str | None = None


class DuplicateWallError(BoardParseError):
    """The payload lists the same wall twice (in either cell order).

    Semantic, not structural: the payload is well-formed, it just breaks the uniqueness
    rule of §5.5.1 — hence 422 INVALID_WALLS rather than 400.
    """

    code = "INVALID_WALLS"
    http_status = 422
    affected_field = "walls"