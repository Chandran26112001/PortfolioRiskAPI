"""Endpoints for funds."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import FundRepoDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.fund import FundCreate, FundRead
from app.schemas.pagination import Page, PageParams
from app.schemas.types import FundCode

router = APIRouter(prefix="/funds", tags=["funds"], responses=VALIDATION_ERROR)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a fund", responses=CONFLICT)
def create_fund(body: FundCreate, funds: FundRepoDep) -> FundRead:
    return FundRead.model_validate(funds.add(body))


@router.get("", summary="List funds")
def list_funds(page: Annotated[PageParams, Query()], funds: FundRepoDep) -> Page[FundRead]:
    items, total = funds.list_page(page)
    return Page[FundRead](
        items=[FundRead.model_validate(fund) for fund in items],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{code}", summary="Get a fund", responses=NOT_FOUND)
def get_fund(code: FundCode, funds: FundRepoDep) -> FundRead:
    return FundRead.model_validate(funds.get_by_code(code))
