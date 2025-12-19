from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db
from database.models.accounts import User, UserProfile
from security.auth import get_current_user
from schemas.user import UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me",
    summary="Get current user's profile",
    description="Returns the profile information of the currently authenticated user, including email and group.",
    response_model=UserProfileResponse,
)
async def get_my_profile(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return UserProfileResponse.model_validate(
        {
            **profile.__dict__,
            "email": current_user.email,
            "group": current_user.group.name,
        }
    )


@router.put(
    "/me/update",
    summary="Update current user's profile",
    description="Allows the current user to update personal details such as name, avatar, or bio.",
    response_model=UserProfileResponse,
)
async def update_my_profile(
        data: UserProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return UserProfileResponse.model_validate(
        {**profile.__dict__, "email": current_user.email}
    )
