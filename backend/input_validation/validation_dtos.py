"""Canonical home of the validation contract (§5.5.4).

These models live in ``input_validation`` because that is the component that produces
them (§3.2.3). They previously lived under ``backend.api.dtos``, which forced
``InputValidator`` — a domain component — to import from the API package and inverted the
dependency direction the architecture specifies (API depends on its collaborators, never
the reverse). ``backend.api.dtos.ValidationResult`` now re-exports these names, so every
existing import site and the OpenAPI schema are unchanged.
"""

from pydantic import BaseModel, ConfigDict, Field


class ValidationError(BaseModel):
    """One semantic problem found in a board configuration or solution path (§5.5.4)."""

    model_config = ConfigDict(populate_by_name=True)

    error_code: str = Field(..., alias="errorCode")
    affected_field: str | None = Field(default=None, alias="affectedField")
    message: str


class ValidationResult(BaseModel):
    """Outcome of semantic validation. Returned inside the body of POST /api/import; also
    produced internally by InputValidator (input) and SolutionValidator (final path) (§5.5.4).
    """

    model_config = ConfigDict(populate_by_name=True)

    valid: bool
    message: str = ""
    errors: list[ValidationError] = Field(default_factory=list)