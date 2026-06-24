from .faststream import RedisStreamMessage as Message
from .faststream import async_router

__all__ = ["Message", "async_router"]
