from pydantic import BaseModel

# DTO class for online users request, includes a reference number field.
class OnlineUsersRequestDTO(BaseModel):

    reference_number: str
