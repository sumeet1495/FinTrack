import json
#
from dtos.configurations.db import DBConfigurationDTO
#
from start_utils import logger

# This class, DBConfiguration, follows the Singleton pattern to ensure that only one instance of the database configuration is created.
# It loads the database configuration from a JSON file and provides a method to retrieve it as a DTO (Data Transfer Object).
# If the configuration file is missing or corrupted, it handles the errors gracefully by logging debug messages.

class DBConfiguration:
    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(DBConfiguration, cls).__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self):

        try:

            with open('config/db/config.json', 'r') as file:
                self.config = json.load(file)

        except FileNotFoundError:
            logger.debug('Config file not found.')

        except json.JSONDecodeError:
            logger.debug('Error decoding config file.')

    def get_config(self):
        return DBConfigurationDTO(
            user_name=self.config.get("user_name", {}),
            password=self.config.get("password", {}),
            host=self.config.get("host", {}),
            port=self.config.get("port", {}),
            database=self.config.get("database", {}),
        )