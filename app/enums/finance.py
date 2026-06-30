from enum import StrEnum


class SystemAccounts(StrEnum):
    """System Accounts Enum."""

    PAYTRACT_FEES = "PAYTRACT_FEES"


class AccountTypes(StrEnum):
    """Account Types Enum."""

    SYSTEM = "SYSTEM"
    GIG = "GIG"


class TransactionTypes(StrEnum):
    """Transaction Types Enum."""

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
