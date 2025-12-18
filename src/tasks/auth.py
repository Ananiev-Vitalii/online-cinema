import asyncio
from datetime import datetime, timezone
from sqlalchemy import delete
from database.db import SessionLocal
from database.models.accounts import RefreshToken, PasswordResetToken
from celery_app.auth import celery_app


@celery_app.task
def cleanup_expired_tokens() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_cleanup_expired_tokens())
    loop.close()


async def _cleanup_expired_tokens() -> None:
    now = datetime.now(timezone.utc)
    async with SessionLocal() as db:
        await db.execute(delete(RefreshToken).where(RefreshToken.expires_at < now))
        await db.execute(delete(PasswordResetToken).where(PasswordResetToken.expires_at < now))
        await db.commit()
        print("✅ Expired tokens cleaned up.")
