import asyncio
import secrets
from uuid import UUID
from typing import Any
from decimal import Decimal
from datetime import UTC, datetime

from fastapi import status
from tortoise.functions import Max, Sum, Count, Coalesce
from tortoise.expressions import Q

from app.orm.models import Gig, Client, Ledger
from app.enums.finance import AccountTypes
from app.enums.offerings import DurationStatus, OfferingStatus, OfferingFrequency
from app.utils.responder import error_response, success_response
from app.typing.offerings import ClientInfo
from app.typing.pagination import PaginationParams


class OfferingService:
    """Offering Service."""

    async def total_balance(self, user_id: UUID) -> dict[str, Any]:
        """Get total balance for a user."""
        gig_ids = await Gig.filter(user_id=user_id).values_list("id", flat=True)

        gig_monies = (
            await Ledger.filter(account_id__in=gig_ids, account_type=AccountTypes.GIG)
            .annotate(
                credits=Coalesce(Sum("credit"), "0"),
                debits=Coalesce(Sum("debit"), "0"),
            )
            .first()
            .values("credits", "debits")
        )

        gig_balance = Decimal(gig_monies["credits"]) - Decimal(gig_monies["debits"])

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Balance fetched successfully.",
            data={
                "balance": gig_balance,
            },
        )

    async def overview(self, user_id: UUID) -> dict[str, Any]:
        """Get overview of a user's offerings."""
        active_gigs_count, total_clients = await asyncio.gather(
            Gig.filter(user_id=user_id, ends_at__gt=datetime.now(UTC)).count(),
            Client.filter(user_id=user_id).count(),
        )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Overview fetched successfully.",
            data={
                "active_gigs_count": active_gigs_count,
                "total_clients": total_clients,
            },
        )

    async def create_gig(
        self,
        user_id: UUID,
        name: str,
        price: Decimal,
        frequency: OfferingFrequency,
        ends_at: datetime,
        auto_collection: bool = False,
        description: str | None = None,
        client: ClientInfo | None = None,
    ) -> dict[str, Any]:
        """Create a new gig."""
        if (not client or not client.get("email")) and auto_collection:
            error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Automatic collection requires a client.",
            )

        if client:
            client_obj = await Client.create(user_id=user_id, **client)
        else:
            client_obj = None

        gig = await Gig.create(
            user_id=user_id,
            name=name,
            description=description,
            client=client_obj,
            price=price,
            frequency=frequency,
            automatic_collection=auto_collection,
            ends_at=ends_at,
        )

        if not auto_collection:
            # TODO: Provision VA
            gig.account_name = f"{gig.name} - {gig.id}"
            gig.account_number = "".join(
                [str(secrets.randbelow(10)) for _ in range(10)]
            )
            gig.account_bank = "Paytract Bank"
            await gig.save()

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="Gig created successfully.",
            data={
                "id": gig.id,
                "name": gig.name,
                "description": gig.description,
                "automatic_collection": gig.automatic_collection,
                "price": gig.price,
                "frequency": gig.frequency,
                "ends_at": gig.ends_at,
            },
        )

    async def list_gigs(
        self,
        user_id: UUID,
        search: str | None,
        state: OfferingStatus | None,
        params: PaginationParams,
    ) -> dict[str, Any]:
        """List gigs for a user."""
        query = Gig.filter(user_id=user_id)
        if search:
            query = query.filter(
                Q(name__icontains=search, description__icontains=search, join_type=Q.OR)
            )

        if state:
            if state == OfferingStatus.PAID:
                query = query.filter(ends_at__gt=datetime.now(UTC))
            elif state == OfferingStatus.OWING:
                query = query.filter(ends_at__lt=datetime.now(UTC))
            elif state == OfferingStatus.COMPLETED:
                query = query.filter(ends_at__lt=datetime.now(UTC))

        gigs = (
            await query.order_by("-created_at")
            .offset((params["page"] - 1) * params["limit"])
            .limit(params["limit"])
            .annotate(
                pending_durations=Coalesce(
                    Count(
                        "durations__status",
                        _filter=Q(
                            durations__status__in={
                                DurationStatus.PENDING,
                                DurationStatus.PARTIAL,
                            }
                        ),
                    ),
                    0,
                ),
            )
        )

        balances_data = (
            await Ledger.filter(
                account_id__in={gig.id for gig in gigs}, account_type=AccountTypes.GIG
            )
            .annotate(
                credits=Coalesce(Sum("credit"), "0"),
                debits=Coalesce(Sum("debit"), "0"),
            )
            .group_by("account_id")
            .values("account_id", "credits", "debits")
        )

        balances = {
            item["account_id"]: Decimal(item["credits"]) - Decimal(item["debits"])
            for item in balances_data
        }

        total_gigs = await Gig.filter(user_id=user_id).count()

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Gigs fetched successfully.",
            data={
                "gigs": [
                    {
                        "id": gig.id,
                        "name": gig.name,
                        "balance": balances.get(gig.id, Decimal("0")),
                        "status": (
                            OfferingStatus.OWING
                            if gig.pending_durations > 1
                            else OfferingStatus.COMPLETED
                            if (
                                gig.ends_at < datetime.now(UTC)
                                and gig.pending_durations == 0
                            )
                            else OfferingStatus.PAID
                        ),
                    }
                    for gig in gigs
                ],
                "pagination": {
                    "page": params["page"],
                    "pages": (total_gigs + params["limit"] - 1) // params["limit"],
                    "limit": params["limit"],
                    "total": total_gigs,
                    "count": len(gigs),
                },
            },
        )

    async def get_gig(self, user_id: UUID, gig_id: UUID) -> dict[str, Any]:
        """Get a gig by ID."""
        gig, balance_data = await asyncio.gather(
            Gig.get_or_none(id=gig_id, user_id=user_id)
            .prefetch_related("client")
            .annotate(
                last_paid_collection_date=Max(
                    "durations__end_at",
                    _filter=Q(durations__status=DurationStatus.PAID),
                ),
                next_due_collection_date=Max("durations__end_at"),
            ),
            Ledger.filter(account_id=gig_id, account_type=AccountTypes.GIG)
            .annotate(
                credits=Coalesce(Sum("credit"), "0"),
                debits=Coalesce(Sum("debit"), "0"),
            )
            .first()
            .values("credits", "debits"),
        )
        if not gig:
            error_response(
                status_code=status.HTTP_404_NOT_FOUND, message="Gig not found."
            )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Gig fetched successfully.",
            data={
                "id": gig.id,
                "name": gig.name,
                "description": gig.description,
                "balance": (
                    Decimal(balance_data["credits"]) - Decimal(balance_data["debits"])
                ),
                "automatic_collection": gig.automatic_collection,
                "price": gig.price,
                "frequency": gig.frequency,
                "ends_at": gig.ends_at,
                "last_payment_at": gig.last_paid_collection_date,
                "next_payment_due": gig.next_due_collection_date,
                "account": {
                    "name": gig.account_name,
                    "number": gig.account_number,
                    "bank": gig.account_bank,
                },
                "client": (
                    {
                        "id": gig.client.id if gig.client else None,
                        "name": gig.client.name if gig.client else None,
                        "email": gig.client.email if gig.client else None,
                    }
                    if gig.client
                    else {}
                ),
            },
        )

    async def validate_active_gig(self, gig_id: UUID) -> dict[str, Any]:
        """Validate if a gig is active."""
        gig = await Gig.get_or_none(id=gig_id)
        if not gig:
            error_response(
                status_code=status.HTTP_404_NOT_FOUND, message="Gig not found."
            )

        if gig.ends_at < datetime.now(UTC):
            error_response(
                status_code=status.HTTP_400_BAD_REQUEST, message="This gig has ended."
            )

        return success_response(
            status_code=status.HTTP_200_OK, message="Gig is active."
        )

    async def get_gig_signing_details(
        self, gig_id: UUID, client_email: str
    ) -> dict[str, Any]:
        """Get signing details for a gig."""
        gig = await Gig.get_or_none(id=gig_id).prefetch_related("client")
        if not gig:
            error_response(
                status_code=status.HTTP_404_NOT_FOUND, message="Gig not found."
            )

        if not gig.client or gig.client.email != client_email:
            error_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="You are not authorized to sign this gig.",
            )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Signing details fetched successfully.",
            data={
                "id": gig.id,
                "name": gig.name,
                "description": gig.description,
                "price": gig.price,
                "frequency": gig.frequency,
                "ends_at": gig.ends_at,
            },
        )
