import os

import pytest
import httpx


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def fastapi_app():
    assert os.getenv("DATABASE_URL"), "DATABASE_URL must be set for tests"
    from app.main import app
    return app


@pytest.fixture
async def client(fastapi_app):
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
