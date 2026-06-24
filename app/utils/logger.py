import logging

import structlog

from app import __package_name__

_shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
]

structlog.configure(
    processors=(
        [
            *_shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
        if False
        else [*_shared_processors, structlog.dev.ConsoleRenderer()]
    ),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

structlog.wrap_logger(logging.getLogger("tortoise.db_client"))
structlog.wrap_logger(logging.getLogger("tortoise"))

logger = structlog.get_logger().bind(service=__package_name__)
