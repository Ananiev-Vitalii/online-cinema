import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile_unauthorized(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_unauthorized(async_client: AsyncClient) -> None:
    response = await async_client.put(
        "/api/v1/users/me/update",
        json={"first_name": "John"}
    )
    assert response.status_code == 401
