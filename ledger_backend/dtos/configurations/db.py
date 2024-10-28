from dataclasses import dataclass

@dataclass
class DBConfigurationDTO:
    user_name: str
    password: str
    host: str
    port: int
    database: str
# This class defines a Data Transfer Object (DTO) for database configuration settings.
