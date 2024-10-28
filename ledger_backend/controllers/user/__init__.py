# Import FastAPI's APIRouter for handling routes
from fastapi import APIRouter

# Import controllers for user login, logout, and register functionality
from controllers.user.login import LoginController
from controllers.user.logout import LogoutController
from controllers.user.register import RegisterController

# Import logger for logging information
from start_utils import logger

# Create an APIRouter with a prefix of "/user" for all routes related to user management
router = APIRouter(prefix="/user")

# Log the registration of the RegisterController route
logger.debug(f"Registering {RegisterController.__name__} route.")
# Add an API route for user registration (POST request) handled by RegisterController's post method
router.add_api_route(
    path="/register",  # The URL path for the register route
    endpoint=RegisterController().post,  # The controller method handling the request
    methods=["POST"]  # HTTP method used for the route
)
# Log that the registration route has been registered
logger.debug(f"Registered {RegisterController.__name__} route.")

# Log the registration of the LoginController route
logger.debug(f"Registering {LoginController.__name__} route.")
# Add an API route for user login (POST request) handled by LoginController's post method
router.add_api_route(
    path="/login",  # The URL path for the login route
    endpoint=LoginController().post,  # The controller method handling the request
    methods=["POST"]  # HTTP method used for the route
)
# Log that the login route has been registered
logger.debug(f"Registered {LoginController.__name__} route.")

# Log the registration of the LogoutController route
logger.debug(f"Registering {LogoutController.__name__} route.")
# Add an API route for user logout (POST request) handled by LogoutController's post method
router.add_api_route(
    path="/logout",  # The URL path for the logout route
    endpoint=LogoutController().post,  # The controller method handling the request
    methods=["POST"]  # HTTP method used for the route
)
# Log that the logout route has been registered
logger.debug(f"Registered {LogoutController.__name__} route.")
