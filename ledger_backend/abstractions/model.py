from abc import ABC
from loguru import logger

# The IModel class serves as a base model that can be extended by other models in the system.
# It provides common attributes like URN for unique identification and a logger for logging operations.
class IModel:

    # Initializes the model with a unique URN for tracking and a logger for context-aware logging.
    # This ensures that all models inheriting from IModel have a standardized way to handle identification and logging.
    def __init__(self, urn: str = None) -> None:
        self.urn = urn
        self.logger = logger
