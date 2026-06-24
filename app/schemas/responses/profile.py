from uuid import UUID

from pydantic import BaseModel


class ProfileResponseSchema(BaseModel):
    """Profile Response Schema."""

    id: UUID
    email: str
