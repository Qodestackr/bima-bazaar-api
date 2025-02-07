from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.claim import ClaimCreate, ClaimOut, ClaimUpdate, ClaimProcess
from app.services.claim_service import ClaimService

router = APIRouter(prefix="/claims", tags=["claims"])

@router.post("/", response_model=ClaimOut)
async def submit_claim(claim: ClaimCreate, db: AsyncSession = Depends(get_db)):
    service = ClaimService(db)
    return await service.submit_claim(claim)

@router.get("/{claim_id}", response_model=ClaimOut)
async def get_claim(claim_id: int, db: AsyncSession = Depends(get_db)):
    service = ClaimService(db)
    return await service.get_claim(claim_id)

@router.put("/{claim_id}", response_model=ClaimOut)
async def update_claim(claim_id: int, claim_update: ClaimUpdate, db: AsyncSession = Depends(get_db)):
    service = ClaimService(db)
    return await service.update_claim(claim_id, claim_update)

@router.get("/", response_model=list[ClaimOut])
async def list_claims(policy_id: int = None, db: AsyncSession = Depends(get_db)):
    service = ClaimService(db)
    return await service.list_claims(policy_id)

@router.post("/{claim_id}/process", response_model=ClaimOut)
async def process_claim(claim_id: int, process_data: ClaimProcess, db: AsyncSession = Depends(get_db)):
    service = ClaimService(db)
    return await service.process_claim(claim_id, process_data.approved, process_data.amount_settled)
