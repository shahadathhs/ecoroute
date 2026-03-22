"""
Root API Routes
"""
from fastapi import APIRouter

from app.schemas.root import PingResponse, RootResponse
from app.services.root import RootService

router = APIRouter(tags=["Root"])
service = RootService()


@router.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    """
    Root endpoint.

    Provides basic information about the API and documentation links.
    """
    return service.get_root_info()


@router.get("/ping", response_model=PingResponse)
async def ping() -> PingResponse:
    """
    Simple ping endpoint for connectivity check.
    """
    return service.ping()
