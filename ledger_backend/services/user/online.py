import ulid
#
from datetime import datetime
from typing import Dict, List
#
from abstractions.service import IService
#
from models.user import User
#
from repositories.user import UserRepository
#
from start_utils import db_session, logger


class OnlineUsersService(IService):

    # Constructor to initialize the service with required dependencies
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

    # Method to execute the logic for fetching online users
    async def run(self, data: dict) -> List[Dict[str, str]]:

        # Fetch the list of online users (who are logged in and not deleted)
        self.logger.debug("Fetching online users")
        users: List[User] = UserRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            db_session=db_session
        ).get_record_by_is_logged_in(
            is_logged_in=True,
            is_deleted=False
        )
        self.logger.debug("Fetched online users")

        # Prepare the user data for the response
        self.logger.debug("Preparing online user data")
        online_user_data: list = list()
        for user in users:

            # For each user, create a dictionary with their ID and login status
            user_data: dict = {
                "id": user.id,
                "is_logged_in": user.is_logged_in
            }

            # Append the prepared user data to the list
            online_user_data.append(user_data)
        self.logger.debug("Prepared online user data")

        # Return the list of online users
        return user_data
