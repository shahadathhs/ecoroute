"""
Database Session Management
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=0,
    echo=settings.debug,
    future=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables if needed)."""
    # Import all models here to ensure they're registered
    from app.models import base  # noqa

    async with engine.begin() as conn:
        # Use Alembic for migrations in production
        # This is only for development
        if settings.is_dev:
            await conn.run_sync(base.Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
