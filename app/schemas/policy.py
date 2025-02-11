from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PolicyBase(BaseModel):
    matatu_registration: str
    owner_name: str
    sacco_name: str          
    route_number: str        
    coverage_type: str
    premium_period: str
    end_date: datetime
    provider: str

class PolicyCreate(PolicyBase):
    # premium_amount will be auto-calculated
    pass

class PolicyOut(PolicyBase):
    id: int
    premium_amount: float
    start_date: datetime
    status: str
    is_active: bool
    last_modified: datetime

    class Config:
        orm_mode = True

class PolicyUpdate(BaseModel):
    owner_name: Optional[str] = None
    sacco_name: Optional[str] = None
    route_number: Optional[str] = None
    coverage_type: Optional[str] = None
    premium_period: Optional[str] = None
    end_date: Optional[datetime] = None
    provider: Optional[str] = None

    class Config:
        orm_mode = True
