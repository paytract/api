from enum import StrEnum


class EmailType(StrEnum):
    """Enum to represent different types of email notifications."""

    VERIFICATION = "verification"
    WELCOME = "welcome"
    CREDENTIALS_RESET = "credentials_reset"
