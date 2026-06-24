from typing import Any

from jinja2 import Template

from app.env import BASE_DIR
from app.enums.email import EmailType
from app.workers.email import publish_email
from app.utils.retry_breaker import apply_breaker
from app.integrations.files.local import read_file
from app.integrations.email.resend import resend_email


class EmailService:
    """Service to handle emails."""

    @apply_breaker
    @staticmethod
    async def send_email_direct(
        email: str, type: EmailType, context: dict[str, Any]
    ) -> None:
        """Send an email immediately.

        Args:
            email (str): The recipient's email address.
            type (EmailType): The type of Email.
            context (dict[str, Any]): The context for the Email.

        Returns:
            None
        """
        subject = await read_file(BASE_DIR / f"templates/{type}/subject.txt")
        template = Template(
            await read_file(BASE_DIR / f"templates/{type}/body.html"), enable_async=True
        )
        body: str = await template.render_async(context)

        resend_email(to_email=email, subject=subject, html_content=body)

    @staticmethod
    async def send_email(email: str, type: EmailType, context: dict[str, Any]) -> None:
        """Enqueue email delivery."""
        await publish_email(email=email, type=type, context=context)
