import csv
import io
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.policy import PolicyCreate, PolicyOut
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/sacco", tags=["sacco"])

@router.post("/bulk-upload", response_model=List[PolicyOut])
async def bulk_upload_policies(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV file containing fleet policy data.
    
    Expected CSV headers: 
      matatu_registration, owner_name, coverage_type, premium_amount, end_date
      
    Example row:
      KAA 123A,John Doe,COMPREHENSIVE,5000.0,2024-12-31T00:00:00
    """
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. CSV required.")

    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    reader = csv.DictReader(io.StringIO(text))
    policies = []
    service = PolicyService(db)

    # Wrap the upload process in a transaction block
    async with db.begin():
        for row in reader:
            try:
                # Convert fields as needed
                row["premium_amount"] = float(row["premium_amount"])
                row["end_date"] = datetime.fromisoformat(row["end_date"])
                row["matatu_registration"] = row["matatu_registration"].strip().upper()

                policy_data = PolicyCreate(**row)
                policy = await service.create_policy(policy_data)
                policies.append(policy)
            except Exception as e:
                # In production, you might collect errors per row for a summary response.
                raise HTTPException(
                    status_code=422,
                    detail=f"Error processing row {row}: {str(e)}"
                )
    return policies
