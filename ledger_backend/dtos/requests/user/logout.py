from pydantic import BaseModel

# DTO class for logout requests, includes a reference number field.
class LogoutRequestDTO(BaseModel):

    reference_number: str
