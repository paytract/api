from contextlib import AsyncExitStack, asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__, __display_name__
from app.api import routers
from app.orm.config import RegisterORM
from app.utils.logger import logger
from app.integrations.workers import async_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncExitStack() as stack:
        logger.info("Application startup initiated")

        await stack.enter_async_context(RegisterORM(app))
        logger.info("Application startup completed")

        yield

        logger.info("Application shutdown completed")


application = FastAPI(title=__display_name__, version=__version__, lifespan=_lifespan)


# Add CORS middleware
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(routers.routes)
application.include_router(async_router)


from app.error_handlers import *  # noqa: E402, F403
