"""
Health Check Schemas
"""
from pydantic import BaseModel
from app.schemas.base import DataResponse


class HealthData(BaseModel):
    """Health check data."""

    status: str
    app_name: str
    version: str
    environment: str


class LivenessData(BaseModel):
    """Liveness probe data."""

    status: str


class ReadinessData(BaseModel):
    """Readiness probe data."""

    status: str


# Response types
HealthResponse = DataResponse[HealthData]
LivenessResponse = DataResponse[LivenessData]
ReadinessResponse = DataResponse[ReadinessData]
