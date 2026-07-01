from uuid import UUID
from typing import Any

from fastapi import Response, status

from app.env import settings
from app.constants import USER_ACCESS_COOKIE, USER_REFRESH_COOKIE
from app.orm.models import User
from app.enums.email import EmailType
from app.services.email import EmailService
from app.utils.responder import error_response, success_response
from app.services.utility import UtilityService
from app.integrations.cache import cache_factory
from app.integrations.google.auth import verify_token


class AuthenticationService:
    """User Authentication Service."""

    async def _set_cookies(
        self, response: Response, user: User, refresh_token: str = ""
    ) -> None:

        access, refresh = await UtilityService.create_tokens(
            str(user.id), refresh_token
        )

        response.set_cookie(
            key=USER_ACCESS_COOKIE,
            value=access,
            httponly=True,
            secure=True,
            samesite="none",
        )

        response.set_cookie(
            key=USER_REFRESH_COOKIE,
            value=refresh,
            httponly=True,
            secure=True,
            samesite="none",
        )

    async def _send_verification_email(self, email: str, first_name: str) -> None:
        """Send a verification email to the user."""
        cache = cache_factory()

        verification_code = UtilityService.get_random_string(
            length=6, numeric_only=True
        )

        await cache.set(f"user_verification:{email}", verification_code, 600)

        await EmailService.send_email(
            email=email,
            type=EmailType.VERIFICATION,
            context={
                "user_first_name": first_name,
                "user_email": email,
                "otp_code": verification_code,
                "verification_url": f"{settings.FRONTEND_URL}/verify?code={verification_code}",
                "expiry_duration": "10 minutes",
                "current_year": UtilityService.get_current_year(),
            },
        )

    async def email_signup(
        self, email: str, password: str, full_name: str, phone: str
    ) -> dict[str, Any]:
        """Registers a user with email and password."""
        exists = await User.exists(email=email)
        if exists:
            error_response(400, "Email already exists.")

        names = full_name.split(" ", 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else None

        hashed_password = UtilityService.hash_password(password)

        user = await User.create(
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        await self._send_verification_email(email, first_name)

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="User registered successfully.",
            data={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
            },
        )

    async def verify_email(self, email: str, code: str) -> dict[str, Any]:
        """Verify a user's email."""
        cache = cache_factory()
        cached_code = await cache.get(f"user_verification:{email}")
        if not cached_code or cached_code != code:
            error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid or expired verification code",
            )

        user = await User.get_or_none(email=email)
        if not user:
            error_response(
                status_code=status.HTTP_404_NOT_FOUND, message="User not found"
            )

        if user.email_verified:
            return success_response(
                status_code=status.HTTP_200_OK, message="User already verified"
            )

        user.email_verified = True
        await user.save()

        await EmailService.send_email(
            email=user.email,
            type=EmailType.WELCOME,
            context={
                "dashboard_url": f"{settings.FRONTEND_URL}/dashboard",
                "user_first_name": user.first_name or "User",
                "user_full_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "user_email": user.email,
                "account_id": str(user.id),
                "join_date": user.date_joined.strftime("%B %d, %Y"),
                "current_year": UtilityService.get_current_year(),
            },
        )

        await cache.delete(f"user_verification:{email}")

        return success_response(
            status_code=status.HTTP_200_OK, message="User verified successfully"
        )

    async def resend_verification_code(self, email: str) -> dict[str, Any]:
        """Resend verification code to user."""
        user = await User.get_or_none(email=email)

        if user is None:
            return error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found",
            )

        elif user.email_verified:
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                message="User is already verified",
            )

        await self._send_verification_email(email, user.first_name or "User")

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Verification code resent successfully",
        )

    async def email_signin(
        self, email: str, password: str, response: Response
    ) -> dict[str, Any]:
        """Signs in a user with email and password."""
        user = await User.get_or_none(email=email)
        if not user:
            error_response(400, "Invalid email or password.")

        if not UtilityService.verify_password(password, user.password):
            error_response(400, "Invalid email or password.")

        await user.save()  # Update last active timestamp

        await self._set_cookies(response, user)

        return success_response(
            status_code=status.HTTP_200_OK,
            message="User signed in successfully.",
            data={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
            },
        )

    async def google_oauth_signin(
        self, id_token: str, response: Response
    ) -> dict[str, Any]:
        """Signs in a user using Google OAuth."""
        user_info = verify_token(id_token)
        if not user_info:
            error_response(400, "Invalid Google token.")

        email = user_info["email"]
        first_name = user_info["given_name"]
        last_name = user_info["family_name"]
        hashed_random_password = UtilityService.hash_password(
            UtilityService.get_random_string(12)
        )

        user = await User.get_or_none(email=email)
        if not user:
            # Create a new user if not exists
            user = await User.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=hashed_random_password,
                email_verified=True,
            )
        elif not user.email_verified:
            user.email_verified = True
            await user.save()

        await self._set_cookies(response, user)

        return success_response(
            status_code=status.HTTP_200_OK,
            message="User signed in successfully via Google.",
            data={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
            },
        )

    async def signout(
        self, response: Response, access_token: str | None, refresh_token: str | None
    ) -> dict[str, Any]:
        """Signs out the user by clearing the cookies."""
        response.delete_cookie(USER_ACCESS_COOKIE)
        response.delete_cookie(USER_REFRESH_COOKIE)

        await UtilityService.invalidate_tokens(access_token, refresh_token)

        return success_response(
            status_code=status.HTTP_200_OK, message="User signed out successfully."
        )

    async def validate_access_token(self, token: str) -> UUID | None:
        """Validates the access token and returns the user ID if valid."""
        return await UtilityService.validate_access(token)

    async def refresh_tokens(
        self, refresh_token: str | None, response: Response
    ) -> dict[str, Any]:
        """Refreshes the access and refresh tokens."""
        if not refresh_token:
            error_response(status.HTTP_400_BAD_REQUEST, "Refresh token is required.")

        user_id = await UtilityService.validate_refresh(refresh_token)
        if not user_id:
            error_response(status.HTTP_400_BAD_REQUEST, "Invalid refresh token.")

        user = await User.get_or_none(id=user_id)
        if not user:
            error_response(status.HTTP_400_BAD_REQUEST, "User not found.")

        await self._set_cookies(response, user, refresh_token)

        return success_response(
            status_code=status.HTTP_200_OK, message="Tokens refreshed successfully."
        )

    async def password_reset(self, email: str) -> dict[str, Any]:
        """Initiate password reset."""
        user = await User.get_or_none(email=email)
        if not user:
            error_response(
                status_code=status.HTTP_200_OK,
                message="Reset link sent to your email if it exists in our system.",
            )

        cache = cache_factory()
        token = UtilityService.get_random_string(64, add_special=True)

        await cache.set(f"user_password_reset:{user.id}", token, 3600)

        await EmailService.send_email(
            email=user.email,
            type=EmailType.CREDENTIALS_RESET,
            context={
                "user_first_name": user.first_name or "User",
                "user_email": user.email,
                "reset_url": f"{settings.FRONTEND_URL}/reset-password?id={user.id}&token={token}",
                "expiry_duration": "60 minutes",
                "current_year": UtilityService.get_current_year(),
            },
        )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Reset link sent to your email if it exists in our system.",
        )

    async def check_valid_reset_token(self, user_id: str, token: str) -> dict[str, Any]:
        """Check valid reset token."""
        cache = cache_factory()
        cache_token = await cache.get(f"user_password_reset:{user_id}")

        if not cache_token or cache_token != token:
            error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid or expired reset link",
            )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Reset link is valid",
        )

    async def complete_password_reset(
        self, user_id: str, token: str, new_password: str
    ) -> dict[str, Any]:
        """Complete password reset."""
        cache = cache_factory()
        cache_token = await cache.get(f"user_password_reset:{user_id}")

        if not cache_token or cache_token != token:
            error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid or expired reset link",
            )

        user = await User.get(id=user_id)
        password = UtilityService.hash_password(new_password)

        user.password = password
        await user.save()

        await cache.delete(f"user_password_reset:{user_id}")

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Password has been reset successfully",
        )
