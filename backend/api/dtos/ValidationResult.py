from pydantic import BaseModel, ConfigDict, Field


class ValidationError(BaseModel):
    """One semantic problem found in a board configuration or solution path (§5.5.4)."""

    model_config = ConfigDict(populate_by_name=True)

    error_code: str = Field(..., alias="errorCode")
    affected_field: str | None = Field(None, alias="affectedField")
    message: str


class ValidationResult(BaseModel):
    """Outcome of semantic validation. Returned by POST /api/import; also produced
    internally by InputValidator (input) and SolutionValidator (final path) (§5.5.4).
    """

    model_config = ConfigDict(populate_by_name=True)

    valid: bool
    message: str = ""
    errors: list[ValidationError] = Field(default_factory=list)
