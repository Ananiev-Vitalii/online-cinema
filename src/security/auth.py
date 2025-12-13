import uuid
from typing import Type
from jose import JWTError, jwt
from typing import Any, Optional
from sqlalchemy import select, delete
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from core.config import settings
from database.models.accounts import RefreshToken, PasswordResetToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PASSWORD UTILS
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT ACCESS TOKEN
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# REFRESH / PASSWORD RESET TOKENS SYSTEM
async def create_token(model: Type[RefreshToken], user_id: int, lifetime_hours: int, db: AsyncSession) -> str:
    token_value = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=lifetime_hours)
    token_obj = model(user_id=user_id, token=token_value, expires_at=expires_at)
    db.add(token_obj)
    await db.commit()
    return token_value


async def delete_token(model: Type[RefreshToken], token: str, db: AsyncSession) -> None:
    await db.execute(delete(model).where(model.token == token))
    await db.commit()


async def verify_token(model: Type[RefreshToken], token: str, db: AsyncSession) -> Optional[RefreshToken]:
    result = await db.execute(select(model).where(model.token == token))
    token_obj = result.scalars().first()
    if not token_obj or token_obj.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return None
    return token_obj


async def create_token_pair(user_id: int, db: AsyncSession) -> dict:
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = await create_token(RefreshToken, user_id, settings.REFRESH_TOKEN_EXPIRE_HOURS, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
