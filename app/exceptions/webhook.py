from typing import Optional, Dict, Any
from app.exceptions.base import KnownError

class WebhookTriggerError(KnownError):
    def __init__(self, url: str, message: str = None):
        if not message:
            message = f"Failed to trigger webhook for URL '{url}'."
        super().__init__(
            message=message,
            status_code=500,
            error_code="WEBHOOK_TRIGGER_ERROR",
            details={"url": url}
        )

class WebhookSubscriptionError(KnownError):
    def __init__(self, subscription_id: Optional[int] = None, message: str = None):
        if not message:
            message = "Webhook subscription error."
        super().__init__(
            message=message,
            status_code=400,
            error_code="WEBHOOK_SUBSCRIPTION_ERROR",
            details={"subscription_id": subscription_id} if subscription_id else {}
        )
