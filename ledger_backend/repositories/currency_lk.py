from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
#
from constants.db.table import Table
#
from models.currency_lk import CurrencyLK
#
from abstractions.repository import IRepository


# The CurrencyLKRepository class handles database operations related to the Currency Lookup table.
# It includes methods to create and retrieve all currency records.
class CurrencyLKRepository(IRepository):

    # Constructor initializes the repository with essential parameters such as URN, user URN, API name, and the database session.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None, session: Session = None):
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.session = session
        self.table = Table.CURRENCY_LK  # Refers to the Currency Lookup table in the database.

        # Ensure that a valid database session is passed to the repository.
        if not self.session:
            raise RuntimeError("DB session not found")

    # Method to create a new currency lookup record in the database.
    # It tracks the execution time for adding the record.
    def create_record(self, currency_lk: CurrencyLK) -> CurrencyLK:

        start_time = datetime.now()  # Record the start time of the operation.
        self.session.add(currency_lk)  # Add the new currency lookup record to the session.
        self.session.commit()  # Commit the session to persist the changes in the database.

        end_time = datetime.now()  # Record the end time after the commit.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return currency_lk  # Return the newly created currency lookup object.

    # Method to retrieve all records from the Currency Lookup table.
    # It returns a list of all currency records.
    def retrieve_all_records(self) -> List[CurrencyLK]:

        start_time = datetime.now()  # Record the start time before the query.
        records = self.session.query(CurrencyLK).all()  # Query the database for all currency records.

        end_time = datetime.now()  # Record the end time after the query.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return records  # Return the list of all currency lookup records.
