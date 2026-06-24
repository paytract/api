from uuid import UUID
from typing import Annotated

from fastapi import Depends, status
from fastapi.security import APIKeyCookie

from app.constants import USER_ACCESS_COOKIE
from app.services.auth import AuthenticationService
from app.utils.exceptions import ErrorResponse


async def get_user(
    access_token: Annotated[
        str | None, Depends(APIKeyCookie(name=USER_ACCESS_COOKIE, auto_error=False))
    ],
    service: Annotated[AuthenticationService, Depends()],
) -> UUID:
    """Validate cookie credentials."""
    if not access_token:
        raise ErrorResponse(status.HTTP_401_UNAUTHORIZED, "Unauthorized access")

    user_id = await service.validate_access_token(access_token)
    if not user_id:
        raise ErrorResponse(status.HTTP_401_UNAUTHORIZED, "Unauthorized access")

    return user_id


DependValidUser = Depends(get_user)
ValidUser = Annotated[UUID, DependValidUser]
