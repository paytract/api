import asyncio
import secrets
from uuid import UUID
from typing import Any
from decimal import Decimal
from datetime import UTC, datetime

from fastapi import status
from tortoise.functions import Sum, Coalesce

from app.env import settings
from app.orm.models import Gig, Client, Ledger, Contract
from app.enums.finance import AccountTypes
from app.enums.offerings import OfferingFrequency
from app.utils.responder import error_response, success_response
from app.typing.offerings import ClientInfo


class OfferingService:
    """Offering Service."""

    async def total_balance(self, user_id: UUID) -> dict[str, Any]:
        """Get total balance for a user."""
        gig_ids, contract_ids = await asyncio.gather(
            Gig.filter(user_id=user_id).values_list("id", flat=True),
            Contract.filter(user_id=user_id).values_list("id", flat=True),
        )

        gig_monies, contract_monies = await asyncio.gather(
            (
                Ledger.filter(account_id__in=gig_ids, account_type=AccountTypes.GIG)
                .annotate(
                    credits=Coalesce(Sum("credit"), "0"),
                    debits=Coalesce(Sum("debit"), "0"),
                )
                .first()
                .values("credits", "debits")
            ),
            (
                Ledger.filter(
                    account_id__in=contract_ids, account_type=AccountTypes.CONTRACT
                )
                .annotate(
                    credits=Coalesce(Sum("credit"), "0"),
                    debits=Coalesce(Sum("debit"), "0"),
                )
                .first()
                .values("credits", "debits")
            ),
        )

        gig_balance = Decimal(gig_monies["credits"]) - Decimal(gig_monies["debits"])
        contract_balance = Decimal(contract_monies["credits"]) - Decimal(
            contract_monies["debits"]
        )
        total_balance = gig_balance + contract_balance

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Balance fetched successfully.",
            data={
                "gig_balance": gig_balance,
                "contract_balance": contract_balance,
                "total_balance": total_balance,
            },
        )

    async def overview(self, user_id: UUID) -> dict[str, Any]:
        """Get overview of a user's offerings."""
        active_gigs_count, active_contracts_count, total_clients = await asyncio.gather(
            Gig.filter(user_id=user_id, ends_at__gt=datetime.now(UTC)).count(),
            Contract.filter(user_id=user_id, ends_at__gt=datetime.now(UTC)).count(),
            Client.filter(user_id=user_id).count(),
        )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Overview fetched successfully.",
            data={
                "active_gigs_count": active_gigs_count,
                "active_contracts_count": active_contracts_count,
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
        description: str | None = None,
        client: ClientInfo | None = None,
    ) -> dict[str, Any]:
        """Create a new gig."""
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
            ends_at=ends_at,
        )

        # TODO: Provision VA
        gig.account_name = f"{gig.name} - {gig.id}"
        gig.account_number = "".join([str(secrets.randbelow(10)) for _ in range(10)])
        gig.account_bank = "Paytract Bank"
        await gig.save()

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="Gig created successfully.",
            data={
                "id": gig.id,
                "name": gig.name,
                "description": gig.description,
            },
        )

    async def create_contract(
        self,
        user_id: UUID,
        name: str,
        price: Decimal,
        frequency: OfferingFrequency,
        ends_at: datetime,
        description: str | None = None,
        client: ClientInfo | None = None,
    ) -> dict[str, Any]:
        """Create a new contract."""
        if client:
            client_obj = await Client.create(user_id=user_id, **client)
        else:
            client_obj = None

        contract = await Contract.create(
            user_id=user_id,
            name=name,
            description=description,
            client=client_obj,
            price=price,
            frequency=frequency,
            ends_at=ends_at,
        )

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="Contract created successfully.",
            data={
                "id": contract.id,
                "name": contract.name,
                "description": contract.description,
                "price": contract.price,
                "frequency": contract.frequency,
                "ends_at": contract.ends_at,
                "signing_url": f"{settings.FRONTEND_URL}/contracts/{contract.id}/sign",
            },
        )

    async def get_signing_details(
        self, contract_id: UUID, client_email: str
    ) -> dict[str, Any]:
        """Get signing details for a contract."""
        contract = await Contract.get_or_none(id=contract_id).prefetch_related("client")
        if not contract:
            error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Contract not found.",
            )

        if not contract.client or contract.client.email != client_email:
            error_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="You are not authorized to sign this contract.",
            )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Signing details fetched successfully.",
            data={
                "id": contract.id,
                "name": contract.name,
                "description": contract.description,
                "price": contract.price,
                "frequency": contract.frequency,
                "ends_at": contract.ends_at,
            },
        )
