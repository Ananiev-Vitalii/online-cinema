import aiosmtplib
from email.mime.text import MIMEText

from core.config import settings


async def send_email(user_email: str, subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = user_email
    msg["Subject"] = subject

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            start_tls=settings.EMAIL_USE_TLS,
            timeout=10,
        )
        print(f"📨 Email sent successfully to {user_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


async def send_activation_email(user_email: str, token: str) -> None:
    subject = "Account Activation"
    verify_link = f"{settings.FRONTEND_URL}/api/v1/auth/verify?token={token}"
    body = f"Please click the following link to activate your account: \n\n{verify_link}"
    await send_email(user_email, subject, body)


async def send_password_reset_email(user_email: str, token: str) -> None:
    subject = "Password Reset Request"
    reset_link = f"{settings.FRONTEND_URL}/api/v1/auth/reset-password?token={token}"
    body = f"To reset your password, click the following link: \n\n{reset_link}"
    await send_email(user_email, subject, body)
