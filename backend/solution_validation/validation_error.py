class ValidationError:
    def __init__(self, errorCode: str, message: str, affectedField: str):
        self._errorCode = errorCode
        self._message = message
        self._affectedField = affectedField

    @property
    def getErrorCode(self) -> str:
        return self._errorCode

    @property
    def getMessage(self) -> str:
        return self._message

    @property
    def getAffectedField(self) -> str:
        return self._affectedField