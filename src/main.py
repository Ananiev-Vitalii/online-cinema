from fastapi import FastAPI
from routes import auth

app = FastAPI(
    title="Online Cinema API",
    version="0.1.0",
)

app.include_router(auth.router, prefix="/api/v1")
