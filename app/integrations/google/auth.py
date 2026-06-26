from google.oauth2 import id_token
from google.auth.transport import requests

from app.env import settings

from .typing import GoogleIDInfo


def verify_token(token: str) -> GoogleIDInfo | None:
    """Verify Google OAuth token."""
    try:
        idinfo: GoogleIDInfo = id_token.verify_oauth2_token(  # type: ignore
            token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        return idinfo
    except ValueError:
        return None
