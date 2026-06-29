from typing import TypedDict


class ContractMetadata(TypedDict):
    """Contract Metadata TypedDict."""

    client_account_number: str
    client_bank_name: str
    client_name: str
    client_address: str
    client_phone: str
    client_email: str


class ClientInfo(TypedDict):
    """Client Info TypedDict."""

    name: str | None
    email: str | None
