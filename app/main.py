"""Application entry point: creates the FastAPI app and registers the routers."""

from fastapi import FastAPI

from app.error_handlers import register_error_handlers
from app.routers import funds, health, positions, prices, securities

app = FastAPI(
    title="Portfolio Risk API",
    description="Fund valuation, sector exposure and historical VaR/Expected Shortfall.",
)

register_error_handlers(app)

app.include_router(health.router)
app.include_router(securities.router)
app.include_router(prices.router)
app.include_router(funds.router)
app.include_router(positions.router)
