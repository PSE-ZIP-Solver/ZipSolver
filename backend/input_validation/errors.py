"""
Typed error hierarchy for board parsing (§5.5.5).

Responsibility:
    Provides a structured taxonomy of exception classes utilized during payload
    interpretation. Allows the API layer to map parse failures by their categorical
    type rather than dynamically inspecting fragile message strings, mirroring the
    system's screenshot error hierarchy.

Implementation Details:
    The `JsonInterpreter.buildBoard` method previously relied upon a generic `ValueError`
    for every fault, culminating in broad 400 API responses. The internal rule dictating
    unique walls (§5.5.1) requires interception before `Board` instantiation due to its
    internal Set collapse behavior. Carrying the precise taxonomy code on specialized
    exceptions empowers the API to cleanly return distinct HTTP 422 statuses while the
    interpreter remains strictly unaware of HTTP context.
"""

from __future__ import annotations


class BoardParseError(ValueError):
    """
    Base for every failure raised while turning a payload into a structural board model.

    Responsibility:
        Acts as the foundational exception for malformed parsing logic, securing backward
        compatibility for pre-existing system callers expecting generalized dictionary
        failure traps.

    Implementation Details:
        Inherits directly from `ValueError`. Embeds static class-level attributes matching
        the overarching API taxonomy, facilitating seamless routing of HTTP statuses and
        localized error codes up the execution chain.
    """

    code: str = "MALFORMED_REQUEST"
    http_status: int = 400
    affected_field: str | None = None


class DuplicateWallError(BoardParseError):
    """
    Indicates the parsed payload explicitly defines the exact same physical barrier twice.

    Responsibility:
        Catches semantic payload rule-breaks (where identical coordinates define redundant
        walls) strictly at the translation layer, ensuring proper downstream error reporting
        instead of a generalized structural failure.

    Implementation Details:
        Overrides parent static fields to specifically dictate a 422 HTTP mapping. Captured
        and raised by the interpreter prior to object instantiation because the underlying
        graph algorithm heavily utilizes Sets which naturally drop unordered duplicates,
        permanently destroying the ability to spot this structural violation later.
    """

    code = "INVALID_WALLS"
    http_status = 422
    affected_field = "walls"
