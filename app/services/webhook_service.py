import logging
import asyncio
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.webhook_subscription import WebhookSubscription

logger = logging.getLogger(__name__)

class WebhookService:
    """
    Service for managing webhook subscriptions and triggering events.
    Handles asynchronous calls so that slow subscribers don't block our Matatu engine.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(self, subscription_data) -> WebhookSubscription:
        """
        Create a new webhook subscription.
        """
        subscription = WebhookSubscription(**subscription_data.dict())
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def _send_webhook(self, url: str, payload: dict, event: str):
        """
        Internal helper to send a single webhook payload using an asynchronous HTTP client.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=5.0)
                logger.info(f"Triggered webhook for event '{event}' to {url}: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to trigger webhook for {url}: {e}")

    async def trigger_event(self, event: str, payload: dict):
        """
        Trigger a webhook event by sending the payload to all subscribers concurrently.
        This ensures our Matatu chaos is handled in the fast lane.
        """
        try:
            result = await self.db.execute(
                select(WebhookSubscription).where(WebhookSubscription.event == event)
            )
            subscriptions = result.scalars().all()
            if not subscriptions:
                logger.info(f"No subscriptions found for event '{event}'")
                return

            # Launch webhook calls concurrently.
            tasks = [self._send_webhook(sub.url, payload, event) for sub in subscriptions]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error triggering event '{event}': {e}")
