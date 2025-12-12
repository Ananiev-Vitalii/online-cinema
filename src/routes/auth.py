from sqlalchemy import select
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from database.db import get_db
from core.config import settings
from services.email import send_activation_email
from database.models.accounts import User, UserGroup
from schemas.common import MessageResponse
from schemas.auth import UserCreate, UserLogin, Token
from security.auth import hash_password, verify_password, create_access_token, decode_token

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


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
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

    access_token = create_access_token({"sub": str(db_user.id)})

    return Token(access_token=access_token)


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
