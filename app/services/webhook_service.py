import requests
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.webhook_subscription import WebhookSubscription

logger = logging.getLogger(__name__)

class WebhookService:
    """
    Service for managing webhook subscriptions and triggering events.
    
    Methods:
        create_subscription: Save a new subscription to the database.
        trigger_event: Find all subscriptions for a given event and POST the payload.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(self, subscription_data) -> WebhookSubscription:
        """
        Create a new webhook subscription.
        
        Args:
            subscription_data: Instance of WebhookSubscriptionCreate.
        
        Returns:
            The created WebhookSubscription object.
        """
        subscription = WebhookSubscription(**subscription_data.dict())
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def trigger_event(self, event: str, payload: dict):
        """
        Trigger a webhook event by sending the payload to all subscribers.
        
        Args:
            event: The event name (e.g., "policy_created").
            payload: The data to send in the webhook notification.
        
        Logs success or error for each subscriber.
        """
        result = await self.db.execute(select(WebhookSubscription).where(WebhookSubscription.event == event))
        subscriptions = result.scalars().all()
        for sub in subscriptions:
            try:
                response = requests.post(sub.url, json=payload, timeout=5)
                logger.info(f"Triggered webhook for event '{event}' to {sub.url}: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to trigger webhook for {sub.url}: {e}")
