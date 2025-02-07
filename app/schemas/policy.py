from pydantic import BaseModel

class PolicyBase(BaseModel):
    matatu_registration: str
    owner_name: str
    coverage_type: str
    premium_amount: float
    premium_period: str
    end_date: datetime
    name: str
    provider: str

class PolicyCreate(PolicyBase):
    pass

class PolicyOut(PolicyBase):
    id: int
    start_date: datetime
    status: str

    class Config:
        orm_mode = True
        # from_attributes = True
