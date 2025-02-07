from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class InsurancePlan(Base):
    """
    Insurance Plan model representing different insurance products.
    
    This model stores the core information about insurance plans that can be compared.
    Benefits are stored as a JSON field to allow flexible benefit structures.
    Suitability and popularity are used for ranking and recommendations.
    """
    __tablename__ = "insurance_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider = Column(String, index=True)
    monthly_premium = Column(Float, nullable=False)
    benefits = Column(JSON, nullable=False)  # Stores benefits as {"benefit_name": boolean}
    suitability_score = Column(Float, default=0.0)  # 0 to 1 score
    popularity_score = Column(Float, default=0.0)   # 0 to 1 score
    plan_type = Column(String, index=True)  # e.g., "COMPREHENSIVE", "THIRD_PARTY"
    description = Column(String, nullable=True)
    terms_conditions = Column(String, nullable=True)