import pytest

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_user(client) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "new@example.com"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client) -> None:
    await register_and_login(client, email="dup@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_success(client) -> None:
    await register_and_login(client, email="login@example.com")
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_invalid_password(client) -> None:
    await register_and_login(client, email="wrongpass@example.com")
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpass999"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_unauthorized_request(client) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"

