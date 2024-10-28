from datetime import datetime
from sqlalchemy.orm import Session
#
from constants.db.table import Table
#
from models.balances import Balances
#
from abstractions.repository import IRepository


# The BalancesRepository class handles database operations for the Balances table.
# It includes methods to create and retrieve balance records.
class BalancesRepository(IRepository):

    # Constructor initializes the repository with essential parameters such as URN, user URN, API name, and the database session.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None, session: Session = None):
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.session = session
        self.table = Table.BALANCES

        # If the session is not provided, raise an error as database operations cannot function without a session.
        if not self.session:
            raise RuntimeError("DB session not found")
    
    # Method to create a new `Balances` record in the database.
    # It tracks the execution time for adding the record to the database.
    def create_record(self, balances: Balances) -> Balances:

        start_time = datetime.now()  # Record the start time before the operation begins.
        self.session.add(balances)  # Add the new balances record to the session.
        self.session.commit()  # Commit the session to persist the changes in the database.

        end_time = datetime.now()  # Record the end time once the operation is complete.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return balances  # Return the newly created balances object.

    # Method to retrieve a `Balances` record by its associated account URN (unique identifier for an account).
    # This is useful for checking the balance associated with a specific account.
    def retrieve_record_by_account_urn(self, account_urn: str) -> Balances:

        start_time = datetime.now()  # Record the start time before the query.
        # Query the database for the balance record that matches the given account URN.
        record = self.session.query(Balances).filter(Balances.account_urn == account_urn).first()
        end_time = datetime.now()  # Record the end time after the query completes.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        # Return the balance record if found; otherwise, return None.
        return record if record else None
