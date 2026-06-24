from uuid import UUID
from datetime import datetime

from tortoise import fields, models


class User(models.Model):
    """User model."""

    id: UUID = fields.UUIDField(primary_key=True)
    email: str = fields.CharField(max_length=255, unique=True)
    password: str = fields.CharField(max_length=255)
    date_joined: datetime = fields.DatetimeField(auto_now_add=True)
    last_active: datetime = fields.DatetimeField(auto_now=True)
