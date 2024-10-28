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


class CreateTransactionService(IService):

    # Constructor to initialize service and necessary repositories for transactions, accounts, balances, and users
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name

        # Initialize repositories for accounts, balances, transactions, and users
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

    # Main method for running transaction logic
    async def run(self, data: dict) -> dict:

        account_name: str = data.get("account_name")
        user_id: str = data.get("user_id")

        # Fetch the user by ID
        self.logger.debug("Fetching user")
        user: User = self.user_repository.retrieve_record_by_id(
            id=user_id,
            is_deleted=False
        )

        if not user:
            raise RuntimeError("User not found")
        
        # Get payee and payer account URNs
        payee_account_urn = data.get("payee_account_urn", "")
        payer_account_urn = data.get("payer_account_urn", "")

        # Validate if both payer and payee URNs are not empty
        if not payer_account_urn or not str(payer_account_urn).strip():
            payer_account_urn = None

        if not payee_account_urn or not str(payee_account_urn).strip():
            payee_account_urn = None

        if not payer_account_urn and not payee_account_urn:
            raise BadInputError(
                response_message="Payee and Payer Account URN both cannot be empty or none.",
                response_key="error_invalid_account_urn",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Check if payer and payee accounts are the same
        if payer_account_urn == payee_account_urn:
            raise BadInputError(
                response_message="Payer and Payee account URNs cannot be the same.",
                response_key="error_same_account_urn",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Fetch payee account and its balances if it exists
        payee_account = None
        payee_account_balances = None
        if payee_account_urn:

            self.logger.debug("Fetching payee account")
            payee_account: Account = self.account_repository.retrieve_record_by_urn(
                urn=payee_account_urn
            )

            if not payee_account:
                raise BadInputError(
                    response_message="Payee Account does not exist for the given urn.",
                    response_key="error_account_not_found",
                    http_status_code=HTTPStatus.BAD_REQUEST
                )
            
            # Assign currency_id from the payee account
            currency_id = payee_account.currency_id

            # Fetch payee balances
            self.logger.debug("Fetching payee account balances")
            payee_account_balances: Balances = self.balances_repository.retrieve_record_by_account_urn(
                account_urn=payee_account.urn
            )

            if not payee_account_balances:
                raise RuntimeError("Payee Account Balances not found")
            
        # Fetch payer account and its balances if it exists
        payer_account = None
        payer_account_balances = None
        if payer_account_urn:

            payer_account: Account = self.account_repository.retrieve_record_by_urn(
                urn=payer_account_urn
            )

            if not payer_account:
                raise BadInputError(
                    response_message="Payer Account does not exist for the given urn.",
                    response_key="error_account_not_found",
                    http_status_code=HTTPStatus.BAD_REQUEST
                )
            
            # Assign currency_id from the payer account
            currency_id = payer_account.currency_id

            # Fetch payer balances
            self.logger.debug("Fetching payer account balances")
            payer_account_balances: Balances = self.balances_repository.retrieve_record_by_account_urn(
                account_urn=payer_account.urn
            )

            if not payer_account_balances:
                raise RuntimeError("Payer Account Balances not found")
            
        # Check that one of the accounts belongs to the logged-in user
        payer_user_id = payer_account.user_id if payer_account else None
        payee_user_id = payee_account.user_id if payee_account else None
        
        self.logger.debug(f"payer user id: {payer_user_id}")
        self.logger.debug(f"payee user id: {payee_user_id}")

        # Ensure the logged-in user owns one of the accounts
        logged_in_user_id = user_id

        if payer_user_id != logged_in_user_id and payee_user_id != logged_in_user_id:
            raise BadInputError(
                response_message="At least one of the Payer or Payee accounts must belong to the logged-in user.",
                response_key="error_no_user_association",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        # Ensure payer and payee accounts have the same currency
        if payer_account and payee_account:
            if payer_account.currency_id != payee_account.currency_id:
                raise BadInputError(
                    response_message="Payee and Payer account currencies do not match.",
                    response_key="error_invalid_currency",
                    http_status_code=HTTPStatus.BAD_REQUEST
                )
        
        # Validate transaction amount
        amount = data.get("amount")

        if not amount or amount < 0:
            raise BadInputError(
                response_message="Invalid amount.",
                response_key="error_invalid_amount",
                http_status_code=HTTPStatus.BAD_REQUEST
            )
        
        # Check for sufficient balance in payer account
        if payer_account and amount > payer_account.balance:
            raise BadInputError(
                    response_message="Insufficient balance in payer account.",
                    response_key="error_insufficient_balance",
                    http_status_code=HTTPStatus.BAD_REQUEST
                )

        # Create a new transaction
        self.logger.debug("Creating transaction")
        purpose = data.get("purpose", "")  # Retrieve transaction purpose
        self.logger.debug(purpose)
        transaction: Transaction = Transaction(
            urn=ulid.ulid(),
            payer_account_id=payer_account.id if payer_account else None,
            payer_account_urn=payer_account.urn if payer_account else None,
            payee_account_id=payee_account.id if payee_account else None,
            payee_account_urn=payee_account.urn if payee_account else None,
            amount=amount,
            purpose=purpose,
            created_on=datetime.now(),
            created_by=user.id
        )

        transaction: Transaction = self.transaction_repository.create_record(
            transaction=transaction
        )
        self.logger.debug("Created transaction")

        # Update balances for both payer and payee accounts
        self.logger.debug("Updating Payer Account Balances")
        if payer_account_balances:
            payer_account_balances.total_debit_balance += amount
            payer_account_balances.total_balance -= amount

        if payer_account:
            payer_account.balance -= amount
        self.logger.debug("Updated Payer Account Balances")

        self.logger.debug("Updating Payee Account Balances")
        if payee_account_balances:
            payee_account_balances.total_credit_balance += amount
            payee_account_balances.total_balance += amount

        if payee_account:
            payee_account.balance += amount
        self.logger.debug("Updated Payee Account Balances")

        # Commit changes to the database
        self.logger.debug("Committing changes to the database")
        db_session.commit()
        self.logger.debug("Committed changes to the database")

        # Send email notifications for the transaction
        self.send_transaction_emails(payer_account, payee_account, amount, currency_id)

        # Prepare response payload
        response_payload = {
            "transaction_urn": transaction.urn,
            "user_urn": user.urn,
            "payee_account_urn": transaction.payee_account_urn,
            "payer_account_urn": transaction.payer_account_urn,
            "currency": currency_lk_global_context_by_id.get(currency_id).name,
            "amount": transaction.amount
        }

        # Return the response with success message
        self.logger.debug("Preparing response metadata")
        response_dto: BaseResponseDTO = BaseResponseDTO(
            transaction_urn=self.urn,
            status=APIStatus.SUCCESS,
            response_message="Successfully created ledger transaction.",
            response_key="success_payee_account_creation",
            data=response_payload
        )
        http_status_code = HTTPStatus.OK
        self.logger.debug("Prepared response metadata")

        return response_dto

    # Email sending logic for payer and payee accounts
    def send_transaction_emails(self, payer_account, payee_account, amount, currency_id):
        currency_code = currency_lk_global_context_by_id.get(currency_id).name
        sender_email: str = os.getenv("sender_email")
        sender_password: str = os.getenv("sender_password")

        # Fetch associated users for both payer and payee accounts
        payer_user = self.user_repository.retrieve_record_by_id(id=payer_account.user_id) if payer_account and payer_account.user_id else None
        payee_user = self.user_repository.retrieve_record_by_id(id=payee_account.user_id) if payee_account and payee_account.user_id else None

        # Send email notifications to both payer and payee if their emails exist
        if payer_user and payer_user.email:
            payer_message = f"Your account {payer_account.urn} has been debited by {amount} {currency_code}. The amount was credited to account {payee_account.urn if payee_account else 'N/A'}. Remaining balance is {payer_account.balance} {currency_code}."
            self.send_email(payer_user.email, "FinTrack Debit Transaction Alert", payer_message, sender_email, sender_password)
        
        if payee_user and payee_user.email:
            payee_message = f"Your account {payee_account.urn} has been credited with {amount} {currency_code} from account {payer_account.urn if payer_account else 'N/A'}. Remaining balance is {payee_account.balance} {currency_code}."
            self.send_email(payee_user.email, "FinTrack Credit Transaction Alert", payee_message, sender_email, sender_password)
    
    # Method to handle actual email sending
    def send_email(self, recipient_email, subject, body, sender_email, sender_password):
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Sending email using Gmail SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {e}")
