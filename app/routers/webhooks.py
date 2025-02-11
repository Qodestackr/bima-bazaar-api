from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.webhook_subscription import WebhookSubscriptionCreate, WebhookSubscriptionOut
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/", response_model=WebhookSubscriptionOut)
async def subscribe_webhook(subscription: WebhookSubscriptionCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to create a new webhook subscription.
    
    Clients provide a URL and an event name. On success, the subscription is stored
    and can be used for future event notifications.
    """
    service = WebhookService(db)
    try:
        sub = await service.create_subscription(subscription)
        return sub
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/", response_model=PolicyOut)
# async def create_policy(policy: PolicyCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
#     new_policy = await service.create_policy(policy)
#     # Trigger webhook in background
#     background_tasks.add_task(
#         webhook_service.trigger_event,
#         "policy_created",
#         {"policy_id": new_policy.id, "status": new_policy.status}
#     )
#     return new_policy
