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

class FetchUsrAccountService(IService):

    # Constructor to initialize the service and necessary repositories for fetching user accounts
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initialize repositories for accounts, balances, and users
        self.account_repository = AccountRepository(
            urn=self.urn,
            user_urn=self.user_urn,
            api_name=self.api_name,
            session=db_session
        )

        self.balances_repository = BalancesRepository(
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

    # Main method for executing the service logic
    async def run(self, data: dict) -> dict:

        # Fetch the user ID from the request data
        user_id: str = data.get("user_id")

        # Retrieve user details from the database based on the user ID
        self.logger.debug("Fetching user")
        user: User = self.user_repository.retrieve_record_by_id(
            id=user_id,
            is_deleted=False
        )

        # If the user does not exist, raise an error
        if not user:
            raise RuntimeError("User not found")

        # Fetch all accounts associated with the user ID
        accounts: List[Account] = self.account_repository.retrieve_records_by_user_id(
            user_id=user_id
        )

        # If no accounts are found for the user, raise an error
        if not accounts:
            raise RuntimeError("No accounts found for the given user")

        # Prepare a list to store account details
        account_details = []

        # Loop through all accounts and fetch balances for each account
        for account in accounts:
            # Fetch the currency details for the account using currency ID
            currency: CurrencyLK = currency_lk_global_context_by_id.get(account.currency_id)

            # If the currency is not found, raise an error
            if not currency:
                raise RuntimeError("Currency not found")

            # Fetch account balances for the account URN
            account_balances: Balances = self.balances_repository.retrieve_record_by_account_urn(
                account_urn=account.urn
            )

            # If account balances are not found, raise an error
            if not account_balances:
                raise RuntimeError("Account balances not found")

            # Append the account details including balances to the account_details list
            account_details.append({
                "account_urn": account.urn,
                "name": account.name,
                "currency": currency.name,
                "balances": {
                    "total_balance": account_balances.total_balance,
                    "total_credit_balance": account_balances.total_credit_balance,
                    "total_debit_balance": account_balances.total_debit_balance
                }
            })

        # Prepare the response payload with the user's accounts
        response_payload = {
            "user_urn": user.urn,
            "accounts": account_details  # Return all account details
        }

        # Prepare response metadata to send back to the user
        self.logger.debug("Preparing response metadata")
        response_dto: BaseResponseDTO = BaseResponseDTO(
            transaction_urn=self.urn,
            status=APIStatus.SUCCESS,
            response_message="Successfully displayed all ledger accounts for the user.",
            response_key="success_user_accounts_display",
            data=response_payload
        )
        http_status_code = HTTPStatus.OK
        self.logger.debug("Prepared response metadata")

        # Return the response data as a DTO
        return response_dto
