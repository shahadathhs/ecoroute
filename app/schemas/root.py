"""
Root API Schemas
"""

from pydantic import BaseModel
from app.schemas.base import DataResponse


class RootData(BaseModel):
    """Root endpoint data."""

    app_name: str
    version: str
    description: str
    docs_url: str
    redoc_url: str
    api_prefix: str


class PingData(BaseModel):
    """Ping endpoint data."""

    ping: str


# Response types
RootResponse = DataResponse[RootData]
PingResponse = DataResponse[PingData]
