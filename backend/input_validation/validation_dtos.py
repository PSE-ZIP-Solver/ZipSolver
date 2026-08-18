"""
Canonical home of the validation contract (§5.5.4).

Responsibility:
    Maintains the standardized data transfer objects utilized to communicate semantic 
    failures between the core puzzle domain and the external API boundaries.

Implementation Details:
    These models reside natively within the `input_validation` package to preserve 
    strict unidirectional architectural dependencies, preventing the domain components 
    (like `InputValidator`) from importing structures mapped directly into the API layer. 
    Re-exported upstream to seamlessly preserve backward compatibility for legacy imports 
    and OpenAPI schema generation.
"""

from pydantic import BaseModel, ConfigDict, Field


class ValidationError(BaseModel):
    """
    Represents a single semantic violation discovered within a board configuration or proposed path.

    Responsibility:
        Acts as a standardized data wrapper for an isolated domain violation, mapping 
        internal structural faults into an actionable, frontend-friendly taxonomy.

    Implementation Details:
        Inherits from Pydantic's `BaseModel` to guarantee automated serialization. 
        Utilizes explicit field aliases (`errorCode`, `affectedField`) coupled with 
        `populate_by_name=True` to allow internal Python logic to comfortably use 
        standard snake_case attributes while seamlessly emitting strict camelCase JSON payloads.
    """

    model_config = ConfigDict(populate_by_name=True)

    error_code: str = Field(..., alias="errorCode")
    affected_field: str | None = Field(default=None, alias="affectedField")
    message: str


class ValidationResult(BaseModel):
    """
    Encapsulates the overarching outcome of a comprehensive semantic validation pass.

    Responsibility:
        Serves as the definitive data transfer object conveying the aggregate success state 
        and any compiled arrays of domain errors, bridging internal architectural checks 
        directly into standard HTTP responses.

    Implementation Details:
        Inherits directly from `BaseModel`. Defaults the internal error array dynamically 
        utilizing a field factory to prevent mutable state sharing across requests. Supports 
        by-name population to cleanly translate internal Python state into standardized API contracts.
    """

    model_config = ConfigDict(populate_by_name=True)

    valid: bool
    message: str = ""
    errors: list[ValidationError] = Field(default_factory=list)