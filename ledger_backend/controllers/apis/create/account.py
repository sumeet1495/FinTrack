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
from dtos.requests.apis.create.account import CreateAccountRequestDTO
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.apis.create.account import CreateAccountService
#
from utilities.dictionary import DictionaryUtility


class CreateAccountController(IController):

    # Constructor to initialize the CreateAccountController
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)  # Call the parent class constructor
        self.api_name = APILK.CREATE_ACCOUNT  # Set the API name for logging and tracking

    # The POST method to handle the creation of an account
    async def post(self, request: Request, request_payload: CreateAccountRequestDTO):

        # Fetching the unique request URN (Universal Resource Name) for logging purposes
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn  # Get the URN from the request state
        self.user_id = getattr(request.state, "user_id", None)  # Get user_id from the request state
        self.user_urn = getattr(request.state, "user_urn", None)  # Get user_urn from the request state
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)  # Bind logger with URN and user details
        self.dictionary_utility = DictionaryUtility(urn=self.urn)  # Initialize dictionary utility

        try:

            # Validate the incoming request data
            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()  # Dump request data into a dictionary
            
            await self.validate_request(  # Perform validation using a utility
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),  # Copy request headers for validation
                api_name=self.api_name,
                user_id=self.user_id
            )
            self.logger.debug("Validated request")

            # Update the request payload with user details
            self.logger.debug("Updating request payload")
            self.request_payload.update(
                {
                    "user_id": self.user_id,  # Add user_id to the request payload
                    "user_urn": self.user_urn  # Add user_urn to the request payload
                }
            )
            self.logger.debug("Updated request payload")

            # Run the CreateAccountService to process the account creation
            self.logger.debug("Running create account service")
            response_dto: BaseResponseDTO = await CreateAccountService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name
            ).run(
                data=self.request_payload  # Pass the updated request payload to the service
            )

            # Prepare the response after successful account creation
            self.logger.debug("Preparing response metadata")
            http_status_code = HTTPStatus.OK  # Set HTTP status to 200 OK
            self.logger.debug("Prepared response metadata")

        # Handle specific errors like BadInputError or UnexpectedResponseError
        except (BadInputError, UnexpectedResponseError) as err:

            self.logger.error(f"{err.__class__} error occured while create account: {err}")
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(  # Prepare error response
                transaction_urn=self.urn,
                status=APIStatus.FAILED,
                response_message=err.response_message,  # Set error message
                response_key=err.response_key,  # Set error key
                data={},
                error={}
            )
            http_status_code = err.http_status_code  # Set HTTP status code based on the error
            self.logger.debug("Prepared response metadata")

        # Catch all other unexpected exceptions
        except Exception as err:

            self.logger.error(f"{err.__class__} error occured while create account: {err}")

            # Prepare a general error response for internal server errors
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,
                response_message="Failed to create account.",
                response_key="error_internal_server_error",
                data={},
                error={}
            )
            http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR  # Set HTTP status to 500
            self.logger.debug("Prepared response metadata")

        # Return the final JSON response with the appropriate status code and content
        return JSONResponse(
            content=response_dto.to_dict(),
            status_code=http_status_code
        )
