"""
User Service

Handles user management operations including creation, retrieval, and updates.
"""

import uuid
from typing import List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequestException, NotFoundException
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user management operations."""

    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
        """Create a new user.

        Args:
            user_data: User creation data
            db: Database session

        Returns:
            Created user

        Raises:
            BadRequestException: If email already exists
        """
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise BadRequestException(
                message="Email already registered",
                details={"email": user_data.email}
            )

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            organization_id=user_data.organization_id,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> User | None:
        """Get user by ID.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            User or None if not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
        """Get user by email.

        Args:
            email: User email
            db: Database session

        Returns:
            User or None if not found
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(
        organization_id: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None
    ) -> List[User]:
        """List users in an organization with pagination.

        Args:
            organization_id: Organization ID
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for email or full_name

        Returns:
            List of users
        """
        query = select(User).where(User.organization_id == organization_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_user(
        user_id: str, user_data: UserUpdate, db: AsyncSession
    ) -> User:
        """Update user.

        Args:
            user_id: User ID
            user_data: Update data
            db: Database session

        Returns:
            Updated user

        Raises:
            NotFoundException: If user not found
        """
        user = await UserService.get_user_by_id(user_id, db)
        if not user:
            raise NotFoundException(
                message="User not found",
                details={"user_id": user_id}
            )

        # Update fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete_user(user_id: str, db: AsyncSession) -> bool:
        """Soft delete user by setting is_active to False.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if deleted

        Raises:
            NotFoundException: If user not found
        """
        user = await UserService.get_user_by_id(user_id, db)
        if not user:
            raise NotFoundException(
                message="User not found",
                details={"user_id": user_id}
            )

        user.is_active = False
        await db.commit()

        return True

    @staticmethod
    async def invite_user(
        email: str,
        role: UserRole,
        organization_id: str,
        db: AsyncSession
    ) -> User:
        """Invite a new user (creates user with temporary password).

        Args:
            email: User email
            role: User role
            organization_id: Organization ID
            db: Database session

        Returns:
            Created user

        Raises:
            BadRequestException: If email already exists
        """
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == email)
        )
        if result.scalar_one_or_none():
            raise BadRequestException(
                message="Email already registered",
                details={"email": email}
            )

        # Generate temporary password
        temp_password = uuid.uuid4().hex[:16]

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password(temp_password),
            full_name=email.split("@")[0],  # Use email prefix as placeholder
            role=role,
            organization_id=organization_id,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # TODO: Send invitation email with temporary password

        return user
