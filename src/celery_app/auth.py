import os
import sys
from celery import Celery

from core.config import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(BASE_DIR)
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

celery_app = Celery(
    "auth_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.imports = ("tasks.auth",)

celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens": {
        "task": "tasks.auth.cleanup_expired_tokens",
        "schedule": settings.TOKEN_CLEANUP_INTERVAL,
    },
}

celery_app.conf.timezone = "UTC"
