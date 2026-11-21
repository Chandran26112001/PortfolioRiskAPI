"""Dependencies that FastAPI injects into route functions.

FastAPI creates each dependency once per request, so all repositories in one request
share the same session and therefore the same transaction.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.repositories.fund import FundRepository
from app.repositories.position import PositionRepository
from app.repositories.price import PriceRepository
from app.repositories.security import SecurityRepository

SessionDep = Annotated[Session, Depends(get_session)]


def get_security_repository(session: SessionDep) -> SecurityRepository:
    return SecurityRepository(session)


def get_fund_repository(session: SessionDep) -> FundRepository:
    return FundRepository(session)


def get_position_repository(session: SessionDep) -> PositionRepository:
    return PositionRepository(session)


def get_price_repository(session: SessionDep) -> PriceRepository:
    return PriceRepository(session)


SecurityRepoDep = Annotated[SecurityRepository, Depends(get_security_repository)]
FundRepoDep = Annotated[FundRepository, Depends(get_fund_repository)]
PositionRepoDep = Annotated[PositionRepository, Depends(get_position_repository)]
PriceRepoDep = Annotated[PriceRepository, Depends(get_price_repository)]
