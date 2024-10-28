from pydantic import BaseModel

# DTO class for login requests, includes reference number, email, and password fields.
class LoginRequestDTO(BaseModel):

    reference_number: str
    email: str
    password: str
