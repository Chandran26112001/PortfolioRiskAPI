"""Request and response models for fund positions."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import FundCode, Quantity, Symbol


class PositionCreate(BaseModel):
    """Body of POST /funds/{code}/positions. The fund comes from the URL."""

    model_config = ConfigDict(extra="forbid")

    symbol: Symbol = Field(examples=["AAPL"])
    quantity: Quantity = Field(
        description="Number of units held. Negative for a short position.", examples=["1500"]
    )
    as_of_date: date = Field(examples=["2026-11-13"])


class PositionRead(BaseModel):
    """A position as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    fund_code: FundCode
    symbol: Symbol
    quantity: Quantity
    as_of_date: date
