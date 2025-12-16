from fastapi import FastAPI
from routes import auth, user

app = FastAPI(
    title="Online Cinema API",
    version="0.1.0",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
