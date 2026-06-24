from uuid import UUID
from typing import Any

from fastapi import status

from app.orm.models import User
from app.utils.responder import success_response


class ProfileService:
    """User Profile Service."""

    async def get_profile(self, user_id: UUID) -> dict[str, Any]:
        """Retrieves the user's profile."""
        user = await User.get(id=user_id)

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Profile retrieved successfully.",
            data={"id": user.id, "email": user.email},
        )
