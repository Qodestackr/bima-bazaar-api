
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.app_logging import configure_logging
import logging
import sentry_sdk

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.exceptions.base import KnownError
from app.routers import policies, claims, payments, damage_assessment, whatsapp_distribution, webhooks
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging_middleware import logging_middleware
from app.config import LOG_LEVEL, SENTRY_DSN
import aioredis

# --- Logging Configuration ---
logger = logging.getLogger("policy_bazaar_api")
logging.basicConfig(level=LOG_LEVEL)

# --- Sentry Initialization ---
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,  # Adjust in prod
        # environment="dev",
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.redis = await aioredis.from_url("redis://localhost:6379")
        logger.info("✅ Application startup: Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        app.state.redis = None
        
    yield
    
    if app.state.redis:
        await app.state.redis.close()
        logger.info("Application shutdown: Redis disconnected")


app = FastAPI(
    title="Bima Bazaar API",
    version="1.0",
    lifespan=lifespan,
    docs_url="/docs",  
    redoc_url=None,    
)
configure_logging()

if SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)


# --- Global Exception Handlers ---
@app.exception_handler(KnownError)
async def known_error_handler(request: Request, exc: KnownError):
    logger.info(f"KnownError handled: {exc.message}", extra={
        "error_code": exc.error_code,
        "status_code": exc.status_code
    })
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )
    
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled Exception", exc_info=exc, extra={
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "internal_error",
            "message": "An internal error occurred. Our team has been notified.",
        },
    )


app.add_middleware(RateLimitMiddleware, redis_client=app.state.redis, limit=100, window=60)
app.middleware("http")(logging_middleware)
app.include_router(webhooks.router)          
app.include_router(whatsapp_distribution.router)
app.include_router(damage_assessment.router)
app.include_router(claims.router)
app.include_router(payments.router)
app.include_router(policies.router)  


# --- Health Checks ---
@app.get("/")
async def read_root():
    return {"message": "Bima Bazaar API"}

@app.get("/status")
async def get_status():
    return {"status": "UP", "version": app.version}

# --- Post-Startup Validation ---
@app.on_event("startup")
async def startup_validation():
    if not app.state.redis:
        logger.error("Redis connection failed on startup!")
        raise RuntimeError("Redis connection failed")
    logger.info("API startup complete")