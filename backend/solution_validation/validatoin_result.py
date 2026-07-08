from typing import List
# Adjust import according to your actual module structure
from .validation_error import ValidationError


class ValidationResult:
    def __init__(self, valid: bool, message: str, errors: List[ValidationError]):
        self._valid = valid
        self._message = message
        self._errors = errors

    @property
    def isValid(self) -> bool:
        return self._valid

    @property
    def getMessage(self) -> str:
        return self._message

    @property
    def getErrors(self) -> List[ValidationError]:
        return self._errors