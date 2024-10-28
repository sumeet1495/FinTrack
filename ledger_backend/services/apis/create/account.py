import ulid
#
import os
from datetime import datetime
from http import HTTPStatus
import smtplib  # Added for sending emails
from email.mime.multipart import MIMEMultipart  # Added for email format
from email.mime.text import MIMEText  # Added for email body content
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
from models.user import User
#
from repositories.account import AccountRepository
from repositories.balances import BalancesRepository
from repositories.user import UserRepository
#
from start_utils import (
    db_session,
    currency_lk_global_context_by_name
)


class CreateAccountService(IService):

    # Constructor to initialize the CreateAccountService with necessary repositories and session
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initializing repositories for account, balances, and user
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

    # Main method to execute account creation logic
    async def run(self, data: dict) -> dict:

        account_name: str = data.get("account_name")
        user_id: str = data.get("user_id")

        # Fetching the user based on user ID
        self.logger.debug("Fetching user")
        user: User = self.user_repository.retrieve_record_by_id(
            id=user_id,
            is_deleted=False
        )

        if not user:
            raise RuntimeError("User not found")

        # Check if the ledger account already exists for the user
        self.logger.debug("Fetching ledger account")
        ledger_account: Account = self.account_repository.retrieve_record_by_user_id_name(
            user_id=user_id,
            name=account_name,
        )

        if ledger_account:
            raise BadInputError(
                response_message="Ledger Account already exists for the given name for this user.",
                response_key="error_account_exists",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Fetching currency from global context based on the currency code provided
        self.logger.debug("Fetching currency")
        currency_code: str = data.get("currency_code")

        if currency_code not in set(currency_lk_global_context_by_name.keys()):
            raise BadInputError(
                response_message=f"Invalid currency code provided. Allowed values are {', '.join(list(currency_lk_global_context_by_name.keys()))}",
                response_key="error_invalid_currency_code",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        currency: CurrencyLK = currency_lk_global_context_by_name.get(currency_code)

        if not currency:
            raise BadInputError(
                response_message="Currency not found.",
                response_key="error_currency_not_found",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Creating the account for the user
        self.logger.debug("Creating Account")
        account: Account = Account(
            urn=f"ACCOUNT_{ulid.ulid()}",
            user_id=user_id,
            name=account_name,
            currency_id=currency.id,
            balance=0.0,
            is_deleted=False,
            created_on=datetime.now(),
            created_by=data.get("user_id")
        )

        account: Account = self.account_repository.create_record(
            account=account
        )
        self.logger.debug("Created Account")

        # Creating initial balance record for the new account
        self.logger.debug("Creating Account Balances")
        balances: Balances = Balances(
            account_id=account.id,
            account_urn=account.urn,
            total_balance=0.0,
            total_credit_balance=0.0,
            total_debit_balance=0.0,
            created_on=datetime.now(),
            created_by=data.get("user_id")
        )
        self.balances_repository.create_record(
            balances=balances
        )
        self.logger.debug("Created Account Balances")

        # Commit changes to the database
        self.logger.debug("Committing changes to the database")
        db_session.commit()
        self.logger.debug("Committed changes to the database")

        # Send email notification to the user about the new account creation
        self.send_account_creation_email(user, account, currency, balances)

        # Prepare the response payload to return
        response_payload = {
            "account_urn": account.urn,
            "user_urn": user.urn,
            "name": account.name,
            "currency": currency.name,
            "balances": {
                "total_balance": balances.total_balance,
                "total_credit_balance": balances.total_credit_balance,
                "total_debit_balance": balances.total_debit_balance
            }
        }

        # Preparing metadata for the response
        self.logger.debug("Preparing response metadata")
        response_dto: BaseResponseDTO = BaseResponseDTO(
            transaction_urn=self.urn,
            status=APIStatus.SUCCESS,
            response_message="Successfully created ledger account.",
            response_key="success_ledger_account_creation",
            data=response_payload
        )
        http_status_code = HTTPStatus.OK
        self.logger.debug("Prepared response metadata")

        return response_dto

    # Email sending logic 
    def send_account_creation_email(self, user: User, account: Account, currency: CurrencyLK, balances: Balances):
        # Fetching sender email and password from environment variables
        sender_email: str = os.getenv("sender_email")
        sender_password: str = os.getenv("sender_password")

        # Check if user email is available and prepare email content
        if user and user.email:
            subject = "FinTrack Account Creation Confirmation"
            message = (
                f"Dear User,\n\nYour account has been successfully created with the following details:\n\n"
                f"Account Number: {account.urn}\n"
                f"Account Name: {account.name}\n"
                f"Currency: {currency.name}\n"
                f"Total Balance: {balances.total_balance} {currency.name}\n"
                f"Total Credit Balance: {balances.total_credit_balance} {currency.name}\n"
                f"Total Debit Balance: {balances.total_debit_balance} {currency.name}\n\n"
                "Thank you for using our services!\n"
            )

            # Call the method to send the email
            self.send_email(user.email, subject, message, sender_email, sender_password)

    # Method to handle actual email sending using SMTP
    def send_email(self, recipient_email, subject, body, sender_email, sender_password):
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Setup SMTP server and send the email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            # Handle any errors during the email sending process
            print(f"Failed to send email to {recipient_email}: {e}")
