import json
#
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
from dtos.requests.user.logout import LogoutRequestDTO
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.user.logout import UserLogoutService
#
from utilities.dictionary import DictionaryUtility


# LogoutController handles the process of logging out users by validating the request and calling the logout service
class LogoutController(IController):

    # Constructor for initializing the controller with optional URN and setting the API name
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.api_name = APILK.LOGOUT

    # POST method for handling logout requests
    async def post(self, request: Request, request_payload: LogoutRequestDTO):

        # Fetch the request URN and user info from the request context and bind logger details
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn
        self.user_id = getattr(request.state, "user_id", None)
        self.user_urn = getattr(request.state, "user_urn", None)
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
        self.dictionary_utility = DictionaryUtility(urn=self.urn)
    
        try:
            # Validate the incoming request payload and update it with the user_id
            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()
            self.request_payload.update({
                "user_id": request.state.user_id
            })
            
            await self.validate_request(
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name,
                user_id=self.user_id
            )
            self.logger.debug("Verified request")

            # Call the user logout service to process the logout request
            self.logger.debug("Running online user service")
            response_payload = await UserLogoutService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name
            ).run(
                data=self.request_payload
            )

            # Prepare the response metadata after a successful logout
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.SUCCESS,
                response_message="Successfully Logged Out the user.",
                response_key="success_user_logout",
                data=response_payload
            )
            http_status_code = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        # Handle specific known errors such as BadInputError and UnexpectedResponseError
        except (BadInputError, UnexpectedResponseError) as err:

            # Log the error and prepare a failure response with the error details
            self.logger.error(f"{err.__class__} error occurred while fetching online users: {err}")
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,
                response_message=err.response_message,
                response_key=err.response_key,
                data={},
                error={}
            )
            http_status_code = err.http_status_code
            self.logger.debug("Prepared response metadata")

        # Catch and handle any other unexpected errors during the process
        except Exception as err:

            # Log the error and prepare a generic failure response
            self.logger.error(f"{err.__class__} error occurred while fetching online users: {err}")

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,
                response_message="Failed to fetch online users.",
                response_key="error_internal_server_error",
                data={},
                error={}
            )
            http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            self.logger.debug("Prepared response metadata")

        # Return the final JSON response with the appropriate status code and response data
        return JSONResponse(
            content=response_dto.to_dict(),
            status_code=http_status_code
        )
