from sqlalchemy.ext.asyncio import AsyncSession
import json
import aioredis

class WebhookService:
    def __init__(self, db: AsyncSession, redis_url="redis://localhost"):
        self.db = db
        self.redis_url = redis_url
        self.redis = None

    async def connect_redis(self):
        """Connect to Redis once for efficiency."""
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def trigger_event(self, event: str, payload: dict):
        """Enqueue webhook jobs instead of calling them immediately."""
        await self.connect_redis()
        result = await self.db.execute(
            select(WebhookSubscription).where(WebhookSubscription.event == event)
        )
        subscriptions = result.scalars().all()

        if not subscriptions:
            logger.info(f"No subscriptions found for event '{event}'")
            return

        # Queue each webhook call
        for sub in subscriptions:
            job_data = {"url": sub.url, "payload": payload, "event": event}
            await self.redis.rpush("webhook_queue", json.dumps(job_data))

        logger.info(f"Queued {len(subscriptions)} webhook events for '{event}'")


# Use Durable Objects → When you need per-entity coordination, real-time updates, 
# or long-lived state that Redis alone won’t handle efficiently.