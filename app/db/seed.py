"""
Database Seed Data

Creates initial data for the application including a default superadmin user and organization.
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Organization, User, UserRole, SubscriptionTier
from app.core.security import hash_password
from app.core.config import settings
from app.core.logger import logger


async def seed_database(db: AsyncSession) -> None:
    """Seed the database with initial data.

    Creates:
    - Default organization if none exists
    - Default superadmin user if the configured email doesn't exist

    Args:
        db: Database session
    """
    from sqlalchemy import select, func

    # Check if superadmin with configured email already exists
    result = await db.execute(
        select(func.count(User.id)).where(User.email == settings.superadmin_email)
    )
    superadmin_exists = result.scalar() > 0

    if superadmin_exists:
        logger.info(f"Superadmin user ({settings.superadmin_email}) already exists - skipping seed")
        return

    logger.info("Seeding database with initial data...")

    # Check if we need to create an organization or find existing one
    result = await db.execute(select(func.count(Organization.id)))
    org_count = result.scalar()

    if org_count > 0:
        # Use existing organization
        result = await db.execute(
            select(Organization).limit(1)
        )
        organization = result.scalar_one()
        logger.info(f"Using existing organization: {organization.name}")
    else:
        # Create default organization
        organization = Organization(
            id=str(uuid.uuid4()),
            name="EcoRoute Organization",
            subscription_tier=SubscriptionTier.ENTERPRISE,
            settings={
                "timezone": "UTC",
                "currency": "USD",
            },
            is_active=True,
        )
        db.add(organization)
        await db.flush()

    # Create default superadmin user
    superadmin = User(
        id=str(uuid.uuid4()),
        email=settings.superadmin_email,
        hashed_password=hash_password(settings.superadmin_password),
        full_name="Super Administrator",
        role=UserRole.SUPER_ADMIN,
        organization_id=organization.id,
        is_active=True,
    )
    db.add(superadmin)
    await db.commit()

    logger.info(f"✓ Database seeded successfully!")
    logger.info(f"  Organization: {organization.name} (ID: {organization.id})")
    logger.info(f"  Superadmin email: {settings.superadmin_email}")
    logger.info(f"  Superadmin password: {settings.superadmin_password}")
    logger.warning(f"  ⚠️  Please change the default password after first login!")
    logger.warning(f"  ⚠️  Login at: POST /v1/auth/login")
