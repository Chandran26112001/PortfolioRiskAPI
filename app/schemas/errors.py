"""The single error body that every failed request returns."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str = Field(examples=["body.close"])
    message: str = Field(examples=["Input should be greater than 0"])


class ErrorResponse(BaseModel):
    code: str = Field(examples=["not_found"])
    message: str = Field(examples=["Security MSFT not found"])
    details: list[ErrorDetail] = Field(default_factory=list)


# Used in route decorators so /docs shows the real error body for each status.
NOT_FOUND: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Not found"}
}
CONFLICT: dict[int | str, dict[str, Any]] = {
    409: {"model": ErrorResponse, "description": "Already exists"}
}
VALIDATION_ERROR: dict[int | str, dict[str, Any]] = {
    422: {"model": ErrorResponse, "description": "Invalid request"}
}
