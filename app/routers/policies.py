from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.policy import PolicyCreate, Policy
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["policies"])

@router.post("/", response_model=Policy)
async def create_policy(policy: PolicyCreate, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    return await service.create_policy(policy)

@router.get("/{policy_id}", response_model=Policy)
async def get_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.get("/", response_model=list[Policy])
async def get_all_policies(db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    return await service.get_all_policies()

@router.put("/{policy_id}", response_model=Policy)
async def update_policy(policy_id: int, policy_data: dict, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    policy = await service.update_policy(policy_id, policy_data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.delete("/{policy_id}")
async def delete_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    service = PolicyService(db)
    success = await service.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.schemas.policy import PolicyOut, PolicyCreate
# from app.services.policy_service import create_policy, get_policies
# from app.db.database import get_db

# router = APIRouter(prefix="/policies", tags=["Policies"])

# @router.get("/", response_model=list[PolicyOut])
# async def read_policies(db: AsyncSession = Depends(get_db)):
#     policies = await get_policies(db)
#     return policies

# @router.post("/", response_model=PolicyOut)
# async def add_policy(policy: PolicyCreate, db: AsyncSession = Depends(get_db)):
#     new_policy = await create_policy(db, policy)
#     return new_policy
