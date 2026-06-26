from typing import Annotated

from pydantic import Field, BaseModel

from ._commons import String, EmailString, IsStrongPassword, IsNigerianPhoneNumber


class RegisterRequestSchema(BaseModel):
    """Register Request Schema."""

    email: EmailString
    password: IsStrongPassword
    full_name: Annotated[String, Field(min_length=3, max_length=100)]
    phone: IsNigerianPhoneNumber


class VerifyEmailRequestSchema(BaseModel):
    """Verify Email Request Schema."""

    email: EmailString
    code: String


class ResendVerificationRequestSchema(BaseModel):
    """Resend Verification Request Schema."""

    email: EmailString


class LoginRequestSchema(BaseModel):
    """Login Request Schema."""

    email: EmailString
    password: String


class GoogleLoginRequestSchema(BaseModel):
    """Google Login Request Schema."""

    token: String


class ResetPasswordRequestSchema(BaseModel):
    """Reset Password Request Schema."""

    email: EmailString


class ResetPasswordCheckRequestSchema(BaseModel):
    """Reset Password Check Request Schema."""

    user_id: String
    token: String


class ResetPasswordConfirmRequestSchema(BaseModel):
    """Reset Password Confirm Request Schema."""

    user_id: String
    token: String
    new_password: IsStrongPassword
