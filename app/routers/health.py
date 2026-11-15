"""Health check endpoint, called by load balancers and container platforms."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health", summary="Liveness check")
async def get_health() -> HealthResponse:
    """Report that the process is up and able to serve requests."""
    return HealthResponse(status="ok")
