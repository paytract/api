from typing import TypedDict


class PaginationParams(TypedDict):
    """Pagination Parameters."""

    page: int
    limit: int


class OffsetParams(TypedDict):
    """Offset Parameters."""

    offset: int
    limit: int


class CursorParams(TypedDict):
    """Cursor Parameters."""

    cursor: int
    limit: int


class PaginationMetadata(TypedDict):
    """Pagination Metadata."""

    page: int
    pages: int
    limit: int
    total: int
    count: int


class OffsetMetadata(TypedDict):
    """Offset Metadata."""

    offset: int
    limit: int
    total: int
    count: int


class CursorMetadata(TypedDict):
    """Cursor Metadata."""

    next_cursor: int
    limit: int
    total: int
    count: int
