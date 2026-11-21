"""Database access for daily closing prices."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import fetch_page, flush_or_conflict
from app.models import Price, Security
from app.schemas.pagination import PageParams


class PriceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_security(self, security: Security, page: PageParams) -> tuple[list[Price], int]:
        query = select(Price).where(Price.security_id == security.id).order_by(Price.price_date)
        return fetch_page(self._session, query, page)

    def add(self, security: Security, price_date: date, close: Decimal) -> Price:
        price = Price(security=security, price_date=price_date, close=close)
        self._session.add(price)
        flush_or_conflict(self._session, f"{security.symbol} already has a price on {price_date}")
        return price
