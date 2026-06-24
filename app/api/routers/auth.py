from typing import Any, Annotated

from fastapi import Depends, Response, APIRouter, status
from fastapi.security import APIKeyCookie

from app.constants import USER_ACCESS_COOKIE, USER_REFRESH_COOKIE
from app.services.auth import AuthenticationService
from app.schemas.requests.users import LoginRequestSchema, RegisterRequestSchema
from app.schemas.responses.generic import (
    ErrorResponseSchema,
    SuccessResponseSchema,
    ValidationErrorResponseSchema,
)

router = APIRouter(prefix="/user/auth", tags=["User Authentication"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def email_signup(
    details: RegisterRequestSchema,
    response: Response,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Registers a user with email and password."""
    return await service.email_signup(details.email, details.password, response)


@router.post(
    "/signin",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def email_signin(
    details: LoginRequestSchema,
    response: Response,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Signs in a user with email and password."""
    return await service.email_signin(details.email, details.password, response)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
    },
)
async def refresh(
    response: Response,
    refresh_token: Annotated[
        str | None, Depends(APIKeyCookie(name=USER_REFRESH_COOKIE, auto_error=False))
    ],
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Refreshes the access token using the refresh token."""
    return await service.refresh_tokens(refresh_token, response)


@router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
)
async def signout(
    response: Response,
    access_token: Annotated[
        str | None, Depends(APIKeyCookie(name=USER_ACCESS_COOKIE, auto_error=False))
    ],
    refresh_token: Annotated[
        str | None, Depends(APIKeyCookie(name=USER_REFRESH_COOKIE, auto_error=False))
    ],
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Signs out the user by clearing the auth cookies."""
    return await service.signout(response, access_token, refresh_token)
