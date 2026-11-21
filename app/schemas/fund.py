"""Request and response models for funds."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import CurrencyCode, FundCode, Name


class FundBase(BaseModel):
    code: FundCode = Field(description="Short fund identifier.", examples=["GLOBAL-EQ"])
    name: Name = Field(examples=["Global Equity Fund"])
    base_currency: CurrencyCode = Field(
        description="Currency the fund reports in (ISO 4217).", examples=["USD"]
    )


class FundCreate(FundBase):
    """Body of POST /funds."""

    model_config = ConfigDict(extra="forbid")


class FundRead(FundBase):
    """A fund as returned by the API."""

    model_config = ConfigDict(from_attributes=True)
