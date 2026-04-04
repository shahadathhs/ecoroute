"""
Root API Routes
"""

from fastapi import APIRouter

from app.schemas.root import PingResponse, RootResponse
from app.services.root import RootService

router = APIRouter(
    tags=["Root"],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "app_name": "EcoRoute Atlas",
                        "version": "1.0.0",
                        "status": "running"
                    }
                }
            }
        }
    }
)
service = RootService()


@router.get(
    "/",
    response_model=RootResponse,
    summary="API Root Information",
    description="Returns basic information about the API including name, version, and available documentation links. Use this endpoint to verify the API is running and get quick access to documentation."
)
async def root() -> RootResponse:
    """
    API Root Endpoint

    Provides basic information about the EcoRoute Atlas API including:
    - Application name and version
    - Available documentation URLs
    - Current system status

    **Example Request:**
    ```bash
    curl http://localhost:8000/
    ```

    **Example Response:**
    ```json
    {
      "app_name": "EcoRoute Atlas",
      "version": "1.0.0",
      "description": "AI-driven supply chain management",
      "docs_url": "/docs",
      "redoc_url": "/redoc",
      "rapidoc_url": "/rapidoc"
    }
    ```
    """
    return service.get_root_info()


@router.get(
    "/ping",
    response_model=PingResponse,
    summary="Health Check Ping",
    description="Simple health check endpoint that returns 'pong'. Use this for basic connectivity testing and monitoring. This endpoint does not check database or other service dependencies."
)
async def ping() -> PingResponse:
    """
    Ping Endpoint

    A simple health check that returns 'pong' to confirm the API is responding.

    **Example Request:**
    ```bash
    curl http://localhost:8000/ping
    ```

    **Example Response:**
    ```json
    {
      "ping": "pong"
    }
    ```

    **Use Cases:**
    - Basic connectivity testing
    - Load balancer health checks
    - Monitoring systems
    - Quick API availability verification
    """
    return service.ping()
