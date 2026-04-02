from pydantic import BaseModel, EmailStr


class RegisterUserCommand(BaseModel):
    email: EmailStr
    full_name: str


class UserDTO(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: str
