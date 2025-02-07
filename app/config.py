import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./policy_bazaar.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

SENTRY_DSN = os.getenv("SENTRY_DSN", "") 
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
