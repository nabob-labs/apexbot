"""Base exception classes for apexbot."""


class ApexbotError(Exception):
    """Base exception used as the parent class for all exceptions raised by this package.

    Calling code should catch `ApexbotError` and derived classes separately before general
    exceptions, e.g.:

    ```
    try:
        apexbot.some_function()
    except SpecificApexbotError:
        ...  # handle a specific exception
    except ApexbotError:
        ...  # handle non-specific apexbot exception
    except Exception:
        ...  # handle exceptions raised by 3rd party dependencies or Python built-ins
    ```

    An optional string-formatted message may be attached to the exception and retrieved by accessing
    the `.message` attribute.
    """

    message: str | None = None

    def __init__(self, *, message: str | None = None) -> None:
        """Initialize the instance."""
        if message:
            self.message = message
            super().__init__(message)


class ApexbotValueError(ApexbotError):
    """ApexbotValueError error."""


"""ApexbotValueError class."""


class ApexbotTypeError(ApexbotError):
    """ApexbotTypeError error."""


"""ApexbotTypeError class."""
