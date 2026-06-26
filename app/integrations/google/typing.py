from typing import TypedDict


class GoogleIDInfo(TypedDict):
    """Google ID Info TypedDict."""

    iss: str
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str
    given_name: str
    family_name: str
