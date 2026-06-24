from typing import Any, Annotated

from fastapi import Depends, APIRouter, status

from app.services.users import ProfileService
from app.api.security.cookie_auth import ValidUser
from app.schemas.responses.generic import (
    ErrorResponseSchema,
    SuccessResponseSchema,
    ValidationErrorResponseSchema,
)
from app.schemas.responses.profile import ProfileResponseSchema

router = APIRouter(prefix="/user/me", tags=["User Profile"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseSchema[ProfileResponseSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ValidationErrorResponseSchema},
    },
)
async def get_profile(
    user_id: ValidUser,
    service: Annotated[ProfileService, Depends()],
) -> dict[str, Any]:
    """Retrieves the user's profile."""
    return await service.get_profile(user_id)
