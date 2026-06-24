# pyright: reportUnknownMemberType=none
import string
import secrets
from uuid import UUID
from hashlib import sha256
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from slugify import slugify
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.env import settings
from app.integrations.cache import cache_factory

ph = PasswordHasher()


class UtilityService:
    """Utility Service."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password."""
        return ph.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a hashed password."""
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError, VerificationError, InvalidHashError:
            return False

    @staticmethod
    def get_random_string(
        length: int = 12, numeric_only: bool = False, add_special: bool = False
    ) -> str:
        """Generates a unique string."""
        characters = string.digits if numeric_only else string.ascii_letters
        if add_special:
            characters += "-._~" + string.digits

        return "".join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def hash_string(value: str) -> str:
        """Hashes a string value."""
        return sha256(value.encode()).hexdigest()

    @staticmethod
    def get_current_year() -> int:
        """Returns the current year."""
        return datetime.now(UTC).year

    @staticmethod
    def slugify(name: str) -> str:
        """Slugify."""
        return slugify(name)

    @staticmethod
    def _encode_jwt(
        payload: dict[str, str | int], claims: dict[str, str | int | datetime]
    ) -> str:
        """Encodes the payload to JWT string."""
        token = jwt.encode(
            dict(**payload, **claims),
            key=settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token

    @staticmethod
    def _decode_jwt(jwt_string: str, claims: list[str] = []) -> dict[str, str | int]:
        """Decodes JWT string to payload."""
        data = jwt.decode_complete(
            jwt_string,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": claims},
        )
        return data["payload"]

    @staticmethod
    async def create_tokens(
        subject: str,
        refresh_token: str = "",
    ) -> tuple[str, str]:
        """Creates access and refresh tokens."""
        now = datetime.now(UTC)
        access = UtilityService._encode_jwt(
            {"sub": subject, "type": "access"},
            {"exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY)},
        )

        if refresh_token:
            cache = cache_factory()
            exp: int | None = UtilityService._decode_jwt(refresh_token, ["exp"]).get(
                "exp"
            )  # type: ignore
            await cache.set(f"refresh_token:{refresh_token}", 1, exat=exp)

        refresh = UtilityService._encode_jwt(
            {"sub": subject, "type": "refresh"},
            {"exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRY)},
        )

        return access, refresh

    @staticmethod
    async def validate_access(token: str) -> UUID | None:
        """Validates a JWT access token."""
        try:
            payload = UtilityService._decode_jwt(token)
            if not payload or payload.get("type") != "access":
                raise ValueError

            cache = cache_factory()
            if await cache.get(f"access_token:{token}"):
                raise ValueError

            return UUID(str(payload["sub"]))

        except ValueError, KeyError, jwt.exceptions.InvalidTokenError:
            return None

    @staticmethod
    async def validate_refresh(token: str) -> UUID | None:
        """Validates a JWT refresh token."""
        try:
            payload = UtilityService._decode_jwt(token)
            if not payload or payload.get("type") != "refresh":
                raise ValueError

            cache = cache_factory()
            if await cache.get(f"refresh_token:{token}"):
                raise ValueError

            return UUID(str(payload["sub"]))

        except ValueError, KeyError, jwt.exceptions.InvalidTokenError:
            return None

    @staticmethod
    async def invalidate_tokens(
        access_token: str | None, refresh_token: str | None
    ) -> None:
        """Invalidates access and refresh tokens."""
        cache = cache_factory()
        exp_access: int | None = None
        exp_refresh: int | None = None
        try:
            exp_access = (
                UtilityService._decode_jwt(access_token, ["exp"]).get("exp")
                if access_token
                else None
            )  # type: ignore
        except Exception:
            ...
        try:
            exp_refresh = (
                UtilityService._decode_jwt(refresh_token, ["exp"]).get("exp")
                if refresh_token
                else None
            )  # type: ignore
        except Exception:
            ...

        if exp_access:
            await cache.set(f"access_token:{access_token}", 1, exat=exp_access)

        if exp_refresh:
            await cache.set(f"refresh_token:{refresh_token}", 1, exat=exp_refresh)
