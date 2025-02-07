import time
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import aioredis

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.redis = redis_client
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        identifier = request.client.host  # or use an API key from headers

        try:
            # Use a Redis transaction to ensure atomicity
            async with self.redis.pipeline(transaction=True) as pipe:
                await pipe.incr(identifier)
                await pipe.expire(identifier, self.window)
                result = await pipe.execute()

            current_count = result[0]  # Result of INCR

            if current_count > self.limit:
                raise HTTPException(status_code=429, detail="Too Many Requests")

        except aioredis.RedisError as e:
            # Log the error and allow the request to proceed if Redis fails
            print(f"Redis error: {e}")
            # Optionally, you can raise an HTTPException here if Redis is critical

        return await call_next(request)
