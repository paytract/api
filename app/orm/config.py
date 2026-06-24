from typing import Any
from functools import partial

from tortoise.contrib.fastapi import RegisterTortoise

from app.env import settings

TORTOISE_CONFIG: dict[str, Any] = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_NAME,
            },
        }
    },
    "apps": {
        "main": {
            "models": ["app.orm.models"],
            "default_connection": "default",
            "migrations": "app.orm.migrations",
        },
    },
}


RegisterORM = partial(
    RegisterTortoise,
    config=TORTOISE_CONFIG,
)
