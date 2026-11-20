"""Health check endpoint, called by load balancers and container platforms."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
async def get_health() -> HealthResponse:
    """Report that the process is up and able to serve requests."""
    return HealthResponse(status="ok")
