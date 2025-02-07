import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_policy():
    response = client.post("/policies/", json={
        "matatu_registration": "KAA 123A",
        "provider": "Old Mutual",
        "owner_name": "John Doe",
        "coverage_type": "comprehensive",
        "premium_amount": 5000.0,
        "end_date": "2024-12-31T00:00:00"
    })
    assert response.status_code == 200
    assert response.json()["matatu_registration"] == "KAA 123A"
    
# @pytest.mark.asyncio
# async def test_create_and_get_policy(async_client):
#     # Create a new policy
#     policy_data = {"name": "Matatu Basic", "provider": "Old Mutual", "premium": 500.0}
#     response = await async_client.post("/policies/", json=policy_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Matatu Basic"
    
#     # Get list of policies and check that the new one is there
#     response = await async_client.get("/policies/")
#     assert response.status_code == 200
#     policies = response.json()
#     assert any(p["name"] == "Matatu Basic" for p in policies)
