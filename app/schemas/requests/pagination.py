from pydantic import Field, BaseModel


class PageFilter(BaseModel):
    """Page Filter."""

    page: int = Field(default=1, description="Current page", ge=1)
    limit: int = Field(default=10, description="Page max length", ge=1, le=100)


class SearchPageFilter(PageFilter):
    """Search & Page Filter."""

    search: str | None = Field(
        default=None, description="Search by name and description"
    )


class OffsetFilter(BaseModel):
    """Offset Filter."""

    offset: int = Field(default=0, description="Start", ge=0)
    limit: int = Field(default=10, description="Max length", ge=1, le=10)


class CursorFilter(BaseModel):
    """Cursor Filter."""

    cursor: int = Field(default=0, description="Start", ge=0)
    limit: int = Field(default=10, description="Max length", ge=1, le=10)
