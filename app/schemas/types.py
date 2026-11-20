"""Reusable constrained types shared by the API schemas."""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field, StringConstraints


class Sector(StrEnum):
    """The 11 GICS sectors. A fixed list keeps sector exposure groupings consistent."""

    ENERGY = "Energy"
    MATERIALS = "Materials"
    INDUSTRIALS = "Industrials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    HEALTH_CARE = "Health Care"
    FINANCIALS = "Financials"
    INFORMATION_TECHNOLOGY = "Information Technology"
    COMMUNICATION_SERVICES = "Communication Services"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"


def _strip(value: object) -> object:
    """Remove surrounding spaces before the length checks run."""
    if isinstance(value, str):
        return value.strip()
    return value


def _strip_and_upper(value: object) -> object:
    """Accept codes in any case: ' brk.b ' becomes 'BRK.B' before the pattern check runs."""
    if isinstance(value, str):
        return value.strip().upper()
    return value


def _reject_zero(value: Decimal) -> Decimal:
    if value == 0:
        raise ValueError("must not be zero")
    return value


# BeforeValidator runs on the raw input, before the StringConstraints checks.
Symbol = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z0-9.\-]{1,12}$"),
    BeforeValidator(_strip_and_upper),
]

FundCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z0-9\-]{1,20}$"),
    BeforeValidator(_strip_and_upper),
]

CurrencyCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{3}$"),
    BeforeValidator(_strip_and_upper),
]

Name = Annotated[
    str,
    StringConstraints(min_length=1, max_length=100),
    BeforeValidator(_strip),
]

# Up to 12 digits before the decimal point and 6 after, matching NUMBER(18, 6) in Oracle later.
Quantity = Annotated[
    Decimal,
    Field(max_digits=18, decimal_places=6),
    AfterValidator(_reject_zero),
]

PriceAmount = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=6)]
