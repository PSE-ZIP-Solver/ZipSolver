from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from backend.api.dtos.ValidationResult import ValidationError


class ErrorCode(str, Enum):
    """Machine-readable identifiers for the 4xx/5xx error taxonomy (§5.5.5)."""

    MALFORMED_REQUEST = "MALFORMED_REQUEST"            # 400 — Pydantic shape/type failure
    UNSUPPORTED_BOARD_SIZE = "UNSUPPORTED_BOARD_SIZE"  # 422 — boardSize not in {6,7,8}
    INVALID_WAYPOINTS = "INVALID_WAYPOINTS"            # 422 — dup / oob / missing waypoints
    INVALID_WALLS = "INVALID_WALLS"                    # 422 — non-adjacent / oob / dup wall
    INTERNAL_ERROR = "INTERNAL_ERROR"                  # 500 — unexpected backend fault


class ErrorResponse(BaseModel):
    """Thin HTTP envelope for every 4xx/5xx response (§5.5.5).

    Solver non-results (UNSOLVABLE / TIMEOUT / FAILED) never use this — they are
    200 SolverResponse outcomes, not errors.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: int
    code: ErrorCode
    message: str
    details: list[ValidationError] | None = None
    timestamp: str = Field(..., description="ISO-8601 (UTC)")
