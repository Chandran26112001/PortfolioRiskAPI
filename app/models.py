"""Database tables, defined as SQLAlchemy ORM classes (the JPA @Entity equivalent)."""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Identity,
    Index,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.schemas.types import Sector

# Fixed constraint names, so migrations and Oracle error messages are predictable.
NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}

SECTOR_VALUES = ", ".join(f"'{sector.value}'" for sector in Sector)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Security(Base):
    __tablename__ = "securities"
    __table_args__ = (
        UniqueConstraint("symbol"),
        CheckConstraint(f"sector IN ({SECTOR_VALUES})", name="sector"),
        CheckConstraint("REGEXP_LIKE(currency, '^[A-Z]{3}$')", name="currency"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(12))
    name: Mapped[str] = mapped_column(String(100))
    sector: Mapped[str] = mapped_column(String(30))
    currency: Mapped[str] = mapped_column(String(3))


class Fund(Base):
    __tablename__ = "funds"
    __table_args__ = (
        UniqueConstraint("code"),
        CheckConstraint("REGEXP_LIKE(base_currency, '^[A-Z]{3}$')", name="base_currency"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(100))
    base_currency: Mapped[str] = mapped_column(String(3))


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        # Column order matters: this index also serves "positions of fund X on date D".
        UniqueConstraint("fund_id", "as_of_date", "security_id"),
        # Oracle locks the whole child table on parent deletes if a foreign key isn't indexed.
        Index(None, "security_id"),
        CheckConstraint("quantity <> 0", name="quantity_not_zero"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"))
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    as_of_date: Mapped[date] = mapped_column(Date)

    fund: Mapped[Fund] = relationship()
    security: Mapped[Security] = relationship()

    @property
    def fund_code(self) -> str:
        return self.fund.code

    @property
    def symbol(self) -> str:
        return self.security.symbol


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("security_id", "price_date"),
        CheckConstraint("close > 0", name="close_positive"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"))
    price_date: Mapped[date] = mapped_column(Date)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6))

    security: Mapped[Security] = relationship()

    @property
    def symbol(self) -> str:
        return self.security.symbol
