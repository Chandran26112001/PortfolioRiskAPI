"""Endpoints for a fund's positions."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import StoreDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
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
async def create_position(code: FundCode, body: PositionCreate, store: StoreDep) -> PositionRead:
    position = PositionRead(fund_code=code, **body.model_dump())
    store.add_position(position)
    return position


@router.get("", summary="List a fund's positions")
async def list_positions(
    code: FundCode,
    store: StoreDep,
    as_of: Annotated[date | None, Query(description="Only positions on this date.")] = None,
) -> list[PositionRead]:
    return store.list_positions(code, as_of)
