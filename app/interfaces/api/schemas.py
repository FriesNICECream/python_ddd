from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    full_name: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: str
