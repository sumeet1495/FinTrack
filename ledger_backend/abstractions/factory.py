from abc import ABC
from loguru import logger

# The IFactory class serves as an abstract base class for creating objects or services.
# It initializes shared attributes such as URN, user_URN, and api_name, and configures logging with contextual details.
class IFactory(ABC):

    # Initializes the factory with URN, user_URN, and api_name for tracking and logging purposes.
    # This ensures that any child class will have access to these attributes and the logger.
    def __init__(
        self, 
        urn: str = None, 
        user_urn: str = None, 
        api_name: str = None
    ) -> None:
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
