# 🎬 Online Cinema — Authentication & User Management System

This project implements a modern **asynchronous FastAPI backend** for an online cinema platform.  
It focuses on authentication, user management, and supporting background tasks using Celery.

---

## ⚙️ Features Overview

### 🔐 Authentication System
Complete user authentication and management flow:

- **User registration** with password hashing (`bcrypt`)
- **Email verification** with activation links
- **JWT-based authentication** (access + refresh tokens)
- **Logout** (token revocation)
- **Password reset** via email
- **Change password** for logged-in users
- **Centralized config** through `.env` and `core/config.py`
- **Asynchronous email sending** using `aiosmtplib`

---

## 🧩 API Endpoints

All routes are available under the `/api/v1` prefix:

| Purpose | Method | Endpoint |
|----------|---------|----------|
| Register new user | `POST` | `/api/v1/auth/register` |
| Verify account (email link) | `GET` | `/api/v1/auth/verify` |
| Login (get access & refresh tokens) | `POST` | `/api/v1/auth/login` |
| Refresh JWT tokens | `POST` | `/api/v1/auth/refresh` |
| Logout (revoke refresh token) | `POST` | `/api/v1/auth/logout` |
| Request password reset | `POST` | `/api/v1/auth/request-password-reset` |
| Reset password using token | `POST` | `/api/v1/auth/reset-password` |
| Change password (authorized user) | `POST` | `/api/v1/auth/change-password` |
| Get user profile | `GET` | `/api/v1/user/profile` |
| Update user profile | `PUT` | `/api/v1/user/profile` |

---

## 🚀 How to Run the Project

Follow these steps to run the project locally.

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Ananiev-Vitalii/online-cinema.git
cd online-cinema
```
### 2️⃣ Install dependencies

Make sure you have Poetry installed.
Then run:
```bash
poetry install
```

### 3️⃣ Configure environment

Copy the environment template and fill in your own values:
```bash
cp .env.sample .env

```

### 4️⃣ Run database migrations

From the project root:
```bash
poetry run alembic upgrade head

```

### 5️⃣ Start the application

From inside the src/ directory:
```bash
poetry run uvicorn main:app --reload

```
The app will start on:

http://127.0.0.1:8000

### 6️⃣ (Optional) Start Celery workers

If you want background tasks (e.g. token cleanup) to work:
```bash
redis-server
poetry run celery -A celery_app.auth.celery_app worker --loglevel=info --pool=solo
poetry run celery -A celery_app.auth.celery_app beat --loglevel=info

```

---

## 🔁 JWT Refresh Tokens and Logout Support

Secure token lifecycle management:

- **RefreshToken model** linked to users (supports multiple tokens)
- **/api/v1/auth/refresh** — verifies and rotates tokens
- **/api/v1/auth/logout** — revokes refresh token
- Added environment variable `REFRESH_TOKEN_EXPIRE_HOURS`
- Fixed timezone comparison in token verification

---

## 🔑 Password Reset Functionality

Secure “Forgot Password” flow:

- **Models:** `PasswordResetToken` linked to `User`
- **Endpoints:**
  - `POST /api/v1/auth/request-password-reset`
  - `POST /api/v1/auth/reset-password`
- **Reusable logic:** unified token management in `security/auth.py`
- **Email service:** `send_password_reset_email()` for reset links
- **Env config:** `PASSWORD_RESET_TOKEN_EXPIRE_HOURS`

---

## 🔒 Change Password Functionality

- **Endpoint:** `POST /api/v1/auth/change-password`
- **Schema:** `ChangePasswordRequest`
- **Security:** verifies old password, hashes new one
- **Auth dependency:** `get_current_user()` extracts data from JWT

---

## 🧠 Password Validation

Centralized, regex-based password validation ensures:
- ≥8 characters
- Uppercase + lowercase
- Digit + special character  
Implemented via reusable `ValidatePassword` Pydantic mixin.

---

## ⚙️ Celery Integration

Used for **background cleanup** of expired tokens.

### 🧩 Features
- Automatic deletion of expired access, refresh, and reset tokens
- **Redis** as broker and result backend
- Periodic task via **Celery Beat**

### 🚀 Run Celery
```bash
redis-server
poetry run celery -A celery_app.auth.celery_app worker --loglevel=info --pool=solo
poetry run celery -A celery_app.auth.celery_app beat --loglevel=info
```
Environment:
```bash
REDIS_URL=redis://localhost:6379/0
TOKEN_CLEANUP_INTERVAL=3600
```

---

### 🗄️ Database Migrations (Alembic)

| Action           | Command                                                   |
| ---------------- | --------------------------------------------------------- |
| Create migration | `poetry run alembic revision --autogenerate -m "Message"` |
| Apply migration  | `poetry run alembic upgrade head`                         |
| Roll back        | `poetry run alembic downgrade -1`                         |
| History          | `poetry run alembic history`                              |

---

### 📖 API Documentation

Automatic Swagger and ReDoc available:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

---

### 🧪 Testing and Coverage

Tests for all custom authentication and user endpoints.

### Run tests

```bash
poetry run pytest --asyncio-mode=auto --cov=routes --cov-report=term-missing

```

---

### 🧩 Technologies Used

- FastAPI (async)

- SQLAlchemy (Async ORM)

- Alembic

- Pydantic v2

- Celery + Redis

- Pytest / HTTPX

- JWT (Jose)

---

### 👨‍💻 Author

- **GitHub:** [Ananiev-Vitalii](https://github.com/Ananiev-Vitalii/online-cinema)  
- **Developer:** Vitalii Ananiev
- **Email:** ananievvitalii10@gmail.com
