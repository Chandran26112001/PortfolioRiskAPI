"""Request and response models for securities."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import CurrencyCode, Name, Sector, Symbol


class SecurityBase(BaseModel):
    symbol: Symbol = Field(description="Ticker symbol.", examples=["AAPL"])
    name: Name = Field(examples=["Apple Inc."])
    sector: Sector = Field(examples=[Sector.INFORMATION_TECHNOLOGY])
    currency: CurrencyCode = Field(description="ISO 4217 currency code.", examples=["USD"])


class SecurityCreate(SecurityBase):
    """Body of POST /securities."""

    model_config = ConfigDict(extra="forbid")


class SecurityRead(SecurityBase):
    """A security as returned by the API."""

    # Lets model_validate read attributes from a SQLAlchemy object, not just a dict.
    model_config = ConfigDict(from_attributes=True)
