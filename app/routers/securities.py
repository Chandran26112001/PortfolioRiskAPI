"""Endpoints for securities.

Routes are plain `def` because database calls block: FastAPI runs them in a thread pool
so they don't stall the event loop.
"""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import SecurityRepoDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.pagination import Page, PageParams
from app.schemas.security import SecurityCreate, SecurityRead
from app.schemas.types import Symbol

router = APIRouter(prefix="/securities", tags=["securities"], responses=VALIDATION_ERROR)


@router.post(
    "", status_code=status.HTTP_201_CREATED, summary="Create a security", responses=CONFLICT
)
def create_security(body: SecurityCreate, securities: SecurityRepoDep) -> SecurityRead:
    return SecurityRead.model_validate(securities.add(body))


@router.get("", summary="List securities")
def list_securities(
    page: Annotated[PageParams, Query()], securities: SecurityRepoDep
) -> Page[SecurityRead]:
    items, total = securities.list_page(page)
    return Page[SecurityRead](
        items=[SecurityRead.model_validate(security) for security in items],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{symbol}", summary="Get a security", responses=NOT_FOUND)
def get_security(symbol: Symbol, securities: SecurityRepoDep) -> SecurityRead:
    return SecurityRead.model_validate(securities.get_by_symbol(symbol))
