"""Endpoints for securities."""

from fastapi import APIRouter, status

from app.dependencies import StoreDep
from app.schemas.errors import CONFLICT, NOT_FOUND, VALIDATION_ERROR
from app.schemas.security import SecurityCreate, SecurityRead
from app.schemas.types import Symbol

router = APIRouter(prefix="/securities", tags=["securities"], responses=VALIDATION_ERROR)


@router.post(
    "", status_code=status.HTTP_201_CREATED, summary="Create a security", responses=CONFLICT
)
async def create_security(body: SecurityCreate, store: StoreDep) -> SecurityRead:
    security = SecurityRead(**body.model_dump())
    store.add_security(security)
    return security


@router.get("", summary="List securities")
async def list_securities(store: StoreDep) -> list[SecurityRead]:
    return store.list_securities()


@router.get("/{symbol}", summary="Get a security", responses=NOT_FOUND)
async def get_security(symbol: Symbol, store: StoreDep) -> SecurityRead:
    return store.get_security(symbol)
