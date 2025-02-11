from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    matatu_registration = Column(String, unique=True, index=True, nullable=False)
    owner_name = Column(String, nullable=False)
    sacco_name = Column(String, nullable=False, index=True)
    route_number = Column(String, nullable=False, index=True)  # 👉(risk factor).
    coverage_type = Column(String, nullable=False, index=True) # COMPREHENSIVE, THIRD_PARTY,...
    premium_amount = Column(Float, nullable=False)
    provider = Column(String) 
    premium_period = Column(String, nullable=False)  # e.g., "monthly", "quarterly"
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime, nullable=False)
    
    status = Column(String, default="ACTIVE")
    is_active = Column(Boolean, default=True, index=True)
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_end_date'),
    )
    
    def __repr__(self):
        return f"<Policy {self.matatu_registration}>"
