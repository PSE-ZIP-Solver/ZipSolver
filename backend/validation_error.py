class ValidationError:
    """
    Represents a structured, granular breakdown of a specific logic or rule failure.

    Responsibility:
        Acts as an immutable data transfer object to communicate the exact operational conditions 
        that caused a proposed solution to fail, providing both human-readable context and 
        machine-parseable identifiers for debugging and API responses.

    Implementation Details:
        Designed strictly as a read-only state container. Isolates the string identifiers and 
        descriptions within protected instance attributes during instantiation, exclusively exposing 
        them via property getters to enforce total immutability downstream.
    """
    def __init__(self, errorCode: str, message: str, affectedField: str):
        """
        Constructs a definitive record of a singular validation failure.

        Args:
            errorCode: The explicit machine-readable categorical identifier for the breach.
            message: The comprehensive human-readable descriptive context explaining the failure.
            affectedField: The specific localized data segment or system scope that triggered the fault.

        Implementation Details:
            Captures and routes all provided string metadata directly into secure, protected 
            internal parameters upon object creation.
        """
        self._errorCode = errorCode
        self._message = message
        self._affectedField = affectedField

    @property
    def getErrorCode(self) -> str:
        """
        Retrieves the strict programmatic identifier associated with the logic breach.

        Returns:
            The explicit categorical string flag defining the error type.

        Implementation Details:
            Grants superficial read access to the encapsulated error string via property constraints.
        """
        return self._errorCode

    @property
    def getMessage(self) -> str:
        """
        Retrieves the descriptive human-readable summary detailing the specific logic failure.

        Returns:
            The string explicitly explaining the violation context.

        Implementation Details:
            Grants superficial read access to the encapsulated message string via property constraints.
        """
        return self._message

    @property
    def getAffectedField(self) -> str:
        """
        Retrieves the defined operational scope or variable name responsible for the trigger.

        Returns:
            The specific string mapping the location of the faulted data.

        Implementation Details:
            Grants superficial read access to the encapsulated target field string via property constraints.
        """
        return self._affectedField