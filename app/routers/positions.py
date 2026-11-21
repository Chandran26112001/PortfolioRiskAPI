"""Endpoints for a fund's positions."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import FundRepoDep, PositionRepoDep, SecurityRepoDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.pagination import Page, PageParams
from app.schemas.position import PositionCreate, PositionRead
from app.schemas.types import FundCode

router = APIRouter(
    prefix="/funds/{code}/positions",
    tags=["positions"],
    responses=NOT_FOUND | VALIDATION_ERROR,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Add a position to a fund",
    responses=CONFLICT,
)
def create_position(
    code: FundCode,
    body: PositionCreate,
    funds: FundRepoDep,
    securities: SecurityRepoDep,
    positions: PositionRepoDep,
) -> PositionRead:
    fund = funds.get_by_code(code)
    security = securities.get_by_symbol(body.symbol)
    position = positions.add(fund, security, body.quantity, body.as_of_date)
    return PositionRead.model_validate(position)


@router.get("", summary="List a fund's positions")
def list_positions(
    code: FundCode,
    page: Annotated[PageParams, Query()],
    funds: FundRepoDep,
    positions: PositionRepoDep,
    as_of: Annotated[date | None, Query(description="Only positions on this date.")] = None,
) -> Page[PositionRead]:
    fund = funds.get_by_code(code)
    items, total = positions.list_for_fund(fund, as_of, page)
    return Page[PositionRead](
        items=[PositionRead.model_validate(position) for position in items],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )
