from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    waypoints: list[Coordinate] = Field(
        ..., description="ordered; index defines visit order"
    )
    walls: list[WallDTO] = Field(default_factory=list, description="may be empty")

    @field_validator("board_size", mode="before")
    @classmethod
    def _reject_boolean_size(cls, value: object) -> object:
        """`bool` is a subclass of `int`, so Pydantic silently coerces JSON `true` to 1.

        That turned a type error into a semantic one: the client got 422
        "Board size 1 is not supported" instead of 400 MALFORMED_REQUEST. Rejecting the
        bool here keeps shape errors in the shape layer, where the taxonomy puts them.
        """
        if isinstance(value, bool):
            raise ValueError("boardSize must be an integer, not a boolean.")
        return value
