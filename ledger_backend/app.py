# Import necessary modules and libraries
import cgi
import ulid
import uvicorn

# Import FastAPI and necessary FastAPI components
from fastapi import FastAPI

'''
Commented-out imports for authentication dependencies and OpenAPI schema customizations
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
'''

# Import exception handling, middleware, and response utilities from FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Import routers from your application controllers
from controllers.apis import router as APIsRouter
from controllers.user import router as UserRouter

# Import custom middlewares for authentication and request context
from middlewares.authetication import AuthenticationMiddleware
from middlewares.request_context import RequestContextMiddleware

# Import and configure CORS middleware to allow cross-origin resource sharing
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

# Import database utilities for creating tables
from start_utils import Base, engine
# Create tables in the database
Base.metadata.create_all(engine)

# Initialize FastAPI application
app = FastAPI()

# Configure CORS middleware to allow cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

'''
Custom OpenAPI schema generation (commented-out):
This section is used to define custom security schemas for your API documentation if needed.
It was commented out but can be used if JWT-based authentication is required for the OpenAPI documentation.
'''

'''
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API description",
        routes=app.routes,
    )
    openapi_schema["components"] = {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
'''

# Define a custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(request.state.urn)  # Log the transaction URN from the request context
    response_payload: dict = {
        "transaction_urn": request.state.urn,
        "response_message": "Bad or missing input.",
        "response_key": "error_bad_input",
        "errors": exc.errors()  # Provide validation error details
    }
    # Return a JSON response with status code 400 for bad input
    return JSONResponse(
        status_code=400,
        content=response_payload,
    )

# Add middleware for trusted hosts to ensure requests come from allowed hosts
app.add_middleware(
    middleware_class=TrustedHostMiddleware, 
    allowed_hosts=["*", "192.ABC.31.XYZ"]  # Define allowed hosts
)

# Log the initialization of the middleware stack
logger.debug("Initialising middleware stack")
# Add custom authentication and request context middlewares
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(RequestContextMiddleware)
logger.debug("Initialised middleware stack")

# Log the initialization of the routers
logger.debug("Initialising routers")
# Include the user router for user-related endpoints
app.include_router(UserRouter)
# Include the APIs router for other API-related endpoints
app.include_router(APIsRouter)
logger.debug("Initialised routers")

# Main entry point for the FastAPI app
if __name__ == '__main__':
    # Run the application using uvicorn, with hot-reloading enabled
    uvicorn.run("app:app", port=8002, host='127.0.0.1', reload=True)
