"""
Health Check Routes
"""

from fastapi import APIRouter

from app.schemas.health import HealthResponse, LivenessResponse, ReadinessResponse
from app.services.health import HealthService

router = APIRouter(
    tags=["Health"],
    responses={
        200: {
            "description": "Healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2026-04-04T22:00:00Z"
                    }
                }
            }
        },
        503: {
            "description": "Service Unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "error": "Database connection failed"
                    }
                }
            }
        }
    }
)
service = HealthService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Complete Health Check",
    description="Returns the overall health status of the application including database and service dependencies. Use this endpoint for comprehensive health monitoring."
)
async def health_check() -> HealthResponse:
    """
    Complete Health Check

    Performs a comprehensive health check including:
    - Application status
    - Database connectivity
    - External service dependencies
    - System resource status

    **Example Request:**
    ```bash
    curl http://localhost:8000/health
    ```

    **Example Response (Healthy):**
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-04-04T22:00:00Z",
      "version": "1.0.0",
      "checks": {
        "database": "healthy",
        "redis": "healthy",
        "api": "healthy"
      }
    }
    ```

    **Use Cases:**
    - Monitoring dashboards
    - Alerting systems
    - Deployment health verification
    - Periodic health checks
    """
    return service.get_health_status()


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Liveness Probe",
    description="Kubernetes liveness probe - checks if the container is still running. Returns HTTP 200 if the container is alive. Does not check external dependencies."
)
async def liveness() -> LivenessResponse:
    """
    Liveness Probe

    Simple liveness check that confirms the API process is running.
    This endpoint is lightweight and does not check external dependencies.

    **Example Request:**
    ```bash
    curl http://localhost:8000/health/live
    ```

    **Example Response:**
    ```json
    {
      "status": "alive",
      "timestamp": "2026-04-04T22:00:00Z"
    }
    ```

    **Kubernetes Configuration:**
    ```yaml
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8000
      initialDelaySeconds: 3
      periodSeconds: 10
    ```
    """
    return service.get_liveness()


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description="Kubernetes readiness probe - checks if the container is ready to serve traffic. Verifies database and external service connections before returning healthy status."
)
async def readiness() -> ReadinessResponse:
    """
    Readiness Probe

    Comprehensive readiness check that verifies:
    - Application is running
    - Database is accessible
    - External services are available
    - Ready to accept traffic

    **Example Request:**
    ```bash
    curl http://localhost:8000/health/ready
    ```

    **Example Response (Ready):**
    ```json
    {
      "status": "ready",
      "timestamp": "2026-04-04T22:00:00Z",
      "checks": {
        "database": "connected",
        "redis": "connected"
      }
    }
    ```

    **Example Response (Not Ready):**
    ```json
    {
      "status": "not_ready",
      "timestamp": "2026-04-04T22:00:00Z",
      "checks": {
        "database": "disconnected"
      }
    }
    ```

    **Kubernetes Configuration:**
    ```yaml
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5
    ```
    """
    return await service.get_readiness()
