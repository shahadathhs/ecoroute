"""
Health Check Routes
"""

from fastapi import APIRouter

from app.schemas.health import HealthResponse, LivenessResponse, ReadinessResponse
from app.services.health import HealthService

router = APIRouter(tags=["Health"])
service = HealthService()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current status of the application.
    """
    return service.get_health_status()


@router.get("/health/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    """
    Liveness probe - checks if the container is alive.
    """
    return service.get_liveness()


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    """
    Readiness probe - checks if the container is ready to serve traffic.
    """
    return await service.get_readiness()
