from abc import ABC
from loguru import logger

# The IRepository class is an abstract base class that defines the foundation for repositories in the system.
# It initializes common parameters like URN, user URN, API name, and a logger for all repository operations.
class IRepository(ABC):

    # Initializes the repository with key identifiers like URN, user URN, and API name.
    # Also binds the logger to these identifiers to provide context-specific logging across different repositories.
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
