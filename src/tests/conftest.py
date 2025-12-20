import pytest
from typing import Any, AsyncGenerator
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture(autouse=True)
def mock_email_send(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_send_email(*args, **kwargs) -> None:
        print("📨 Fake email sent")
        return None

    monkeypatch.setattr("services.email.send_activation_email", fake_send_email)
    monkeypatch.setattr("services.email.send_password_reset_email", fake_send_email)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
