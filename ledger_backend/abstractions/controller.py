from abc import ABC
#
from errors.bad_input_error import BadInputError
#
from start_utils import db_session, logger
#
from utilities.dictionary import DictionaryUtility

# The IController class is an abstract base class (ABC) that other controllers will inherit from.
# It sets up basic properties such as URNs (unique reference numbers), API names, logging, and a utility for dictionary manipulation.
# It also includes a basic method for validating requests, which can be overridden by child classes as needed.

class IController(ABC):

    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        # Initializes the controller with URNs, user details, and API names.
        # Sets up logger and dictionary utilities for use within the controller.
        super().__init__()
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn)
        self.dictionary_utility = DictionaryUtility(urn=self.urn)

    # This method is a placeholder for validating requests. It's meant to be overridden by subclasses.
    # It takes in various parameters like the request payload, headers, and user ID.
    async def validate_request(
        self,
        urn: str,
        user_urn: str,
        request_payload: dict,
        request_headers: dict,
        api_name: str,
        user_id: str,
    ) -> None:
        
        # Validation logic would go here in subclasses, but the base method does nothing by default.
        self.user_urn = user_urn
        self.api_name = api_name

        return None
