from datetime import datetime
from sqlalchemy.orm import Session
#
from constants.db.table import Table
#
from models.account import Account
#
from abstractions.repository import IRepository


# AccountRepository is responsible for interacting with the `Account` table in the database.
# It includes methods for creating, retrieving, and updating accounts.
class AccountRepository(IRepository):

    # Constructor method to initialize the repository with essential data, such as URN, user URN, API name, and the database session.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None, session: Session = None):
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.session = session
        self.table = Table.ACCOUNT

        # Raise an error if the database session is not provided.
        if not self.session:
            raise RuntimeError("DB session not found")
    
    # Method to create and save a new `Account` record in the database.
    # It tracks the execution time for adding the record.
    def create_record(self, account: Account) -> Account:

        start_time = datetime.now()
        self.session.add(account)  # Add the new account to the session.
        self.session.commit()  # Commit the session to save the changes to the database.

        end_time = datetime.now()
        execution_time = end_time - start_time  # Calculate the execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")

        return account  # Return the newly created account object.

    # Method to retrieve an account by its unique URN (Universal Resource Name).
    # The function tracks the execution time for querying the record.
    def retrieve_record_by_urn(self, urn: str) -> Account:

        start_time = datetime.now()
        # Query the database for the account matching the given URN.
        record = self.session.query(Account).filter(Account.urn == urn).first()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        # Return the account record if found, otherwise return None.
        return record if record else None
    
    # Method to retrieve an account based on the `user_id` and account `name`.
    # This is useful to check if a user already has an account with a specific name.
    def retrieve_record_by_user_id_name(self, user_id: int, name: str) -> Account:

        start_time = datetime.now()
        # Query the database for the account matching the `user_id` and `name`.
        record = self.session.query(Account).filter(Account.user_id == user_id, Account.name == name).first()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        # Return the account record if found, otherwise return None.
        return record if record else None
    
    # Method to update an existing `Account` record with new data based on the provided URN.
    # This method allows you to update multiple fields of an account.
    def update_record(self, urn: str, new_data: dict) -> Account:
        
        start_time = datetime.now()
        # Retrieve the account to be updated.
        _account = self.session.query(Account).filter(Account.urn == urn).first()

        # Raise an error if the account is not found.
        if not _account:
            raise ValueError(f"Transaction Log with id {id} not found")
        
        # Update each attribute in the account with the new values.
        for attr, value in new_data.items():
            setattr(_account, attr, value)

        # Commit the changes to the database.
        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return _account  # Return the updated account object.
    
    # Method to retrieve all accounts associated with a specific user_id.
    # This function is useful when a user has multiple accounts.
    def retrieve_records_by_user_id(self, user_id: int) -> list[Account]:
        """
        Retrieve all accounts associated with a specific user_id.
        """
        start_time = datetime.now()
        
        # Query to get all accounts that match the user_id.
        records = self.session.query(Account).filter(Account.user_id == user_id).all()
        
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")
        
        # Return the list of accounts if found, otherwise return an empty list.
        return records if records else []
