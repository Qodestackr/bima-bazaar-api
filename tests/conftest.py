import pytest
from httpx import AsyncClient
from app.main import app

# Fixture for an async test client
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
