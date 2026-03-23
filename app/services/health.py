"""
Health Check Service
"""

from fastapi import status
from app.core.config import settings
from app.core.response import ResponseBuilder
from app.schemas.health import (
    HealthData,
    HealthResponse,
    LivenessData,
    LivenessResponse,
    ReadinessData,
    ReadinessResponse,
)


class HealthService:
    """Service for health check operations."""

    @staticmethod
    def get_health_status() -> HealthResponse:
        """
        Get application health status.

        Returns:
            HealthResponse: Health status information
        """
        return ResponseBuilder.success(
            data=HealthData(
                status="healthy",
                app_name=settings.app_name,
                version=settings.app_version,
                environment=settings.environment,
            ),
            message="Application is healthy",
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def get_liveness() -> LivenessResponse:
        """
        Get liveness status.

        Returns:
            LivenessResponse: Liveness status
        """
        return ResponseBuilder.success(
            data=LivenessData(status="alive"),
            message="Application is alive",
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    async def get_readiness() -> ReadinessResponse:
        """
        Get readiness status.

        Returns:
            ReadinessResponse: Readiness status
        """
        # Add database and other service checks here
        # For now, return ready
        return ResponseBuilder.success(
            data=ReadinessData(status="ready"),
            message="Application is ready",
            status_code=status.HTTP_200_OK,
        )
