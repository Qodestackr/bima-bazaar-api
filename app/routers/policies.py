from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyOut
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["policies"])

@router.post("/", response_model=PolicyOut, status_code=201)
async def create_policy(policy: PolicyCreate, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    return await service.create_policy(policy)

@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.get("/", response_model=List[PolicyOut])
async def get_all_policies(db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    return await service.get_all_policies()

@router.put("/{policy_id}", response_model=PolicyOut)
async def update_policy(policy_id: int, policy_data: dict, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    policy = await service.update_policy(policy_id, policy_data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.delete("/{policy_id}", status_code=204)
async def delete_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    success = await service.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return #{"message": "Policy deleted successfully"}...🫰No content to return; FastAPI handles 204 automatically
