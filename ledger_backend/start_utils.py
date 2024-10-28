# Import necessary Python libraries for environment variable loading, logging, and SQLAlchemy
import os
import sys
#
from dotenv import load_dotenv  # For loading environment variables from a .env file
from loguru import logger  # Loguru for enhanced logging features
from sqlalchemy import create_engine  # For creating a SQLAlchemy engine
from sqlalchemy.orm import sessionmaker  # For creating database sessions
from sqlalchemy.ext.declarative import declarative_base  # For defining SQLAlchemy ORM models
from typing import List  # For type hinting
#
# Import configurations, models, and utility classes from your application
from configurations.db import DBConfiguration, DBConfigurationDTO  # For database configuration
#
from models.currency_lk import CurrencyLK  # ORM model for CurrencyLK
#
from repositories.currency_lk import CurrencyLKRepository  # Repository for handling CurrencyLK data
#
from utilities.dictionary import DictionaryUtility  # Utility for dictionary operations

# Configure the loguru logger with a custom format and colorized output
logger.remove(0)
logger.add(sys.stderr, colorize=True, format="<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | <level>{level}</level> | <cyan>{message}</cyan> | <magenta>{name}:{function}:{line}</magenta> | <yellow>{extra}</yellow>")

# Load environment variables from the .env file using dotenv
load_dotenv()

# Log the start of configuration loading
logger.info("Loading Configurations")
db_configuration: DBConfigurationDTO = DBConfiguration().get_config()  # Load DB configurations
logger.info("Loaded Configurations")

# Access the necessary environment variables for app configuration and security
logger.info("Loading environment variables")
APP_NAME: str = os.environ.get('APP_NAME')  # Application name from environment
SECRET_KEY: str = os.getenv("SECRET_KEY")  # Secret key for app security
ALGORITHM: str = os.getenv("ALGORITHM")  # Algorithm used for token generation
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # Token expiry time
logger.info("Loaded environment variables")

# Initialize the MySQL database using SQLAlchemy
logger.info("Initializing MySQL database")
# Create an engine to connect to the MySQL database using the configuration values
engine = create_engine(f'mysql+pymysql://{db_configuration.user_name}:{db_configuration.password}@{db_configuration.host}:{db_configuration.port}/{db_configuration.database}')
# Set up the session maker for handling database sessions
Session = sessionmaker(bind=engine)
db_session = Session()  # Create a new database session
Base = declarative_base()  # Set up the base class for SQLAlchemy models
logger.info("Initialized MySQL database")

# Initialize the dictionary utility for use throughout the application
dictionary_utility = DictionaryUtility(urn=None)

# Log the start of registering CurrencyLK repository into the global context
logger.info(f"Registering {CurrencyLKRepository.__name__} global context.")
# Retrieve all records of CurrencyLK from the database using the repository pattern
currency_lk_records: List[CurrencyLK] = CurrencyLKRepository(
    urn=None, 
    session=db_session
).retrieve_all_records()

# Build a dictionary for CurrencyLK records with 'name' as the key
currency_lk_global_context_by_name: dict = dictionary_utility.build_dictonary_with_key(
    records=currency_lk_records,
    key="name"
)

# Build another dictionary for CurrencyLK records with 'id' as the key
currency_lk_global_context_by_id: dict = dictionary_utility.build_dictonary_with_key(
    records=currency_lk_records,
    key="id"
)
# Log the completion of registering CurrencyLK repository into the global context
logger.info(f"Registered {CurrencyLKRepository.__name__} global context.")

# Define a set of unprotected routes that do not require authentication
unprotected_routes: set = {
    "/user/register",
    "/user/login"
}

# Commit the session to save any pending changes to the database
db_session.commit()
