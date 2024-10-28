from pydantic import BaseModel

# Base DTO class with common fields: reference number, consent, and purpose.
class BaseRequestDTO(BaseModel):

    reference_number: str
    consent: bool
    purpose: str