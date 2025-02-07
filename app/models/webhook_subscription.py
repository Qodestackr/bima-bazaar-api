from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WebhookSubscription(Base):
    """
    Database model for storing webhook subscriptions.
    
    Attributes:
        id: Unique identifier.
        url: The endpoint to which events will be sent.
        event: The event name to subscribe to (e.g., "policy_created").
        created_at: Timestamp when the subscription was created.
    """
    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
