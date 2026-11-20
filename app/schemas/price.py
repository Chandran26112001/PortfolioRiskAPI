"""Request and response models for daily closing prices."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import PriceAmount, Symbol


class PriceCreate(BaseModel):
    """Body of POST /securities/{symbol}/prices. The security comes from the URL."""

    model_config = ConfigDict(extra="forbid")

    price_date: date = Field(examples=["2026-11-13"])
    close: PriceAmount = Field(
        description="Closing price in the security's currency.", examples=["227.48"]
    )


class PriceRead(BaseModel):
    """A closing price as returned by the API."""

    symbol: Symbol
    price_date: date
    close: PriceAmount
