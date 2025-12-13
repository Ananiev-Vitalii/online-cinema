from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseUser):
    """Used for user registration."""


class UserLogin(BaseUser):
    """Used for user login."""


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
