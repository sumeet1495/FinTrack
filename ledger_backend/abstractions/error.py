from abc import ABC
from loguru import logger

# The IError class serves as a base class for all custom error types in the application.
# It inherits from Python's BaseException to function as an exception, and it includes logging functionality.
# The goal is to standardize error handling across the application by including unique reference numbers (URNs) and logging within each error instance.

class IError(BaseException):

    # Initializes the error with an optional unique reference number (URN) and sets up logging capabilities.
    def __init__(self, urn: str = None) -> None:
        self.urn = urn
        self.logger = logger
