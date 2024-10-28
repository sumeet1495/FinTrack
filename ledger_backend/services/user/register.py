import bcrypt
import os
import ulid
#
from datetime import datetime
from http import HTTPStatus
#
from abstractions.service import IService
#
from errors.bad_input_error import BadInputError
#
from models.user import User
#
from repositories.user import UserRepository
#
from start_utils import db_session

class UserRegistrationService(IService):

    # Constructor to initialize the service with the required attributes and repository setup
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initializing the UserRepository with the required parameters
        self.user_repository = UserRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            session=db_session
        )

    # Main logic for the user registration process
    async def run(self, data: dict) -> dict:

        # Check if a user already exists with the given email
        self.logger.debug("Checking if user exists")
        user: User = self.user_repository.retrieve_record_by_email(
            email=data.get("email")
        )

        # If the user already exists, raise an error
        if user:
            self.logger.debug("User already exists")
            raise BadInputError(
                response_message="Email already registered. Please choose a different email address.",
                response_key="error_email_already_registered",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        # If the user does not exist, proceed with creating the new user
        self.logger.debug("Preparing user data")
        user: User = User(
            urn=ulid.ulid(),  # Generate a unique URN for the new user
            email=data.get("email"),
            password=bcrypt.hashpw(data.get("password").encode("utf-8"), os.getenv("BCRYPT_SALT").encode("utf8")).decode("utf8"),  # Hash the password using bcrypt
            is_deleted=False,
            created_at=datetime.now()  # Set the creation timestamp
        )
        
        # Save the user record in the database
        user: User = self.user_repository.create_record(
            user=user
        )
        self.logger.debug("Prepared user data")

        # Return relevant details of the newly created user
        return {
            "user_urn": user.urn,
            "user_email": user.email,
            "created_at": str(user.created_at)
        }
