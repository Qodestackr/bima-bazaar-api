import asyncio
import json
import aioredis
import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WebhookWorker:
    """
    Durable Object-like Webhook Processor that ensures reliable event handling.
    """
    def __init__(self, redis_url="redis://localhost", retry_backoff=5):
        self.redis_url = redis_url
        self.retry_backoff = retry_backoff  # seconds
        self.redis = None

    async def connect(self):
        """Initialize Redis connection."""
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def process_event(self):
        """Continuously checks for pending webhook jobs and processes them."""
        if not self.redis:
            await self.connect()

        while True:
            try:
                event = await self.redis.lpop("webhook_queue")
                if event:
                    event_data = json.loads(event)
                    await self._send_webhook(event_data)
                else:
                    await asyncio.sleep(1)  # Avoid CPU burnout if queue is empty
            except Exception as e:
                logger.error(f"WebhookWorker error: {e}")
                await asyncio.sleep(self.retry_backoff)

    async def _send_webhook(self, event_data):
        """Handles the actual webhook sending."""
        url = event_data["url"]
        payload = event_data["payload"]
        event = event_data["event"]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code >= 400:
                    # Store for retry if it fails
                    await self._retry_event(event_data)
                else:
                    logger.info(f"Webhook sent: {event} → {url}")
            except Exception as e:
                logger.error(f"Failed webhook {url}: {e}")
                await self._retry_event(event_data)

    async def _retry_event(self, event_data):
        """Schedules a retry if a webhook fails."""
        retry_time = datetime.utcnow() + timedelta(seconds=self.retry_backoff)
        event_data["retry_at"] = retry_time.isoformat()
        await self.redis.rpush("webhook_queue", json.dumps(event_data))
        logger.info(f"Retrying webhook later: {event_data['url']}")

# Start processing when script runs
if __name__ == "__main__":
    worker = WebhookWorker()
    asyncio.run(worker.process_event())
