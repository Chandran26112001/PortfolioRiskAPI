"""Application entry point: creates the FastAPI app and registers the routers."""

from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="Portfolio Risk API",
    description="Fund valuation, sector exposure and historical VaR/Expected Shortfall.",
)

app.include_router(health.router)
