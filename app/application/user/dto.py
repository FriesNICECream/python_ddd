from pydantic import BaseModel, EmailStr


class UserDTO(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: str
