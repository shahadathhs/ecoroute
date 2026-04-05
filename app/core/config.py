"""
Application Configuration Module
"""

from typing import List
from functools import lru_cache

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="EcoRoute Atlas", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    api_prefix: str = Field(default="/api", description="API prefix")

    # Server
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ecoroute",
        description="Database connection URL",
    )

    # Vector Database
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection: str = Field(
        default="atlas_intelligence", description="Qdrant collection name"
    )

    # Security
    secret_key: str = Field(default="change-me", description="Secret key for JWT")

    # CORS
    cors_origins: str | List[str] = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS allowed origins",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, list):
            return v

        # v is a string at this point
        if v.startswith("["):
            # JSON-like format: ["http://...", "http://..."]
            import json

            parsed: List[str] = json.loads(v)
            return parsed
        else:
            # Comma-separated format
            return [origin.strip() for origin in v.split(",")]

    @property
    def is_dev(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ("development", "dev")

    @property
    def is_prod(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ("production", "prod")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
