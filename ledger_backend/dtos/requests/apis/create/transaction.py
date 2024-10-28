from typing import Optional
#
from dtos.requests.apis.base import BaseRequestDTO

# DTO class for the Create Transaction request, containing optional payee and payer account URNs, and the transaction amount.
class CreateTransactionRequestDTO(BaseRequestDTO):

    payee_account_urn: Optional[str]
    payer_account_urn: Optional[str]
    amount: float