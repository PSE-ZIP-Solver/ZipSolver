from typing import List
from backend.validation_error import ValidationError


class ValidationResult:
    """
    Encapsulates the finalized macro-level outcome of a complete solution evaluation pass.

    Responsibility:
        Delivers a unified, structured response payload that definitively declares whether a
        trajectory was successful, alongside high-level contextual summaries and any explicit
        granular errors cataloged during the assessment.

    Implementation Details:
        Maintains robust state security by acting as an immutable compound wrapper. It securely
        houses a boolean success flag, a string context message, and an iterable collection of
        sub-errors, restricting external access entirely to protected property decorators.
    """

    def __init__(self, valid: bool, message: str, errors: List[ValidationError]):
        """
        Consolidates the global outcome metrics of a validation lifecycle.

        Args:
            valid: The absolute binary determination of the solution's compliance.
            message: A high-level summary string describing the overall outcome of the pass.
            errors: A compiled sequence of specific, granular failure records, if any occurred.

        Implementation Details:
            Routes the absolute success state, summary context, and error compilation array directly
            into isolated, protected internal object states to lock the resolution in memory.
        """
        self._valid = valid
        self._message = message
        self._errors = errors

    @property
    def isValid(self) -> bool:
        """
        Retrieves the absolute binary compliance determination of the validated subject.

        Returns:
            The definitive boolean flag confirming complete success or failure.

        Implementation Details:
            Exposes read-only observation capabilities to the strictly protected validity
            flag utilizing standard decorator bindings.
        """
        return self._valid

    @property
    def getMessage(self) -> str:
        """
        Retrieves the overarching human-readable summary of the validation pass.

        Returns:
            The structured string detailing the generalized completion status.

        Implementation Details:
            Exposes read-only observation capabilities to the strictly protected summary
            text utilizing standard decorator bindings.
        """
        return self._message

    @property
    def getErrors(self) -> List[ValidationError]:
        """
        Retrieves the aggregated chronological log of all specific infractions caught.

        Returns:
            The complete iterable list containing granular violation records.

        Implementation Details:
            Exposes read-only observation capabilities to the strictly protected error array
            utilizing standard decorator bindings.
        """
        return self._errors
