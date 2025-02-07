from pydantic import BaseModel

class WebhookSubscriptionCreate(BaseModel):
    """
    Schema for creating a new webhook subscription.
    
    Attributes:
        url: The subscriber's endpoint URL.
        event: The event to subscribe to.
    """
    url: str
    event: str

class WebhookSubscriptionOut(WebhookSubscriptionCreate):
    """
    Schema for returning webhook subscription data.
    
    Attributes:
        id: Unique subscription identifier.
        created_at: Timestamp when the subscription was created.
    """
    id: int
    created_at: str

    class Config:
        orm_mode = True
