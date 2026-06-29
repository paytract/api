from enum import StrEnum


class OfferingFrequency(StrEnum):
    """Offering Frequency Enum."""

    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    EVERY_SIX_MONTHS = "EVERY_SIX_MONTHS"
    EVERY_TWELVE_MONTHS = "EVERY_TWELVE_MONTHS"
