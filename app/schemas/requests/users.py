from pydantic import BaseModel

from ._commons import String, EmailString, IsStrongPassword


class RegisterRequestSchema(BaseModel):
    """Register Request Schema."""

    email: EmailString
    password: IsStrongPassword


class LoginRequestSchema(BaseModel):
    """Login Request Schema."""

    email: EmailString
    password: String
