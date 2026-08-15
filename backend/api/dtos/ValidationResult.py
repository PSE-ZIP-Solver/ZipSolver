"""Re-export of the validation contract (§5.5.4).

The models themselves live in ``backend.input_validation.validation_dtos`` — the component
that produces them. Keeping this module as a thin re-export preserves every existing
import path (``from backend.api.dtos.ValidationResult import ValidationResult``) and the
generated OpenAPI schema, while the dependency now points API -> input_validation rather
than the other way round.
"""

from backend.input_validation.validation_dtos import ValidationError, ValidationResult

__all__ = ["ValidationError", "ValidationResult"]