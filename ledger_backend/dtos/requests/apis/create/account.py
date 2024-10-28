from typing import Optional
#
from dtos.requests.apis.base import BaseRequestDTO

# DTO class for the Create Account request, containing account name and currency code fields.
class CreateAccountRequestDTO(BaseRequestDTO):

    account_name: str
    currency_code: str

