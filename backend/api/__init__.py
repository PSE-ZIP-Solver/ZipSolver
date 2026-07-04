"""Public API package exports.

Keep the FastAPI application import lazy.  Python executes this file before any
``backend.api.*`` submodule import, so eagerly importing ``BackendAPI`` here
would make DTO and architecture imports require the web runtime as well.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.api.BackendAPI import BackendAPI

__all__ = ["BackendAPI"]


def __getattr__(name: str) -> Any:
    if name == "BackendAPI":
        from backend.api.BackendAPI import BackendAPI

        return BackendAPI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
