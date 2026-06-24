from typing import TypedDict, NotRequired


class UploadResponse(TypedDict):
    """File Upload Response."""

    success: bool
    filename: str
    url: str
    message: NotRequired[str]
