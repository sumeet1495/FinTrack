# Import necessary modules for handling datetime and generating unique ULIDs
from datetime import datetime
from ulid import ulid

# Import FastAPI and Starlette middleware base class for creating middleware
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Import logger for logging requests and middleware actions
from start_utils import logger

# Define the RequestContextMiddleware class, extending from BaseHTTPMiddleware
class RequestContextMiddleware(BaseHTTPMiddleware):
    
    # The dispatch method processes the request before and after it is handled by the main application
    async def dispatch(self, request: Request, call_next):
        # Code to execute before the request is processed by the main application

        # Log entry into the middleware
        logger.debug("Inside request context middleware")

        # Capture the start time of the request for performance tracking
        start_time: datetime = datetime.now()

        # Generate a unique request URN using ULID and store it in the request state
        logger.debug("Generating request urn", urn=None)
        request_urn: str = ulid()  # Generate a unique ULID
        request.state.urn = request_urn  # Store the URN in the request state
        logger.debug("Generated request urn", urn=request_urn)

        # Call the next middleware or route handler in the stack and get the response
        response: Response = await call_next(request)
        
        # After the request is processed, capture the end time and calculate the processing time
        end_time: datetime = datetime.now()
        process_time = end_time - start_time

        # Add custom headers to the response with the processing time and request URN
        logger.debug("Updating process time header", urn=request_urn)
        response.headers["X-Process-Time"] = str(process_time)  # Include processing time in headers
        response.headers["X-Request-URN"] = request_urn  # Include request URN in headers
        logger.debug("Updated process time header", urn=request_urn)
        
        # Return the response to the client
        return response
