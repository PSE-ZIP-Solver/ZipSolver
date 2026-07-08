from pydantic import BaseModel, ConfigDict, Field

Coordinate = tuple[int, int]


class WallDTO(BaseModel):
    """A wall as the unordered pair of the two cells it separates (§5.5.1)."""

    model_config = ConfigDict(populate_by_name=True)

    neighbor_a: Coordinate = Field(..., alias="neighborA")
    neighbor_b: Coordinate = Field(..., alias="neighborB")


class PuzzleRequest(BaseModel):
    """Board configuration and request body for POST /api/solve and POST /api/import (§5.5.1).

    Shape only — Pydantic guarantees types and structure. Semantic legality (in-bounds,
    adjacency, waypoint order) is InputValidator's job, not this model's. Carries no
    solver-limit or model fields: those are fixed backend-side per the trust boundary.
    """

    model_config = ConfigDict(populate_by_name=True)

    board_size: int = Field(..., alias="boardSize", description="6 | 7 | 8")
    waypoints: list[Coordinate] = Field(..., description="ordered; index defines visit order")
    walls: list[WallDTO] = Field(default_factory=list, description="may be empty")
