"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ResponseBuilder
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    TokenResponseSchema,
    RefreshTokenRequest,
)
from app.schemas.user import UserData
from app.services.auth import AuthService

router = APIRouter(
    tags=["Authentication"],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 200,
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "access_token": "eyJ...",
                            "refresh_token": "eyJ...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 401,
                        "success": False,
                        "message": "Invalid email or password",
                        "data": None,
                    }
                }
            },
        },
    },
)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    user = await AuthService.get_current_user_from_token(token, db)
    return await AuthService.get_current_active_user(user)

router = APIRouter(
    tags=["Authentication"],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 200,
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "access_token": "eyJ...",
                            "refresh_token": "eyJ...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 401,
                        "success": False,
                        "message": "Invalid email or password",
                        "data": None,
                    }
                }
            },
        },
    },
)

security = HTTPBearer()


@router.post(
    "/v1/auth/login",
    response_model=TokenResponseSchema,
    summary="User Login",
    description="Authenticate user with email and password. Returns JWT access and refresh tokens.",
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login Endpoint

    Authenticates a user with their email and password credentials.

    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"email": "user@example.com", "password": "password123"}'
    ```

    **Example Response (Success):**
    ```json
    {
      "status_code": 200,
      "success": true,
      "message": "Login successful",
      "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 1800
      }
    }
    ```

    **Use Cases:**
    - Initial user authentication
    - Obtaining tokens for API access
    - Setting up authenticated sessions

    **Error Responses:**
    - `401`: Invalid email or password
    - `401`: User account is inactive
    """
    token_response = await AuthService.login(login_data.email, login_data.password, db)

    return ResponseBuilder.success(
        data=token_response,
        message="Login successful",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/v1/auth/refresh",
    response_model=TokenResponseSchema,
    summary="Refresh Access Token",
    description="Refresh access token using a valid refresh token.",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh Token Endpoint

    Generates a new access token using a valid refresh token.

    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/v1/auth/refresh \\
      -H "Content-Type: application/json" \\
      -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
    ```

    **Example Response (Success):**
    ```json
    {
      "status_code": 200,
      "success": true,
      "message": "Token refreshed successfully",
      "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 1800
      }
    }
    ```

    **Use Cases:**
    - Renewing expired access tokens
    - Maintaining user sessions without re-authentication
    - Seamless token rotation

    **Error Responses:**
    - `401`: Invalid or expired refresh token
    - `401`: User account is inactive
    """
    token_response = await AuthService.refresh_token(refresh_data.refresh_token, db)

    return ResponseBuilder.success(
        data=token_response,
        message="Token refreshed successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/v1/auth/me",
    summary="Get Current User",
    description="Get information about the currently authenticated user.",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get Current User Endpoint

    Returns the profile information of the authenticated user.

    **Example Request:**
    ```bash
    curl -X GET http://localhost:8000/v1/auth/me \\
      -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
    ```

    **Example Response (Success):**
    ```json
    {
      "status_code": 200,
      "success": true,
      "message": "User profile retrieved successfully",
      "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "LOGISTICS_MANAGER",
        "organization_id": "550e8400-e29b-41d4-a716-446655440001",
        "is_active": true,
        "last_login": "2026-04-28T10:30:00Z",
        "created_at": "2026-04-01T08:00:00Z",
        "updated_at": "2026-04-28T10:30:00Z"
      }
    }
    ```

    **Use Cases:**
    - Verifying authentication status
    - Getting user profile information
    - Checking user permissions/role

    **Error Responses:**
    - `401`: Invalid or expired access token
    - `401`: User account is inactive
    """
    # Convert User to UserData
    user_data = UserData(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=current_user.organization_id,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

    return ResponseBuilder.success(
        data=user_data,
        message="User profile retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/v1/auth/logout",
    summary="Logout User",
    description="Logout the current user (invalidate tokens on client).",
)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout Endpoint

    Logs out the current user. Note: JWT tokens are stateless, so this endpoint
    primarily signals the client to discard tokens. For true token invalidation,
    implement a token blacklist or use short-lived tokens with refresh token rotation.

    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/v1/auth/logout \\
      -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
    ```

    **Example Response (Success):**
    ```json
    {
      "status_code": 200,
      "success": true,
      "message": "Logout successful",
      "data": null
    }
    ```

    **Use Cases:**
    - User-initiated logout
    - Clearing client-side tokens
    - Ending user sessions

    **Implementation Notes:**
    - Client should discard both access and refresh tokens
    - For server-side token invalidation, implement token blacklist
    - Consider implementing refresh token rotation for better security
    """
    return ResponseBuilder.success(
        data=None,
        message="Logout successful",
        status_code=status.HTTP_200_OK,
    )
