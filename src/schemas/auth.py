from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re

PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).+$")


class ValidatePassword(BaseModel):
    @field_validator("password", "new_password", check_fields=False)
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must include uppercase, lowercase, number, and special character."
            )
        return value


class BaseUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongPassword123"
            }
        }
    )


class UserCreate(BaseUser, ValidatePassword):
    """Used for user registration."""


class UserLogin(BaseUser):
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongPassword123"
            }
        }
    )


class PasswordResetConfirm(ValidatePassword):
    token: str
    new_password: str = Field(..., min_length=8)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongPassword123"
            }
        }
    )


class ChangePasswordRequest(ValidatePassword):
    old_password: str
    new_password: str = Field(..., min_length=8)
