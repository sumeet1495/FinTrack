# Import necessary modules from FastAPI and standard libraries
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from http import HTTPStatus  # For using standard HTTP status codes
from starlette.middleware.base import BaseHTTPMiddleware  # Middleware base class
from constants.api_status import APIStatus  # API status constants
from dtos.responses.base import BaseResponseDTO  # Base response DTO for standard responses
from repositories.user import UserRepository  # User repository for user data access
from start_utils import db_session, logger, unprotected_routes  # Utilities and database session
from utilities.jwt import JWTUtility  # Utility class for JWT token handling

# Define the AuthenticationMiddleware class, extending from BaseHTTPMiddleware
class AuthenticationMiddleware(BaseHTTPMiddleware):

    # The dispatch method processes every request before reaching the endpoint
    async def dispatch(self, request: Request, call_next):
        logger.debug("Inside authentication middleware")

        # Bypass authentication for OPTIONS HTTP method (used in CORS preflight requests)
        if request.method == "OPTIONS":
            logger.debug("OPTIONS request bypassed authentication")
            return await call_next(request)

        urn: str = request.state.urn  # Retrieve transaction URN (unique identifier)
        endpoint: str = request.url.path  # Get the current request's endpoint

        # If the endpoint is unprotected, allow access without authentication
        if endpoint in unprotected_routes or endpoint in ["/docs", "/redoc", "/openapi.json"]:
            logger.debug("Accessing Unprotected Route", urn=request.state.urn)
            response: Response = await call_next(request)
            return response
        
        # For protected routes, proceed with JWT token validation
        logger.debug("Accessing Protected Route", urn=request.state.urn)
        token: str = request.headers.get("authorization")  # Extract the Authorization header
        if not token or "bearer" not in token.lower():  # Check if bearer token is provided
            logger.debug("Preparing response metadata", urn=request.state.urn)
            # Prepare response DTO for failed authentication
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=urn,
                status=APIStatus.FAILED,
                response_message="JWT Authentication failed.",
                response_key="error_authetication_error",
                data={},
                error={}
            )
            http_status_code = HTTPStatus.UNAUTHORIZED  # Set response status to 401 Unauthorized
            logger.debug("Prepared response metadata", urn=request.state.urn)
            return JSONResponse(
                content=response_dto.to_dict(),
                status_code=http_status_code
            )

        try:
            # Attempt to decode the JWT token
            logger.debug("Decoding the authetication token", urn=request.state.urn)
            token = token.split(" ")[1]  # Extract the actual token part from 'Bearer <token>'

            # Decode the JWT token and retrieve user data
            user_data: dict = JWTUtility(
                urn=urn
            ).decode_token(token=token)
            logger.debug("Decoded the authetication token", urn=request.state.urn)

            # Verify if the user is still logged in by checking the session in the database
            logger.debug("Fetching user logged in status.", urn=request.state.urn)
            user = UserRepository(
                urn=urn,
                session=db_session
            ).retrieve_record_by_id_and_is_logged_in(
                id=user_data.get("user_id"),
                is_logged_in=True,
                is_deleted=False
            )
            logger.debug("Fetched user logged in status.", urn=request.state.urn)

            # If no user session is found, return a session expired error
            if not user:
                logger.debug("Preparing response metadata", urn=request.state.urn)
                response_dto: BaseResponseDTO = BaseResponseDTO(
                    transaction_urn=urn,
                    status=APIStatus.FAILED,
                    response_message="User Session Expired.",
                    response_key="error_session_expiry",
                )
                http_status_code = HTTPStatus.UNAUTHORIZED
                logger.debug("Prepared response metadata", urn=request.state.urn)
                return JSONResponse(
                    content=response_dto.to_dict(),
                    status_code=http_status_code
                )
            
            # Store the user ID and URN in the request state for use in other parts of the app
            request.state.user_id = user_data.get("user_id")
            request.state.user_urn = user_data.get("user_urn")
            
        # Handle any exceptions during the JWT authentication process
        except Exception as err:
            logger.debug(f"{err.__class__} occurred while authenticating jwt token, {err}", urn=request.state.urn)

            logger.debug("Preparing response metadata", urn=request.state.urn)
            # Prepare response DTO for failed authentication
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transaction_urn=urn,
                status=APIStatus.FAILED,
                response_message="JWT Authentication failed.",
                response_key="error_authetication_error"
            )
            http_status_code = HTTPStatus.UNAUTHORIZED
            logger.debug("Prepared response metadata", urn=request.state.urn)
            return JSONResponse(
                content=response_dto.to_dict(),
                status_code=http_status_code
            )
        
        # Proceed to the next middleware or endpoint after successful authentication
        logger.debug("Procceding with the request execution.", urn=request.state.urn)
        response: Response = await call_next(request)

        return response
