from sqlalchemy import select
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from database.db import get_db
from core.config import settings
from services.email import send_activation_email, send_password_reset_email
from database.models.accounts import User, UserGroup, RefreshToken, PasswordResetToken
from schemas.common import MessageResponse
from schemas.auth import UserCreate, UserLogin, TokenPair, RefreshTokenRequest, PasswordResetRequest, \
    PasswordResetConfirm, ChangePasswordRequest
from security.auth import (
    hash_password, verify_password, create_access_token, decode_token, create_token_pair,
    delete_token, verify_token, create_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    group_result = await db.execute(select(UserGroup).where(UserGroup.name == "USER"))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Default group 'USER' not found. Please initialize user groups."
        )

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        group_id=group.id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=settings.VERIFY_TOKEN_EXPIRE_MINUTES)
    )
    await send_activation_email(user.email, token)

    return MessageResponse(
        message=(
            f"User '{user.email}' registered successfully. "
            "Please check your email to activate your account."
        )
    )


@router.post("/login", response_model=TokenPair)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Check your email."
        )

    token_pair = await create_token_pair(db_user.id, db)

    return TokenPair(**token_pair)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> dict:
    token_obj = await verify_token(RefreshToken, data.refresh_token, db)
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user_id = token_obj.user_id
    await delete_token(RefreshToken, data.refresh_token, db)
    return await create_token_pair(user_id, db)


@router.post("/logout")
async def logout(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    await delete_token(RefreshToken, data.refresh_token, db)
    return MessageResponse(message="Successfully logged out")


@router.get("/verify", include_in_schema=False)
async def verify_email(
        token: str = Query(...), db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="The token does not contain an email address.")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()

    return MessageResponse(message=f"Account {email} has been successfully activated. 🎉")


@router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not activated")

    token_value = await create_token(
        PasswordResetToken, user.id, settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS, db
    )

    await send_password_reset_email(user.email, token_value)

    return MessageResponse(message=f"Password reset link sent to {user.email}")


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    token_obj = await verify_token(PasswordResetToken, data.token, db)
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == token_obj.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = hash_password(data.new_password)
    await db.commit()

    await delete_token(PasswordResetToken, data.token, db)

    return MessageResponse(message="Password has been successfully reset.")


@router.post("/change-password")
async def change_password(
        data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    current_user.hashed_password = hash_password(data.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully.")
