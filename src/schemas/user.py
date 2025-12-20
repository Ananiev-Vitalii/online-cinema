from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from database.enums import GenderEnum


class UserProfileBase(BaseModel):
    first_name: str = None
    last_name: str = None
    gender: GenderEnum = None
    date_of_birth: date = None
    avatar: str = None
    info: str = None


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    email: EmailStr
    group: str

    model_config = ConfigDict(
        from_attributes=True
    )


class UserProfileUpdate(UserProfileBase):
    """Schema for updating user profile."""
