from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class ClaimStatus(enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    incident_date = Column(DateTime, nullable=False)
    submission_date = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED, nullable=False)
    description = Column(Text, nullable=True)
    amount_claimed = Column(Float, nullable=False)
    amount_settled = Column(Float, nullable=True)
    evidence_url = Column(String, nullable=True)
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Claim id={self.id} policy_id={self.policy_id} status={self.status.value}>"
