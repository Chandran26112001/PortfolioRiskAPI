"""In-memory storage, used until the database arrives in Stage 2.

Data lives in the server process: it is lost on restart, and each worker process
would have its own separate copy.

The checks here (unknown fund, duplicate key) are the ones the database will enforce
with foreign keys and unique constraints in Stage 2.
"""

from datetime import date

from app.errors import ConflictError, NotFoundError
from app.schemas.fund import FundRead
from app.schemas.position import PositionRead
from app.schemas.price import PriceRead
from app.schemas.security import SecurityRead


class InMemoryStore:
    def __init__(self) -> None:
        self._securities: dict[str, SecurityRead] = {}
        self._funds: dict[str, FundRead] = {}
        self._positions: dict[tuple[str, str, date], PositionRead] = {}
        self._prices: dict[tuple[str, date], PriceRead] = {}

    # Securities

    def get_security(self, symbol: str) -> SecurityRead:
        security = self._securities.get(symbol)
        if security is None:
            raise NotFoundError(f"Security {symbol} not found")
        return security

    def list_securities(self) -> list[SecurityRead]:
        return sorted(self._securities.values(), key=lambda security: security.symbol)

    def add_security(self, security: SecurityRead) -> None:
        if security.symbol in self._securities:
            raise ConflictError(f"Security {security.symbol} already exists")
        self._securities[security.symbol] = security

    # Funds

    def get_fund(self, code: str) -> FundRead:
        fund = self._funds.get(code)
        if fund is None:
            raise NotFoundError(f"Fund {code} not found")
        return fund

    def list_funds(self) -> list[FundRead]:
        return sorted(self._funds.values(), key=lambda fund: fund.code)

    def add_fund(self, fund: FundRead) -> None:
        if fund.code in self._funds:
            raise ConflictError(f"Fund {fund.code} already exists")
        self._funds[fund.code] = fund

    # Positions

    def list_positions(self, fund_code: str, as_of_date: date | None) -> list[PositionRead]:
        self.get_fund(fund_code)
        positions = [
            position
            for position in self._positions.values()
            if position.fund_code == fund_code
            and (as_of_date is None or position.as_of_date == as_of_date)
        ]
        return sorted(positions, key=lambda position: (position.as_of_date, position.symbol))

    def add_position(self, position: PositionRead) -> None:
        self.get_fund(position.fund_code)
        self.get_security(position.symbol)
        key = (position.fund_code, position.symbol, position.as_of_date)
        if key in self._positions:
            raise ConflictError(
                f"Fund {position.fund_code} already has a position in {position.symbol} "
                f"on {position.as_of_date}"
            )
        self._positions[key] = position

    # Prices

    def list_prices(self, symbol: str) -> list[PriceRead]:
        self.get_security(symbol)
        prices = [price for price in self._prices.values() if price.symbol == symbol]
        return sorted(prices, key=lambda price: price.price_date)

    def add_price(self, price: PriceRead) -> None:
        self.get_security(price.symbol)
        key = (price.symbol, price.price_date)
        if key in self._prices:
            raise ConflictError(f"{price.symbol} already has a price on {price.price_date}")
        self._prices[key] = price
