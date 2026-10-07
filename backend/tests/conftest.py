import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DB_PATH = Path(__file__).parent / "test.db"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123456")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{TEST_DB_PATH}")
os.environ.setdefault("OCR_PROVIDER", "mock")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MAX_UPLOAD_SIZE_MB", "1")

from app.db.base import Base  # noqa: E402
from app.db.database import get_db_session  # noqa: E402
from app.main import app  # noqa: E402

engine = create_async_engine(os.environ["DATABASE_URL"], future=True)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture(autouse=True)
async def clean_database() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    async with TestingSessionLocal() as db:
        yield db


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db_session] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


async def register_and_login(client: AsyncClient, email: str = "user@example.com", password: str = "strongpass123") -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture

def sample_pdf_bytes() -> bytes:
    return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


@pytest.fixture

def sample_jpg_bytes() -> bytes:
    return b"\xff\xd8\xff\xe0mockjpeg"


@pytest.fixture

def sample_png_bytes() -> bytes:
    return b"\x89PNG\r\n\x1a\nmockpng"

