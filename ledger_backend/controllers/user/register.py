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
from dtos.requests.user.register import RegisterRequestDTO
#
from dtos.responses.base import BaseResponseDTO
#
from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError
#
from services.user.register import UserRegistrationService
#
from utilities.dictionary import DictionaryUtility

# The RegisterController class is responsible for handling the registration process for new users.
class RegisterController(IController):

    # Constructor to initialize the controller and set the API name for logging purposes
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.api_name = APILK.REGISTER

    # POST method to handle user registration requests
    async def post(self, request: Request, request_payload: RegisterRequestDTO):

        # Fetch request URN and user details from request state, and bind logger with additional context
        self.logger.debug("Fetching request URN")
        self.urn = request.state.urn
        self.user_id = getattr(request.state, "user_id", None)
        self.user_urn = getattr(request.state, "user_urn", None)
        self.logger = self.logger.bind(urn=self.urn, user_urn=self.user_urn, api_name=self.api_name)
        self.dictionary_utility = DictionaryUtility(urn=self.urn)

        try:
            # Validate the incoming registration request payload
            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()
            await self.validate_request(
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name,
                user_id=None
            )
            self.logger.debug("Verified request")

            # Call the user registration service to handle the registration logic
            self.logger.debug("Running user registration service")
            user_registration_service = UserRegistrationService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name
            )
            response_payload: dict = await user_registration_service.run(
                data=request_payload.model_dump()
            )

            # Prepare response metadata for successful user registration
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.SUCCESS,
                response_message="Successfully Registered the user.",
                response_key="success_user_registration",
                data=response_payload
            )
            http_status_code = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        # Handle known errors like BadInputError and UnexpectedResponseError
        except (BadInputError, UnexpectedResponseError) as err:

            # Log the error and prepare a failure response with appropriate status and message
            self.logger.error(f"{err.__class__} error occurred while registering user: {err}")
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

        # Catch any unexpected errors and log them while preparing a generic failure response
        except Exception as err:

            # Log the error and prepare a failure response for internal server errors
            self.logger.error(f"{err.__class__} error occurred while registering user: {err}")

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=self.urn,
                status=APIStatus.FAILED,
                response_message="Failed to register user.",
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
