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
from dtos.requests.apis.fetch.statement import FetchStatementRequestDTO
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.apis.fetch.statement import FetchStatementService
#
from utilities.dictionary import DictionaryUtility


class FetchStatementController(IController):

    # Constructor to initialize the controller and set the API name
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.api_name = APILK.CREATE_TRANSACTION

    # GET method to handle fetching statement details
    async def get(self, request: Request, request_payload: FetchStatementRequestDTO):

        # Fetch and log the request URN for tracking
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn  # Retrieve the request's URN from state
        self.user_id = getattr(request.state, "user_id", None)  # Get user_id from the request state
        self.user_urn = getattr(request.state, "user_urn", None)  # Get user_urn from the request state
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)  # Bind logger
        self.dictionary_utility = DictionaryUtility(urn=self.urn)  # Initialize dictionary utility

        try:
            # Validate the incoming request payload
            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()  # Dump the request payload into a dictionary

            ## Validate the original request using request details
            await self.validate_request(
                urn=self.urn,  # Pass the URN for tracking
                user_urn=self.user_urn,  # Pass the user's URN
                request_payload=self.request_payload,  # Payload for validation
                request_headers=dict(request.headers.mutablecopy()),  # Log the request headers
                api_name=self.api_name,  # API name for reference
                user_id=self.user_id  # Pass the user ID
            )
            self.logger.debug("Validated request")

            # Modify the request payload after validation
            self.logger.debug("Updating request payload")
            self.request_payload.update(
                {
                    "user_id": self.user_id,  # Update with user_id from the state
                    "user_urn": self.user_urn  # Update with user_urn from the state
                }
            )
            self.logger.debug("Updated request payload")

            # Call the service to fetch the statement details
            self.logger.debug("Running fetch statement service")
            response_dto: BaseResponseDTO = await FetchStatementService(
                urn=self.urn,  # Pass URN for tracking
                user_urn=self.user_urn,  # Pass the user's URN
                api_name=self.api_name  # Pass the API name for logging
            ).run(
                data=self.request_payload  # Provide the updated request payload to the service
            )

            # Prepare success response metadata
            self.logger.debug("Preparing response metadata")
            http_status_code = HTTPStatus.OK  # Set HTTP status code to 200 OK
            self.logger.debug("Prepared response metadata")

        # Handle specific known errors (BadInputError and UnexpectedResponseError)
        except (BadInputError, UnexpectedResponseError) as err:

            self.logger.error(f"{err.__class__} error occurred while fetching statement: {err}")
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,  # Include the transaction URN
                status=APIStatus.FAILED,  # Mark the status as failed
                response_message=err.response_message,  # Provide the error message
                response_key=err.response_key,  # Error key for specific failure
                data={},  # No data in case of failure
                error={}  # No error details to expose
            )
            http_status_code = err.http_status_code  # Set the error's HTTP status code
            self.logger.debug("Prepared response metadata")

        # Handle general exceptions
        except Exception as err:

            self.logger.error(f"{err.__class__} error occurred while fetching statement: {err}")

            # Prepare a general error response for internal server errors
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,  # Include the transaction URN
                status=APIStatus.FAILED,  # Mark the status as failed
                response_message="Failed to fetch statement.",  # General error message
                response_key="error_internal_server_error",  # Error key for internal server error
                data={},  # No data in case of failure
                error={}  # No error details to expose
            )
            http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR  # Set HTTP status to 500
            self.logger.debug("Prepared response metadata")

        # Return the final JSON response with the appropriate status code and content
        return JSONResponse(
            content=response_dto.to_dict(),  # Convert response DTO to a dictionary
            status_code=http_status_code  # Set the status code for the response
        )
