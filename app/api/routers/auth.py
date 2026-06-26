from typing import Any, Annotated

from fastapi import Depends, Response, APIRouter, status
from fastapi.security import APIKeyCookie

from app.constants import USER_ACCESS_COOKIE, USER_REFRESH_COOKIE
from app.services.auth import AuthenticationService
from app.schemas.requests.users import (
    LoginRequestSchema,
    RegisterRequestSchema,
    GoogleLoginRequestSchema,
    VerifyEmailRequestSchema,
    ResetPasswordRequestSchema,
    ResendVerificationRequestSchema,
    ResetPasswordCheckRequestSchema,
    ResetPasswordConfirmRequestSchema,
)
from app.schemas.responses.users import ProfileResponseSchema
from app.schemas.responses.generic import (
    ErrorResponseSchema,
    SuccessResponseSchema,
    ValidationErrorResponseSchema,
)

router = APIRouter(prefix="/user/auth", tags=["User Authentication"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[ProfileResponseSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def email_signup(
    details: RegisterRequestSchema, service: Annotated[AuthenticationService, Depends()]
) -> dict[str, Any]:
    """Registers a user with email and password."""
    return await service.email_signup(
        details.email, details.password, details.full_name, details.phone
    )


@router.post(
    "/signup/verify",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def verify_email(
    details: VerifyEmailRequestSchema,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Verifies a user's email using the provided code."""
    return await service.verify_email(details.email, details.code)


@router.post(
    "/signup/resend-verification",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def resend_verification(
    details: ResendVerificationRequestSchema,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Resends the verification code to the user's email."""
    return await service.resend_verification_code(details.email)


@router.post(
    "/signin",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[ProfileResponseSchema],
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
    "/oauth/google",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[ProfileResponseSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def google_signin(
    details: GoogleLoginRequestSchema,
    response: Response,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Signs in a user with Google OAuth."""
    return await service.google_oauth_signin(details.token, response)


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


@router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def password_reset(
    details: ResetPasswordRequestSchema,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Initiates a password reset process for the user."""
    return await service.password_reset(details.email)


@router.post(
    "/password/reset/check",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def password_reset_check(
    details: ResetPasswordCheckRequestSchema,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Checks the validity of a password reset token."""
    return await service.check_valid_reset_token(details.user_id, details.token)


@router.post(
    "/password/reset/confirm",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[None],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def password_reset_confirm(
    details: ResetPasswordConfirmRequestSchema,
    service: Annotated[AuthenticationService, Depends()],
) -> dict[str, Any]:
    """Completes the password reset process for the user."""
    return await service.complete_password_reset(
        details.user_id, details.token, details.new_password
    )
