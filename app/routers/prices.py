"""Endpoints for a security's daily closing prices."""

from fastapi import APIRouter, status

from app.dependencies import StoreDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
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
async def create_price(symbol: Symbol, body: PriceCreate, store: StoreDep) -> PriceRead:
    price = PriceRead(symbol=symbol, **body.model_dump())
    store.add_price(price)
    return price


@router.get("", summary="List a security's price history")
async def list_prices(symbol: Symbol, store: StoreDep) -> list[PriceRead]:
    return store.list_prices(symbol)
