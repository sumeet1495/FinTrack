from abstractions.error import IError

# Custom error class for handling bad input errors, inherits from IError and includes response message, key, and status code.
class BadInputError(IError):

    def __init__(self, response_message: str, response_key: str, http_status_code: int) -> None:

        super().__init__()
        self.response_message = response_message
        self.response_key = response_key
        self.http_status_code = http_status_code