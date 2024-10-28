from dtos.requests.apis.base import BaseRequestDTO

# DTO class for fetching account details, requiring an account URN.
class FetchAccountRequestDTO(BaseRequestDTO):

    account_urn: str