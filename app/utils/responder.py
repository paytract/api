from typing import Any, Never

from app.utils.exceptions import ErrorResponse
from app.typing.pagination import CursorMetadata, OffsetMetadata, PaginationMetadata


def success_response(
    status_code: int,
    message: str,
    data: Any = None,
) -> dict[str, Any]:
    """Returns a response for success responses."""
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
    }


def paginated_success_response(
    status_code: int,
    message: str,
    metadata: PaginationMetadata,
    data: Any = None,
) -> dict[str, Any]:
    """Returns a paginated response for success responses."""
    return {
        "status_code": status_code,
        "message": message,
        "metadata": metadata,
        "data": data,
    }


def offset_success_response(
    status_code: int,
    message: str,
    metadata: OffsetMetadata,
    data: Any = None,
) -> dict[str, Any]:
    """Returns an offset response for success responses."""
    return {
        "status_code": status_code,
        "message": message,
        "metadata": metadata,
        "data": data,
    }


def cursor_success_response(
    status_code: int,
    message: str,
    metadata: CursorMetadata,
    data: Any = None,
) -> dict[str, Any]:
    """Returns a cursor response for success responses."""
    return {
        "status_code": status_code,
        "message": message,
        "metadata": metadata,
        "data": data,
    }


def error_response(status_code: int, message: str) -> Never:
    """Response for failure responses.

    Raises:
        ErrorResponse: Custom HTTP Error.
    """
    raise ErrorResponse(status_code, message)
