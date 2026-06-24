from uuid import UUID
from typing import Any

from fastapi import Response

from app.constants import USER_ACCESS_COOKIE, USER_REFRESH_COOKIE
from app.orm.models import User
from app.utils.responder import error_response, success_response
from app.services.utility import UtilityService


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

    async def email_signup(
        self, email: str, password: str, response: Response
    ) -> dict[str, Any]:
        """Registers a user with email and password."""
        exists = await User.exists(email=email)
        if exists:
            return error_response(400, "Email already exists.")

        hashed_password = UtilityService.hash_password(password)

        user = await User.create(email=email, password=hashed_password)

        await self._set_cookies(response, user)

        return success_response(201, "User registered successfully.")

    async def email_signin(
        self, email: str, password: str, response: Response
    ) -> dict[str, Any]:
        """Signs in a user with email and password."""
        user = await User.get_or_none(email=email)
        if not user:
            return error_response(400, "Invalid email or password.")

        if not UtilityService.verify_password(password, user.password):
            return error_response(400, "Invalid email or password.")

        await user.save()  # Update last active timestamp

        await self._set_cookies(response, user)

        return success_response(200, "User signed in successfully.")

    async def signout(
        self, response: Response, access_token: str | None, refresh_token: str | None
    ) -> dict[str, Any]:
        """Signs out the user by clearing the cookies."""
        response.delete_cookie(USER_ACCESS_COOKIE)
        response.delete_cookie(USER_REFRESH_COOKIE)

        await UtilityService.invalidate_tokens(access_token, refresh_token)

        return success_response(200, "User signed out successfully.")

    async def validate_access_token(self, token: str) -> UUID | None:
        """Validates the access token and returns the user ID if valid."""
        return await UtilityService.validate_access(token)

    async def refresh_tokens(
        self, refresh_token: str | None, response: Response
    ) -> dict[str, Any]:
        """Refreshes the access and refresh tokens."""
        if not refresh_token:
            return error_response(400, "Refresh token is required.")

        user_id = await UtilityService.validate_refresh(refresh_token)
        if not user_id:
            return error_response(400, "Invalid refresh token.")

        user = await User.get_or_none(id=user_id)
        if not user:
            return error_response(400, "User not found.")

        await self._set_cookies(response, user, refresh_token)

        return success_response(200, "Tokens refreshed successfully.")
