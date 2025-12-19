from fastapi import FastAPI
from routes import auth, user

app = FastAPI(
    title="Online Cinema API",
    version="1.0.0",
    description=(
        "Online Cinema API provides authentication, user management, and profile operations.\n\n"
        "Use this documentation to explore available endpoints for registration, login, password recovery, "
        "and profile management."
    ),
    openapi_tags=[
        {"name": "Auth", "description": "Endpoints for authentication, registration, and password management."},
        {"name": "User", "description": "Endpoints for viewing and updating user profiles."}
    ],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
