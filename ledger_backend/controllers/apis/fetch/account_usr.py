from fastapi import Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
#
from abstractions.controller import IController
#
from constants.api_lk import APILK
from constants.api_status import APIStatus
#
from dtos.requests.apis.fetch.account_usr import FetchAccountUsrRequestDTO  # Updated import
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.apis.fetch.account_usr import FetchUsrAccountService
#
from utilities.dictionary import DictionaryUtility


class FetchUsrAccountController(IController):

    # Constructor to initialize the controller with the URN
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.api_name = APILK.CREATE_TRANSACTION  # Set the API name

    # GET method for fetching the user account information
    async def get(self, request: Request):  # Updated DTO name

        # Fetch and log the request URN for tracking
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn  # Retrieve the request's URN from state
        self.user_id = getattr(request.state, "user_id", None)  # Get user_id from the request state
        self.user_urn = getattr(request.state, "user_urn", None)  # Get user_urn from the request state
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)  # Bind logger
        self.dictionary_utility = DictionaryUtility(urn=self.urn)  # Initialize dictionary utility

        try:
            # Update the request payload with user information
            self.logger.debug("Updating request payload")
            self.request_payload = {
                "user_id": self.user_id,  # Include user_id in the payload
                "user_urn": self.user_urn  # Include user_urn in the payload
            }
            self.logger.debug("Updated request payload")

            # Call the service to fetch the user's account data
            self.logger.debug("Running fetch account service")
            response_dto: BaseResponseDTO = await FetchUsrAccountService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name
            ).run(
                data=self.request_payload  # Pass the updated payload to the service
            )

            # Prepare success response metadata
            self.logger.debug("Preparing response metadata")
            http_status_code = HTTPStatus.OK  # Set HTTP status code to 200 OK
            self.logger.debug("Prepared response metadata")

        # Handle known errors, such as validation or unexpected response errors
        except (BadInputError, UnexpectedResponseError) as err:

            self.logger.error(f"{err.__class__} error occurred while fetching account: {err}")
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,  # Mark the response as failed
                response_message=err.response_message,  # Provide an error message
                response_key=err.response_key,  # Error key for specific failure
                data={},
                error={}
            )
            http_status_code = err.http_status_code  # Use the error's HTTP status code
            self.logger.debug("Prepared response metadata")

        # Handle any other general exceptions
        except Exception as err:

            self.logger.error(f"{err.__class__} error occurred while fetching account: {err}")

            # Prepare a general error response for internal server issues
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,  # Mark the response as failed
                response_message="Failed to fetch account.",  # General error message
                response_key="error_internal_server_error",  # Error key for internal server error
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
