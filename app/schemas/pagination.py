"""Paging for list endpoints: ?limit=50&offset=100 in, a Page envelope out."""

from pydantic import BaseModel, Field


class PageParams(BaseModel):
    """Query parameters shared by every list endpoint."""

    limit: int = Field(default=50, ge=1, le=500, description="Maximum number of items to return.")
    offset: int = Field(default=0, ge=0, description="Number of items to skip.")


class Page[T](BaseModel):
    """One page of results, plus what a client needs to fetch the next one."""

    items: list[T]
    total: int = Field(description="Number of items across all pages.")
    limit: int
    offset: int
