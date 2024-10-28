import jwt
#
from datetime import datetime, timedelta
from jwt import PyJWTError
from typing import Dict, Union
#
from abstractions.utility import IUtility
#
from start_utils import logger, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES 


# JWTUtility handles the creation and validation (decoding) of JWT tokens.
# This utility is key for user authentication and session management in the application.
class JWTUtility(IUtility):

    # Initialize the utility with a unique request identifier (URN).
    # The logger is also initialized to track events or errors during the token process.
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.urn = urn
        self.logger = logger

    # Create a new JWT access token by encoding the provided data.
    # The token will expire based on the `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable.
    def create_access_token(self, data: dict) -> str:

        # Copy data to avoid modifying the original input dictionary.
        to_encode = data.copy()

        # Set token expiration time. If no expiration time is defined, default to 15 minutes.
        if ACCESS_TOKEN_EXPIRE_MINUTES:
            expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        
        # Add the expiration timestamp to the token payload.
        to_encode.update({"exp": expire})

        # Encode the token with the SECRET_KEY and the specified ALGORITHM.
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    # Decode and verify a given JWT token to extract its payload.
    # If the token is invalid or expired, an error will be raised.
    def decode_token(self, token: str) -> Union[Dict[str, str]]:
        try:

            # Log the token, secret key, and algorithm for debugging purposes.
            print(token, SECRET_KEY, ALGORITHM)

            # Decode the token using the secret key and the specified algorithm.
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        
        except PyJWTError as err:
            # Log and re-raise the error if token decoding fails.
            print(err)
            raise err
