from pydantic import BaseModel


class SuccessResponseSchema[T](BaseModel):
    """Success Response Schema."""

    status_code: int
    message: str
    data: T | None = None


class ErrorResponseSchema(BaseModel):
    """Error Response Schema."""

    status_code: int
    message: str


class ValidationErrorResponseSchema(BaseModel):
    """Validation Error Response Schema."""

    status_code: int
    message: str
    errors: list[str] | None = None


class _PaginationMetadata(BaseModel):
    page: int
    pages: int
    limit: int
    total: int
    count: int


class PaginatedSuccessResponseSchema[T](BaseModel):
    """Paginated Response Schema."""

    status_code: int
    message: str
    metadata: _PaginationMetadata
    data: list[T]


class _OffsetMetadata(BaseModel):
    offset: int
    limit: int
    total: int
    count: int


class OffsetSuccessResponseSchema[T](BaseModel):
    """Offset Response Schema."""

    status_code: int
    message: str
    metadata: _OffsetMetadata
    data: list[T]


class _CursorMetadata(BaseModel):
    next_cursor: int
    limit: int
    total: int
    count: int


class CursorSuccessResponseSchema[T](BaseModel):
    """Cursor Response Schema."""

    status_code: int
    message: str
    metadata: _CursorMetadata
    data: list[T]
