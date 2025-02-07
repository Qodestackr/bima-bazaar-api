from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["Payments"])

# capture payment callbacks
class MpesaCallback(BaseModel):
    transaction_id: str
    amount: float
    status: str

@router.post("/mpesa/callback")
async def mpesa_callback(callback: MpesaCallback):
    # TODO: Validate and process M-Pesa webhook data
    return {"status": "success", "message": "Payment callback processed"}
