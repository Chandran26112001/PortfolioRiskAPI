"""Endpoints for a security's daily closing prices."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import PriceRepoDep, SecurityRepoDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.pagination import Page, PageParams
from app.schemas.price import PriceCreate, PriceRead
from app.schemas.types import Symbol

router = APIRouter(
    prefix="/securities/{symbol}/prices",
    tags=["prices"],
    responses=NOT_FOUND | VALIDATION_ERROR,
)


@router.post(
    "", status_code=status.HTTP_201_CREATED, summary="Add a closing price", responses=CONFLICT
)
def create_price(
    symbol: Symbol, body: PriceCreate, securities: SecurityRepoDep, prices: PriceRepoDep
) -> PriceRead:
    security = securities.get_by_symbol(symbol)
    price = prices.add(security, body.price_date, body.close)
    return PriceRead.model_validate(price)


@router.get("", summary="List a security's price history")
def list_prices(
    symbol: Symbol,
    page: Annotated[PageParams, Query()],
    securities: SecurityRepoDep,
    prices: PriceRepoDep,
) -> Page[PriceRead]:
    security = securities.get_by_symbol(symbol)
    items, total = prices.list_for_security(security, page)
    return Page[PriceRead](
        items=[PriceRead.model_validate(price) for price in items],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )
