
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

import logging
import sentry_sdk

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.exceptions.base import KnownError
from app.routers import policies, claims, payments, damage_assessment, whatsapp_distribution, webhooks
from app.middleware.rate_limit import RateLimitMiddleware

# --- Logging Configuration ---
logger = logging.getLogger("policy_bazaar_api")
logging.basicConfig(level=LOG_LEVEL)

# --- Sentry Initialization ---
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,  # Adjust in prod
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.create_redis_pool("redis://localhost")
    yield
    redis.close()
    await redis.wait_closed()

app = FastAPI(title="Bima Bazaar API", version="1.0", lifespan=lifespan)

if SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)


app.add_middleware(RateLimitMiddleware, redis_client=app.state.redis, limit=100, window=60)

app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(payments.router)
app.include_router(damage_assessment.router)
app.include_router(whatsapp_distribution.router)
app.include_router(webhooks.router)

# --- Global Exception Handlers ---

@app.exception_handler(KnownError)
async def known_error_handler(request: Request, exc: KnownError):
    logger.info(f"KnownError handled: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log er details
    logger.exception("Unhandled Exception: ", exc_info=exc)
    # Sentry auto capture if SentryAsgiMiddleware is active.
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "internal_error",
            "message": "An internal error occurred. Our team has been notified.",
        },
    )

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}
