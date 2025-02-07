from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
from decimal import Decimal

class BenefitDict(BaseModel):
    """Schema for benefits dictionary validation"""
    __root__: Dict[str, bool]

class InsurancePlanBase(BaseModel):
    """Base schema for insurance plan data"""
    name: str
    provider: str
    monthly_premium: Decimal = Field(..., ge=0)
    benefits: Dict[str, bool]
    plan_type: str
    description: Optional[str] = None
    terms_conditions: Optional[str] = None

class InsurancePlanCreate(InsurancePlanBase):
    """Schema for creating a new insurance plan"""
    pass

class InsurancePlanUpdate(InsurancePlanBase):
    """Schema for updating an existing insurance plan"""
    suitability_score: Optional[float] = Field(None, ge=0, le=1)
    popularity_score: Optional[float] = Field(None, ge=0, le=1)

class InsurancePlanInDB(InsurancePlanBase):
    """Schema for insurance plan data as stored in database"""
    id: int
    suitability_score: float
    popularity_score: float

    class Config:
        orm_mode = True

class InsurancePlanCompare(InsurancePlanInDB):
    """Schema for insurance plan comparison response"""
    benefit_details: Optional[Dict[str, str]] = None
    comparison_highlights: Optional[Dict[str, str]] = None