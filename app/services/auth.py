"""
Authentication Service

Handles user authentication, token generation, and user session management.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.errors import NotFoundException, UnauthorizedException
from app.core.response import ResponseBuilder
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse


class AuthService:
    """Authentication service for user login and token management."""

    @staticmethod
    async def authenticate_user(
        email: str, password: str, db: AsyncSession
    ) -> User | None:
        """Authenticate user with email and password.

        Args:
            email: User email
            password: User password
            db: Database session

        Returns:
            User if authenticated, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    async def login(
        email: str, password: str, db: AsyncSession
    ) -> TokenResponse:
        """Authenticate user and generate tokens.

        Args:
            email: User email
            password: User password
            db: Database session

        Returns:
            Token response with access and refresh tokens

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        user = await AuthService.authenticate_user(email, password, db)

        if not user:
            raise UnauthorizedException(
                message="Invalid email or password",
                details={"email": email}
            )

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Generate tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "organization_id": str(user.organization_id) if user.organization_id else None,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes in seconds
        )

    @staticmethod
    async def refresh_token(
        refresh_token: str, db: AsyncSession
    ) -> TokenResponse:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token
            db: Database session

        Returns:
            New token response

        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise UnauthorizedException(
                    message="Invalid token type",
                    details={"expected": "refresh", "got": payload.get("type")}
                )

            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException(
                    message="Invalid token payload",
                )

            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                raise UnauthorizedException(
                    message="User not found or inactive",
                )

            # Generate new tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "organization_id": str(user.organization_id) if user.organization_id else None,
            }

            access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=30 * 60,
            )

        except ValueError as e:
            raise UnauthorizedException(
                message="Invalid refresh token",
                details={"error": str(e)}
            )

    @staticmethod
    async def get_current_user_from_token(
        token: str, db: AsyncSession
    ) -> User:
        """Get user from JWT token.

        Args:
            token: JWT access token
            db: Database session

        Returns:
            User object

        Raises:
            UnauthorizedException: If token is invalid or user not found
        """
        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                raise UnauthorizedException(
                    message="Invalid token type",
                )

            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException(
                    message="Invalid token payload",
                )

            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundException(
                    message="User not found",
                    details={"user_id": user_id}
                )

            if not user.is_active:
                raise UnauthorizedException(
                    message="User account is inactive",
                )

            return user

        except ValueError as e:
            raise UnauthorizedException(
                message="Invalid token",
                details={"error": str(e)}
            )

    @staticmethod
    async def get_current_active_user(
        current_user: User
    ) -> User:
        """Check if user is active.

        Args:
            current_user: Current user from token

        Returns:
            User if active

        Raises:
            UnauthorizedException: If user is not active
        """
        if not current_user.is_active:
            raise UnauthorizedException(
                message="User account is inactive",
            )

        return current_user
