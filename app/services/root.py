"""
Root API Service
"""
from fastapi import status
from app.core.config import settings
from app.core.response import ResponseBuilder
from app.schemas.root import PingData, PingResponse, RootData, RootResponse


class RootService:
    """Service for root endpoint operations."""

    @staticmethod
    def get_root_info() -> RootResponse:
        """
        Get root endpoint information.

        Returns:
            RootResponse: Root information
        """
        return ResponseBuilder.success(
            data=RootData(
                app_name=settings.app_name,
                version=settings.app_version,
                description="AI-driven backend for global supply chain management",
                docs_url="/docs",
                redoc_url="/redoc",
                api_prefix=settings.api_prefix,
            ),
            message="Welcome to EcoRoute Atlas API",
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def ping() -> PingResponse:
        """
        Simple ping check.

        Returns:
            PingResponse: Ping response
        """
        return ResponseBuilder.success(
            data=PingData(ping="pong"),
            message="Pong successfully",
            status_code=status.HTTP_200_OK,
        )
