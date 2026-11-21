"""Database access for securities."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import fetch_page, flush_or_conflict
from app.errors import NotFoundError
from app.models import Security
from app.schemas.pagination import PageParams
from app.schemas.security import SecurityCreate


class SecurityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_symbol(self, symbol: str) -> Security:
        security = self._session.scalar(select(Security).where(Security.symbol == symbol))
        if security is None:
            raise NotFoundError(f"Security {symbol} not found")
        return security

    def list_page(self, page: PageParams) -> tuple[list[Security], int]:
        # Paging needs a stable order; symbol is unique, so pages never overlap.
        return fetch_page(self._session, select(Security).order_by(Security.symbol), page)

    def add(self, data: SecurityCreate) -> Security:
        security = Security(**data.model_dump())
        self._session.add(security)
        flush_or_conflict(self._session, f"Security {data.symbol} already exists")
        return security
