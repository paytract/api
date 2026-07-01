from enum import StrEnum


class OfferingFrequency(StrEnum):
    """Offering Frequency Enum."""

    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    EVERY_SIX_MONTHS = "EVERY_SIX_MONTHS"
    EVERY_TWELVE_MONTHS = "EVERY_TWELVE_MONTHS"


class DurationStatus(StrEnum):
    """Duration Status Enum."""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"


class OfferingStatus(StrEnum):
    """Offering Status Enum."""

    PAID = "PAID"
    OWING = "OWING"
    COMPLETED = "COMPLETED"
