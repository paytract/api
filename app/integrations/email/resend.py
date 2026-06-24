import resend

from app.env import settings

resend.api_key = settings.RESEND_API_KEY


def resend_email(
    to_email: str, subject: str, html_content: str, idempotency_key: str | None = None
) -> resend.Emails.SendResponse:
    """Sends an email using Resend service."""
    params: resend.Emails.SendParams = {
        "from": settings.RESEND_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    options: resend.Emails.SendOptions | None = (
        {"idempotency_key": idempotency_key} if idempotency_key else None
    )
    response = resend.Emails.send(params, options=options)
    return response
