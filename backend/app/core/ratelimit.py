"""Redis sliding-window rate limiter used as a FastAPI dependency."""
import time
from fastapi import HTTPException, Request
import redis.asyncio as aioredis
from app.core.config import settings

_redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(limit: int = 60, window: int = 60):
    async def dep(request: Request):
        ident = request.headers.get("authorization", request.client.host)
        key = f"rl:{hash(ident)}:{request.url.path}"
        now = time.time()
        async with _redis.pipeline() as pipe:
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            _, _, count, _ = await pipe.execute()
        if count > limit:
            raise HTTPException(429, "Rate limit exceeded")
    return dep
