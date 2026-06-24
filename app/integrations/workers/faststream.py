from typing import Annotated

from faststream.redis import RedisStreamMessage as Rsm
from faststream.redis.fastapi import Context, RedisRouter

from app.env import settings

async_router = RedisRouter(settings.REDIS_URL)

RedisStreamMessage = Annotated[Rsm, Context("message")]


__all__ = ["RedisStreamMessage", "async_router"]
