from abc import ABC
#
from start_utils import logger

# The IService class is an abstract base class that provides a template for service classes.
# It initializes important attributes such as URN, user URN, and API name, along with setting up the logger for services.
class IService(ABC):

    # This constructor binds the URN, user URN, and API name to the service, allowing for context-specific logging.
    # The logger is configured to log information about the particular service execution using these attributes.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
