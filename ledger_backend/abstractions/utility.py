from abc import ABC
from loguru import logger

# The IUtility class is an abstract base class that provides a common structure for utility classes.
# It initializes the URN, user URN, and API name, which can be useful for logging and identifying utility operations.
class IUtility(ABC):

    # This constructor initializes the utility with specific contextual information such as URN, user URN, and API name.
    # Additionally, it sets up a logger that is tailored to log messages within this context, making troubleshooting easier.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
