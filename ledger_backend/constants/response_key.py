from typing import Final
# This class defines constants for different types of error response keys.
class ResponseKey:

    ERROR_UNEXPECTED_RESPONSE: Final[str] = "error_unexpected_response"
    ERROR_BAD_INPUT: Final[str] = "error_bad_input"
    ERROR_BAD_ARGUMENT: Final[str] = "error_bad_{argument}"
    ERROR_INVALID_ARGUMENT: Final[str] = "error_invalid_{argument}"
    ERROR_INVALID_DOCUMENT: Final[str] = "error_invalid_{document}"