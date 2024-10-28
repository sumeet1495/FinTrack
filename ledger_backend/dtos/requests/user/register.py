from pydantic import BaseModel

# DTO class for user registration request, includes reference number, email, and password fields.
class RegisterRequestDTO(BaseModel):

    reference_number: str
    email: str
    password: str
