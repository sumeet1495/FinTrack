from typing import Final

# This class defines the status values used across APIs to represent the outcome of an operation.
class APIStatus:

    SUCCESS: Final[str] = "SUCCESS"
    FAILED: Final[str] = "FAILED"
    PENDING: Final[str] = "PENDING"