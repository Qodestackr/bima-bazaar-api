from pydantic import BaseModel

class DamageAssessmentOut(BaseModel):
    estimated_cost: float
    recommendations: str
    image_url: str

    class Config:
        orm_mode = True
