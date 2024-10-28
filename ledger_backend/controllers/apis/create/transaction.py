from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
#
from abstractions.controller import IController
#
from constants.api_lk import APILK
from constants.api_status import APIStatus
#
from dtos.requests.apis.create.transaction import CreateTransactionRequestDTO
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.apis.create.transaction import CreateTransactionService
#
from utilities.dictionary import DictionaryUtility


class CreateTransactionController(IController):

    # Constructor to initialize CreateTransactionController
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.api_name = APILK.CREATE_TRANSACTION  # Set API name for transaction

    # The POST method to handle creating a transaction
    async def post(self, request: Request, request_payload: CreateTransactionRequestDTO):

        # Fetch the request URN for tracking the transaction
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn
        self.user_id = getattr(request.state, "user_id", None)  # Retrieve user_id from request state
        self.user_urn = getattr(request.state, "user_urn", None)  # Retrieve user_urn from request state
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
        self.dictionary_utility = DictionaryUtility(urn=self.urn)  # Initialize dictionary utility for use

        try:

            # Validate the request payload data
            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()  # Convert request payload to dictionary
            
            await self.validate_request(  # Validate the request data
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),  # Copy headers for validation
                api_name=self.api_name,
                user_id=self.user_id
            )
            self.logger.debug("Validated request")

            # Update the request payload with additional user data
            self.logger.debug("Updating request payload")
            self.request_payload.update(
                {
                    "user_id": self.user_id,  # Add user_id to payload
                    "user_urn": self.user_urn  # Add user_urn to payload
                }
            )
            self.logger.debug("Updated request payload")

            # Call the service responsible for creating a transaction
            self.logger.debug("Running create transaction service")
            response_dto: BaseResponseDTO = await CreateTransactionService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name
            ).run(
                data=self.request_payload  # Pass the updated payload to the service
            )

            # Prepare the success response metadata
            self.logger.debug("Preparing response metadata")
            http_status_code = HTTPStatus.OK  # Set the response status to 200 OK
            self.logger.debug("Prepared response metadata")

        # Handle specific known errors, such as validation or unexpected response errors
        except (BadInputError, UnexpectedResponseError) as err:

            self.logger.error(f"{err.__class__} error occured while creating transaction: {err}")
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,  # Indicate failure
                response_message=err.response_message,  # Set the error message
                response_key=err.response_key,  # Set the error key
                data={},
                error={}
            )
            http_status_code = err.http_status_code  # Use the error's HTTP status code
            self.logger.debug("Prepared response metadata")

        # Catch and handle all other general exceptions
        except Exception as err:

            self.logger.error(f"{err.__class__} error occured while creating transaction: {err}")

            # Prepare a general failure response for internal server errors
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,  # Indicate failure
                response_message="Failed to create transaction.",  # General error message
                response_key="error_internal_server_error",  # Error key for internal server error
                data={},
                error={}
            )
            http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR  # Set status to 500 Internal Server Error
            self.logger.debug("Prepared response metadata")

        # Return the final JSON response with the appropriate status code and content
        return JSONResponse(
            content=response_dto.to_dict(),
            status_code=http_status_code
        )
