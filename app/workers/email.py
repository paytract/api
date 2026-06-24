from typing import Any

from pydantic import BaseModel

from app import __package_name__
from app.enums.email import EmailType
from app.integrations.workers import async_router


class _EmailData(BaseModel):
    email: str
    type: EmailType
    context: dict[str, Any]


async def publish_email(email: str, type: EmailType, context: dict[str, Any]) -> None:
    """Helper function to publish email sending tasks to the worker broker."""
    await async_router.publisher(stream=f"{__package_name__}:email-service").publish(
        _EmailData(email=email, type=type, context=context)
    )


@async_router.subscriber(stream=f"{__package_name__}:email-service")
async def email_service_worker(message: _EmailData) -> None:
    """Worker handler to process email sending tasks."""
    from app.services.email import EmailService

    await EmailService.send_email_direct(
        email=message.email, type=message.type, context=message.context
    )
