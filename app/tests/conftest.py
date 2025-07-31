import os
os.environ["ENV_STATE"] = "test"
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Request, Response, ASGITransport



from app.db.database import database
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac


