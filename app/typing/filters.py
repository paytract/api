from typing import TypedDict
from datetime import datetime


class DateRangeFilter(TypedDict):
    """Date Range Filter Parameters."""

    start_date: datetime | None
    end_date: datetime | None
