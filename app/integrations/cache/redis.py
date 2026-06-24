import redis.asyncio

from app.env import settings

redis_pool = redis.asyncio.ConnectionPool.from_url(  # type: ignore
    settings.REDIS_URL, decode_responses=True
)


def redis_factory() -> redis.asyncio.Redis:
    """Get an async Redis client from the connection pool."""
    return redis.asyncio.Redis.from_pool(redis_pool)
