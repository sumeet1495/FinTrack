from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
#
from constants.db.table import Table
#
from models.transaction import Transaction
#
from abstractions.repository import IRepository


# The TransactionRepository class is responsible for performing database operations related to transactions.
# It includes methods to create a new transaction and retrieve transaction records by payee and payer account URNs.
class TransactionRepository(IRepository):

    # Constructor initializes the repository with necessary parameters such as URN, user URN, API name, and the database session.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None, session: Session = None):
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.session = session
        self.table = Table.TRANSACTION  # Refers to the Transaction table in the database.

        # Ensure that a valid database session is provided.
        if not self.session:
            raise RuntimeError("DB session not found")
        
    # Method to create a new transaction record in the database.
    # It adds the transaction to the session and commits it to the database, logging the execution time.
    def create_record(self, transaction: Transaction) -> Transaction:

        start_time = datetime.now()  # Record the start time for tracking execution.
        self.session.add(transaction)  # Add the new transaction to the session.
        self.session.commit()  # Commit the session to persist the transaction.

        end_time = datetime.now()  # Record the end time after the commit.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return transaction  # Return the created transaction object.

    # Method to retrieve transaction records based on the payee account URN.
    # It fetches all transactions where the payee account matches the given URN.
    def retrieve_record_by_payee_account_urn(self, payee_account_urn: str) -> List[Transaction]:

        start_time = datetime.now()  # Record the start time before querying the database.
        record = self.session.query(Transaction).filter(Transaction.payee_account_urn == payee_account_urn).all()  # Query transactions by payee account URN.
        end_time = datetime.now()  # Record the end time after the query.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return record if record else None  # Return the list of transactions, or None if no records are found.
    
    # Method to retrieve transaction records based on the payer account URN.
    # It fetches all transactions where the payer account matches the given URN.
    def retrieve_record_by_payer_account_urn(self, payer_account_urn: str) -> List[Transaction]:

        start_time = datetime.now()  # Record the start time before querying the database.
        record = self.session.query(Transaction).filter(Transaction.payer_account_urn == payer_account_urn).all()  # Query transactions by payer account URN.
        end_time = datetime.now()  # Record the end time after the query.
        execution_time = end_time - start_time  # Calculate the total execution time.
        self.logger.info(f"Execution time: {execution_time} seconds")  # Log the execution time.

        return record if record else None  # Return the list of transactions, or None if no records are found.
