"""
Main Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logger import setup_logger, logger
from app.core.errors import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.api import root, health, docs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database
    from app.db.session import init_db

    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    from app.db.session import close_db

    await close_db()
    logger.info(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="""
## 🌍 EcoRoute Atlas

AI-driven backend system for global supply chain management, sustainability tracking, and regulatory compliance.

### 🎯 Key Features

- **Identity & Access Management (IAM)**: Advanced RBAC with multi-tenancy support
- **Atlas AI**: LLM-powered regulatory assistant using RAG for real-time legal audits
- **Sustainability Tracking**: Automated CO2 footprint calculation and optimization
- **Fleet Monitoring**: Real-time IoT data ingestion for proactive maintenance

### 📚 Documentation

- **Interactive Docs**: Try out API endpoints directly from your browser
- **Multiple Views**: Choose between RapiDoc (recommended), Swagger UI, or ReDoc
- **Full Schema**: Complete request/response schemas with validation

### 🔒 Authentication

This API uses JWT tokens for authentication. Include your token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### 📊 Response Format

All endpoints return JSON responses with the following structure:

```json
{{
  "data": {{...}},
  "message": "Success",
  "status": "success"
}}
```

### 🌐 Environment

- **Version**: {version}
- **Environment**: Development/Production
        """.format(version=settings.app_version),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.ecoroute.com",
                "description": "Production server"
            }
        ],
        tags=[
            {
                "name": "Root",
                "description": "Basic system endpoints for API information and health checks."
            },
            {
                "name": "Health",
                "description": "Health monitoring and system status endpoints."
            },
            {
                "name": "Documentation",
                "description": "Documentation viewers and API reference hubs."
            }
        ],
        contact={
            "name": "EcoRoute Team",
            "url": "https://github.com/shahadathhs/ecoroute",
            "email": "support@ecoroute.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        }
    )

    # Setup logger
    setup_logger()

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, general_exception_handler)  # type: ignore

    # Include routers
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(docs.router)

    logger.info("Application created successfully")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
