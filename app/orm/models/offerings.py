from uuid import UUID
from decimal import Decimal
from datetime import datetime

from tortoise import fields, models

from app.enums.offerings import DurationStatus, OfferingFrequency

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

    automatic_collection: bool = fields.BooleanField(default=False)

    account_name: str = fields.CharField(max_length=255, null=True)
    account_number: str = fields.CharField(max_length=20, null=True)
    account_bank: str = fields.CharField(max_length=255, null=True)

    card_token: str = fields.CharField(max_length=255, null=True)
    valid_card: bool = fields.BooleanField(default=False)
    signed_at: datetime = fields.DatetimeField(null=True)
    resigned: bool = fields.BooleanField(default=False)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    ends_at: datetime = fields.DatetimeField()

    # Annotations
    total_durations: int
    pending_durations: int
    last_paid_collection_date: datetime | None
    next_due_collection_date: datetime | None

    class Meta(models.Model.Meta):
        """Gig model metadata."""

        table = "gigs"


class Duration(models.Model):
    """Duration model."""

    id: int = fields.BigIntField(primary_key=True)
    gig: fields.ForeignKeyRelation[Gig] = fields.ForeignKeyField(
        "main.Gig", related_name="durations", on_delete=fields.CASCADE
    )

    frequency: OfferingFrequency = fields.CharEnumField(
        OfferingFrequency, max_length=50
    )
    status: DurationStatus = fields.CharEnumField(
        DurationStatus, max_length=50, default=DurationStatus.PENDING
    )
    amount_paid: Decimal = fields.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    start_at: datetime = fields.DatetimeField()
    end_at: datetime = fields.DatetimeField()

    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    class Meta(models.Model.Meta):
        """Duration model metadata."""

        table = "durations"
