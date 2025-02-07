from sqlalchemy import Column, Integer, String, Float, DateTime,func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    matatu_registration = Column(String, unique=True, index=True, nullable=False)
    owner_name = Column(String, nullable=False)
    coverage_type = Column(String, nullable=False, index=True) # e.g., comprehensive, third-party
    premium_amount = Column(Float, nullable=False)
    provider = Column(String)                    # e.g. "Old Mutual"
    premium_period = Column(String)                      # monthly premium
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime, nullable=False)
    
    status = Column(String, default="active")  # e.g., active, expired, cancelled

    # created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Policy {self.matatu_registration}>"
