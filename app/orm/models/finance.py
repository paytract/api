from uuid import UUID
from decimal import Decimal

from tortoise import fields, models

from app.enums.finance import AccountTypes, SystemAccounts, TransactionTypes


class SystemAccount(models.Model):
    """System Account model."""

    id: UUID = fields.UUIDField(primary_key=True)
    name: SystemAccounts = fields.CharEnumField(
        SystemAccounts, max_length=50, unique=True
    )

    class Meta(models.Model.Meta):
        """System Account model metadata."""

        table = "system_accounts"


class Ledger(models.Model):
    """Ledger model."""

    entry_id: int = fields.BigIntField(primary_key=True)
    trace_id: UUID = fields.UUIDField()
    account_type: AccountTypes = fields.CharEnumField(AccountTypes, max_length=50)
    account_id: UUID = fields.UUIDField()
    credit: Decimal = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit: Decimal = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    narration: str = fields.TextField(null=True)

    class Meta(models.Model.Meta):
        """Ledger model metadata."""

        table = "ledgers"
        indexes = (("trace_id",), ("account_id", "account_type"))


class Transaction(models.Model):
    """Transaction model."""

    id: UUID = fields.UUIDField(primary_key=True)
    trace_id: UUID = fields.UUIDField()
    account_type: AccountTypes = fields.CharEnumField(AccountTypes, max_length=50)
    account_id: UUID = fields.UUIDField()
    amount: Decimal = fields.DecimalField(max_digits=10, decimal_places=2)
    narration: str = fields.TextField(null=True)
    type: TransactionTypes = fields.CharEnumField(TransactionTypes, max_length=10)

    class Meta(models.Model.Meta):
        """Transaction model metadata."""

        table = "transactions"
        indexes = (("trace_id",), ("account_id", "account_type", "type"))
