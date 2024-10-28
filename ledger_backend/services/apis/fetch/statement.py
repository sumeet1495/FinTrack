import ulid
import pandas as pd
#
from datetime import datetime
from http import HTTPStatus
from typing import List
#
from abstractions.service import IService
#
from constants.api_status import APIStatus
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
#
from models.currency_lk import CurrencyLK
from models.account import Account
from models.balances import Balances
from models.transaction import Transaction
from models.user import User
#
from repositories.account import AccountRepository
from repositories.balances import BalancesRepository
from repositories.transaction import TransactionRepository
from repositories.user import UserRepository
#
from start_utils import (
    db_session,
    currency_lk_global_context_by_id
)


# Service class responsible for fetching the user's account statement
class FetchStatementService(IService):

    # Constructor to initialize repositories and necessary context
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initializing repositories to interact with database tables
        self.account_repository = AccountRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            session=db_session
        )

        self.transaction_repository = TransactionRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            session=db_session         
        )

        self.user_repository = UserRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            session=db_session     
        )

    # Main logic to fetch account statement (credit and debit transactions)
    async def run(self, data: dict) -> dict:

        # Extracting account name and user ID from the request data
        account_name: str = data.get("account_name")
        user_id: str = data.get("user_id")

        # Fetch user details based on user_id
        self.logger.debug("Fetching user")
        user: User = self.user_repository.retrieve_record_by_id(
            id=user_id,
            is_deleted=False
        )

        # Raise an error if user is not found
        if not user:
            raise RuntimeError("User not found")
        
        # Fetch account URN from the request data
        account_urn = data.get("account_urn", "")

        # Check if account URN is provided; raise an error if missing
        if not account_urn:
            raise BadInputError(
                response_message="Account URN cannot be empty or none.",
                response_key="error_invalid_account_urn",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        # Initializing an empty list to collect all transaction data
        all_transactions = []

        # Fetching all credit transactions related to the account
        self.logger.debug("Fetching Credit transactions")
        credit_transactions: List[Transaction] = self.transaction_repository.retrieve_record_by_payee_account_urn(
            payee_account_urn=account_urn
        )

        # Handle if there are no credit transactions
        if credit_transactions is None:
           credit_transactions = []

        # Loop through all credit transactions and collect relevant data
        for credit_transaction in credit_transactions:
            payer_account = self.account_repository.retrieve_record_by_urn(
                urn=credit_transaction.payer_account_urn
            )
            payee_account = self.account_repository.retrieve_record_by_urn(
                urn=credit_transaction.payee_account_urn
            )
            # Fetching currency code associated with the transaction
            currency_code = None
            if payee_account:
              currency: CurrencyLK = currency_lk_global_context_by_id.get(payee_account.currency_id)
              currency_code = currency.code if currency else None

            # Storing credit transaction details in a dictionary
            transaction_data = {
                "transaction_urn": credit_transaction.urn,
                "payer_account_urn": credit_transaction.payer_account_urn,
                "payee_account_urn": credit_transaction.payee_account_urn,
                "amount": credit_transaction.amount,
                "currency_code": currency_code,
                "transaction_timestamp": credit_transaction.created_on,
                "transaction_type": "CREDIT",
                "payer_account_name": payer_account.name if payer_account else None,
                "payee_account_name": payee_account.name if payee_account else None,
                "purpose": credit_transaction.purpose
            }
            all_transactions.append(transaction_data)
        self.logger.debug("Fetched Credit transaction")

        # Fetching all debit transactions related to the account
        self.logger.debug("Fetching Debit transactions")
        debit_transactions: List[Transaction] = self.transaction_repository.retrieve_record_by_payer_account_urn(
            payer_account_urn=account_urn
        )

        # Handle if there are no debit transactions
        if debit_transactions is None:
           debit_transactions = []

        # Loop through all debit transactions and collect relevant data
        for debit_transaction in debit_transactions:
            payer_account = self.account_repository.retrieve_record_by_urn(
                urn=debit_transaction.payer_account_urn
            )
            payee_account = self.account_repository.retrieve_record_by_urn(
                urn=debit_transaction.payee_account_urn
            )

            # Fetching currency code associated with the transaction
            currency_code = None
            if payer_account:
              currency: CurrencyLK = currency_lk_global_context_by_id.get(payer_account.currency_id)
              currency_code = currency.code if currency else None

            # Storing debit transaction details in a dictionary
            transaction_data = {
                "transaction_urn": debit_transaction.urn,
                "payer_account_urn": debit_transaction.payer_account_urn,
                "payee_account_urn": debit_transaction.payee_account_urn,
                "amount": debit_transaction.amount,
                "currency_code": currency_code,
                "transaction_timestamp": debit_transaction.created_on,
                "transaction_type": "DEBIT",
                "payer_account_name": payer_account.name if payer_account else None,
                "payee_account_name": payee_account.name if payee_account else None,
                "purpose": debit_transaction.purpose
            }
            all_transactions.append(transaction_data)
        self.logger.debug("Fetched Debit transaction")

        # Convert transactions list to a pandas DataFrame for easier manipulation
        df_transactions = pd.DataFrame(data=all_transactions)
        df_transactions = df_transactions.sort_values(by="transaction_timestamp", ascending=False)
        df_transactions['transaction_timestamp'] = df_transactions['transaction_timestamp'].astype("string")

        # Convert DataFrame back to dictionary format to return in response
        all_transactions_data = df_transactions.to_dict("records")

        # Prepare the response DTO with transaction data
        self.logger.debug("Preparing response metadata")
        response_dto: BaseResponseDTO = BaseResponseDTO(
            transaction_urn=self.urn,
            status=APIStatus.SUCCESS,
            response_message="Successfully created ledger account.",
            response_key="success_payee_account_creation",
            data=all_transactions_data
        )
        http_status_code = HTTPStatus.OK
        self.logger.debug("Prepared response metadata")

        # Return the response DTO with the HTTP status code
        return response_dto
