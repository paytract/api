from uuid import UUID
from decimal import Decimal
from datetime import datetime

from tortoise import fields, models

from app.enums.offerings import OfferingFrequency

from .users import User


class Client(models.Model):
    """Client model."""

    id: UUID = fields.UUIDField(primary_key=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "main.User", related_name="clients", on_delete=fields.CASCADE
    )
    name: str | None = fields.CharField(max_length=255, null=True)
    email: str | None = fields.CharField(max_length=255, null=True)
    metadata: str | None = fields.TextField(null=True)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta(models.Model.Meta):
        """Client model metadata."""

        table = "clients"


class Gig(models.Model):
    """Gig model."""

    id: UUID = fields.UUIDField(primary_key=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "main.User", related_name="gigs", on_delete=fields.CASCADE
    )
    name: str = fields.CharField(max_length=255)
    description: str = fields.TextField(null=True)
    client: fields.ForeignKeyNullableRelation[Client] = fields.ForeignKeyField(
        "main.Client", related_name="gigs", on_delete=fields.CASCADE, null=True
    )
    price: Decimal = fields.DecimalField(max_digits=10, decimal_places=2)
    frequency: OfferingFrequency = fields.CharEnumField(
        OfferingFrequency, max_length=50
    )
    account_name: str = fields.CharField(max_length=255, null=True)
    account_number: str = fields.CharField(max_length=20, null=True)
    account_bank: str = fields.CharField(max_length=255, null=True)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    ends_at: datetime = fields.DatetimeField()

    class Meta(models.Model.Meta):
        """Gig model metadata."""

        table = "gigs"


class Contract(models.Model):
    """Contract model."""

    id: UUID = fields.UUIDField(primary_key=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "main.User", related_name="contracts", on_delete=fields.CASCADE
    )
    name: str = fields.CharField(max_length=255)
    description: str = fields.TextField(null=True)
    client: fields.ForeignKeyNullableRelation[Client] = fields.ForeignKeyField(
        "main.Client", related_name="contracts", on_delete=fields.CASCADE, null=True
    )
    price: Decimal = fields.DecimalField(max_digits=10, decimal_places=2)
    frequency: OfferingFrequency = fields.CharEnumField(
        OfferingFrequency, max_length=50
    )

    mandate_id: str = fields.CharField(max_length=255, null=True)
    is_valid: bool = fields.BooleanField(default=False)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    ends_at: datetime = fields.DatetimeField()
    signed_at: datetime = fields.DatetimeField(null=True)

    class Meta(models.Model.Meta):
        """Contract model metadata."""

        table = "contracts"
