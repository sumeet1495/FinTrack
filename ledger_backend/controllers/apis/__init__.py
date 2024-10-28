from fastapi import APIRouter
#
from controllers.apis.create.account import CreateAccountController
from controllers.apis.create.transaction import CreateTransactionController
from controllers.apis.fetch.statement import FetchStatementController
from controllers.apis.fetch.account import FetchAccountController
from controllers.apis.fetch.account_usr import FetchUsrAccountController
#
from start_utils import logger


# Initialize a new FastAPI router with the prefix "/apis"
router = APIRouter(prefix="/apis")

# Register the CreateAccountController's route for account creation
logger.debug(f"Registering {CreateAccountController.__name__} route.")
router.add_api_route(
    path="/create/account",  # Route for creating a new account
    endpoint=CreateAccountController().post,  # The POST method handler from the CreateAccountController
    methods=["POST"]  # HTTP method supported by this route
)
logger.debug(f"Registered {CreateAccountController.__name__} route.")

# Register the CreateTransactionController's route for transaction creation
logger.debug(f"Registering {CreateTransactionController.__name__} route.")
router.add_api_route(
    path="/create/transaction",  # Route for creating a new transaction
    endpoint=CreateTransactionController().post,  # The POST method handler from the CreateTransactionController
    methods=["POST"]  # HTTP method supported by this route
)
logger.debug(f"Registered {CreateTransactionController.__name__} route.")

# Register the FetchStatementController's route for fetching a statement
logger.debug(f"Registering {FetchStatementController.__name__} route.")
router.add_api_route(
    path="/fetch/statement",  # Route for fetching a statement
    endpoint=FetchStatementController().get,  # The GET method handler from the FetchStatementController
    methods=["POST"]  # HTTP method supported by this route (intentionally POST here)
)
logger.debug(f"Registered {FetchStatementController.__name__} route.")

# Register the FetchAccountController's route for fetching an account
logger.debug(f"Registering {FetchAccountController.__name__} route.")
router.add_api_route(
    path="/fetch/account",  # Route for fetching an account
    endpoint=FetchAccountController().get,  # The GET method handler from the FetchAccountController
    methods=["POST"]  # HTTP method supported by this route (intentionally POST here)
)
logger.debug(f"Registered {FetchAccountController.__name__} route.")

# Register the FetchUsrAccountController's route for fetching user-specific accounts
logger.debug(f"Registering {FetchUsrAccountController.__name__} route.")
router.add_api_route(
    path="/fetch/usr-account",  # Route for fetching user-specific accounts
    endpoint=FetchUsrAccountController().get,  # The GET method handler from the FetchUsrAccountController
    methods=["GET"]  # HTTP method supported by this route
)
logger.debug(f"Registered {FetchUsrAccountController.__name__} route.")
