import re
#
from loguru import logger
from typing import List
#
from abstractions.utility import IUtility

# DictionaryUtility class provides several utility methods for processing dictionaries, 
# such as converting case formats, building dictionaries from records, and masking values.
class DictionaryUtility(IUtility):

    # Initialize the utility with a unique request identifier (URN) and set up logging.
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.urn = urn
        self.logger = logger

    # Build a dictionary from a list of records using the specified attribute (key) as the dictionary key.
    def build_dictonary_with_key(self, records: List, key: str):

        result: dict = dict()

        for record in records:
            result[getattr(record, key)] = record

        return result
    
    # Convert a snake_case string to camelCase. 
    # This is commonly used when switching between database field names and JavaScript object names.
    def snake_to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    # Recursively convert all keys in a dictionary from snake_case to camelCase.
    # Handles nested dictionaries and lists of dictionaries.
    def convert_dict_keys_to_camel_case(self, data):
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                new_key = self.snake_to_camel_case(k)
                new_dict[new_key] = self.convert_dict_keys_to_camel_case(v)
            return new_dict
        elif isinstance(data, list):
            return [self.convert_dict_keys_to_camel_case(item) for item in data]
        else:
            return data
        
    # Convert a camelCase string to snake_case.
    # This is useful when converting JSON data into database fields or Python variables.
    def camel_to_snake_case(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    # Recursively convert all keys in a dictionary from camelCase to snake_case.
    # Similar to the camel to snake case conversion, but handles nested dictionaries and lists.
    def convert_dict_keys_to_snake_case(self, data: dict):

        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                new_key = self.camel_to_snake_case(k)
                new_dict[new_key] = self.convert_dict_keys_to_snake_case(v)
            return new_dict

        elif isinstance(data, list):

            return [self.convert_dict_keys_to_snake_case(item) for item in data]

        else:
            return data
        
    # Mask sensitive values in a dictionary or list.
    # Strings are replaced with 'X's, integers and floats are zeroed out.
    def mask_value(self, value):
        if isinstance(value, str):
            return 'X' * len(value)
        elif isinstance(value, int):
            return 0
        elif isinstance(value, float):
            return 0.0
        return value

    # Recursively apply the mask_value function to all values in a dictionary or list.
    # Useful for masking sensitive data before logging or sending to a third-party service.
    def mask_dict_values(self, data):
        if isinstance(data, dict):
            return {k: self.mask_dict_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.mask_dict_values(item) for item in data]
        else:
            return self.mask_value(data)
        
    # Recursively remove specified keys from a dictionary.
    # Useful for removing unnecessary or sensitive fields before returning or saving data.
    def remove_keys_from_dict(self, data: dict, keys_to_remove: List[str]) -> dict:
        """
        Remove specified keys from a dictionary recursively.
        
        :param d: Dictionary from which keys need to be removed.
        :param keys_to_remove: Set of keys to remove.
        :return: Dictionary with specified keys removed.
        """
        if isinstance(data, dict):
            return {k: self.remove_keys_from_dict(v, keys_to_remove) for k, v in data.items() if k not in keys_to_remove}
        elif isinstance(data, list):
            return [self.remove_keys_from_dict(i, keys_to_remove) for i in data]
        else:
            return data
