"""Database access for fund positions."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.db import fetch_page, flush_or_conflict
from app.models import Fund, Position, Security
from app.schemas.pagination import PageParams


class PositionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_fund(
        self, fund: Fund, as_of_date: date | None, page: PageParams
    ) -> tuple[list[Position], int]:
        # Join securities once and fill position.security from that join (contains_eager),
        # instead of one extra query per position.
        query = (
            select(Position)
            .join(Position.security)
            .options(contains_eager(Position.security))
            .where(Position.fund_id == fund.id)
            .order_by(Position.as_of_date, Security.symbol)
        )
        if as_of_date is not None:
            query = query.where(Position.as_of_date == as_of_date)
        return fetch_page(self._session, query, page)

    def add(self, fund: Fund, security: Security, quantity: Decimal, as_of_date: date) -> Position:
        position = Position(fund=fund, security=security, quantity=quantity, as_of_date=as_of_date)
        self._session.add(position)
        flush_or_conflict(
            self._session,
            f"Fund {fund.code} already has a position in {security.symbol} on {as_of_date}",
        )
        return position
