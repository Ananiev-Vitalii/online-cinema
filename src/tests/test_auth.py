import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "testuser@example.com", "password": "StrongPass123!"}
    )
    assert response.status_code in (200, 400)
    data = response.json()
    assert "message" in data or "detail" in data


@pytest.mark.asyncio
async def test_login_invalid(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "notexist@example.com", "password": "Wrong123!"}
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.text


@pytest.mark.asyncio
async def test_refresh_invalid(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "fake-token"}
    )
    assert response.status_code == 401
    assert "Invalid or expired refresh token" in response.text


@pytest.mark.asyncio
async def test_request_password_reset(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/request-password-reset",
        json={"email": "unknown@example.com"}
    )
    assert response.status_code in (404, 403)
