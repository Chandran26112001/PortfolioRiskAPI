"""Endpoints for funds."""

from fastapi import APIRouter, status

from app.dependencies import StoreDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.fund import FundCreate, FundRead
from app.schemas.types import FundCode

router = APIRouter(prefix="/funds", tags=["funds"], responses=VALIDATION_ERROR)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a fund", responses=CONFLICT)
async def create_fund(body: FundCreate, store: StoreDep) -> FundRead:
    fund = FundRead(**body.model_dump())
    store.add_fund(fund)
    return fund


@router.get("", summary="List funds")
async def list_funds(store: StoreDep) -> list[FundRead]:
    return store.list_funds()


@router.get("/{code}", summary="Get a fund", responses=NOT_FOUND)
async def get_fund(code: FundCode, store: StoreDep) -> FundRead:
    return store.get_fund(code)
