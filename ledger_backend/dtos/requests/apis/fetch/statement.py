from dtos.requests.apis.base import BaseRequestDTO

# DTO class for fetching account statements, requiring an account URN.
class FetchStatementRequestDTO(BaseRequestDTO):

    account_urn: str