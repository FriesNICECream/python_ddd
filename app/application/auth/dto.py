from pydantic import BaseModel, EmailStr, Field


class RegisterCommand(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginCommand(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisteredUserDTO(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: str


class AccessTokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
