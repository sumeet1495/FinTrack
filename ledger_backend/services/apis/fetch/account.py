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

# Service class responsible for fetching account details
class FetchAccountService(IService):

    # Constructor to initialize the necessary repositories and context
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initialize the repositories for account, balances, and user data
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

    # Method to handle the core logic of fetching account details
    async def run(self, data: dict) -> dict:

        # Fetching account name and user ID from the request data
        account_name: str = data.get("account_name")
        user_id: str = data.get("user_id")

        # Fetch the user details based on the user ID
        self.logger.debug("Fetching user")
        user: User = self.user_repository.retrieve_record_by_id(
            id=user_id,
            is_deleted=False
        )

        # Raise an error if the user is not found
        if not user:
            raise RuntimeError("User not found")
        
        # Get the account URN from the request data
        account_urn = data.get("account_urn", "")

        # Raise an error if the account URN is empty
        if not account_urn:
            raise BadInputError(
                response_message="Account URN cannot be empty or none.",
                response_key="error_invalid_account_urn",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Fetch the account details using the account URN
        account: Account = self.account_repository.retrieve_record_by_urn(
            urn=account_urn
        )

        # Raise an error if the account is not found
        if not account:
            raise BadInputError(
                response_message="Ledger account not found for the given urn",
                response_key="error_account_not_found",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Fetch the currency details for the account
        currency: CurrencyLK = currency_lk_global_context_by_id.get(account.currency_id)

        # Raise an error if the currency is not found
        if not currency:
            raise RuntimeError("Currency not found")
        
        # Fetch the account balances for the account URN
        account_balances: Balances = self.balances_repository.retrieve_record_by_account_urn(
            account_urn=account.urn
        )

        # Raise an error if the account balances are not found
        if not account_balances:
            raise RuntimeError("Account balances not found")
        
        # Prepare the response payload containing account details and balances
        response_payload = {
            "account_urn": account.urn,
            "user_urn": user.urn,
            "name": account.name,
            "currency": currency.name,
            "balances": {
                "total_balance": account_balances.total_balance,
                "total_credit_balance": account_balances.total_credit_balance,
                "total_debit_balance": account_balances.total_debit_balance
            }
        }

        # Log the preparation of response metadata
        self.logger.debug("Preparing response metadata")

        # Prepare the final response DTO to be sent back to the client
        response_dto: BaseResponseDTO = BaseResponseDTO(
            transaction_urn=self.urn,
            status=APIStatus.SUCCESS,
            response_message="Successfully displayed ledger account.",
            response_key="success_payee_account_display",
            data=response_payload
        )
        http_status_code = HTTPStatus.OK
        self.logger.debug("Prepared response metadata")

        # Return the response data and status code
        return response_dto
