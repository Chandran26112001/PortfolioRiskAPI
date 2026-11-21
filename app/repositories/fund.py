"""Database access for funds."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import fetch_page, flush_or_conflict
from app.errors import NotFoundError
from app.models import Fund
from app.schemas.fund import FundCreate
from app.schemas.pagination import PageParams


class FundRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_code(self, code: str) -> Fund:
        fund = self._session.scalar(select(Fund).where(Fund.code == code))
        if fund is None:
            raise NotFoundError(f"Fund {code} not found")
        return fund

    def list_page(self, page: PageParams) -> tuple[list[Fund], int]:
        return fetch_page(self._session, select(Fund).order_by(Fund.code), page)

    def add(self, data: FundCreate) -> Fund:
        fund = Fund(**data.model_dump())
        self._session.add(fund)
        flush_or_conflict(self._session, f"Fund {data.code} already exists")
        return fund
