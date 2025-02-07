from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class ClaimStatusEnum(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"

class ClaimBase(BaseModel):
    policy_id: int
    incident_date: datetime
    description: Optional[str] = None
    amount_claimed: float
    evidence_url: Optional[str] = None

class ClaimCreate(ClaimBase):
    pass

class ClaimUpdate(BaseModel):
    description: Optional[str] = None
    amount_claimed: Optional[float] = None
    evidence_url: Optional[str] = None
    status: Optional[ClaimStatusEnum] = None

class ClaimProcess(BaseModel):
    approved: bool
    amount_settled: Optional[float] = None

class ClaimOut(ClaimBase):
    id: int
    submission_date: datetime
    status: ClaimStatusEnum
    amount_settled: Optional[float] = None
    last_modified: datetime

    class Config:
        orm_mode = True
