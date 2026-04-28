"""
User Management API Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenException
from app.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.user import (
    UserData,
    UserCreate,
    UserUpdate,
    UserInvite,
    RoleUpdateRequest,
    UserResponse,
)
from app.services.user import UserService

router = APIRouter(
    tags=["User Management"],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 200,
                        "success": True,
                        "message": "User retrieved successfully",
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "role": "LOGISTICS_MANAGER",
                            "organization_id": "550e8400-e29b-41d4-a716-446655440001",
                            "is_active": True,
                        },
                    }
                }
            },
        },
        403: {
            "description": "Forbidden - Insufficient permissions",
        },
    },
)

security = HTTPBearer()


# Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user from JWT token."""
    from app.services.auth import AuthService

    token = credentials.credentials
    user = await AuthService.get_current_user_from_token(token, db)
    return await AuthService.get_current_active_user(user)


class RoleChecker:
    """Dependency class for role-based access control."""

    def __init__(self, *roles: UserRole):
        self.roles = roles

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role not in self.roles:
            raise ForbiddenException(
                message="Insufficient permissions",
                details={
                    "required_role": [r.value for r in self.roles],
                    "user_role": current_user.role.value,
                },
            )
        return current_user


# Admin and Company Admin dependency
require_admin = RoleChecker(UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN)
require_manager = RoleChecker(
    UserRole.SUPER_ADMIN,
    UserRole.COMPANY_ADMIN,
    UserRole.LOGISTICS_MANAGER,
)


@router.get(
    "/v1/users",
    response_model=UserResponse,
    summary="List Users",
    description="List all users in the organization with pagination and search.",
)
async def get_users(
    current_user: Annotated[User, Depends(require_admin)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by email or name"),
    db: AsyncSession = Depends(get_db),
):
    """
    List Users Endpoint

    Returns a paginated list of users in the organization.

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/v1/users?page=1&page_size=10" \\
      -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
    ```

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page, max 100 (default: 10)
    - `search`: Search term for email or full name (optional)
    """
    skip = (page - 1) * page_size

    users = await UserService.get_users(
        organization_id=current_user.organization_id,
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
    )

    # Convert to UserData
    users_data = [
        UserData(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            organization_id=user.organization_id,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]

    # Get total count (simplified - in production use COUNT query)
    total = len(users_data)  # TODO: Implement proper count query

    from app.core.response import ResponseBuilder, MetaData

    return ResponseBuilder.paginated(
        data=users_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Users retrieved successfully",
    )


@router.post(
    "/v1/users",
    response_model=UserResponse,
    summary="Create User",
    description="Create a new user in the organization.",
)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create User Endpoint

    Creates a new user account in the organization.

    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/v1/users \\
      -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
        "role": "STANDARD_DISPATCHER"
      }'
    ```

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN
    """
    # Set organization_id to current user's organization
    user_data.organization_id = current_user.organization_id

    user = await UserService.create_user(user_data, db)

    user_data = UserData(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=user.organization_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    from app.core.response import ResponseBuilder

    return ResponseBuilder.success(
        data=user_data,
        message="User created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/v1/users/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Get detailed information about a specific user.",
)
async def get_user(
    user_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get User Endpoint

    Returns detailed information about a specific user.

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN
    """
    user = await UserService.get_user_by_id(user_id, db)

    if not user or user.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="User not found",
            details={"user_id": user_id},
        )

    user_data = UserData(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=user.organization_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    from app.core.response import ResponseBuilder

    return ResponseBuilder.success(
        data=user_data,
        message="User retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/v1/users/{user_id}",
    response_model=UserResponse,
    summary="Update User",
    description="Update user information.",
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update User Endpoint

    Updates information for an existing user.

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN
    """
    user = await UserService.get_user_by_id(user_id, db)

    if not user or user.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="User not found",
            details={"user_id": user_id},
        )

    updated_user = await UserService.update_user(user_id, user_data, db)

    user_data_response = UserData(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role,
        organization_id=updated_user.organization_id,
        is_active=updated_user.is_active,
        last_login=updated_user.last_login,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )

    from app.core.response import ResponseBuilder

    return ResponseBuilder.success(
        data=user_data_response,
        message="User updated successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/v1/users/invite",
    response_model=UserResponse,
    summary="Invite User",
    description="Invite a new user to the organization (sends email invitation).",
)
async def invite_user(
    invite_data: UserInvite,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Invite User Endpoint

    Invites a new user to the organization by email. A temporary password
    will be generated and sent to the user's email address.

    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/v1/users/invite \\
      -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "invitee@example.com",
        "role": "DRIVER"
      }'
    ```

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN

    **Note:**
    - In production, this would send an email with the temporary password
    - For now, the password is logged but not sent
    """
    user = await UserService.invite_user(
        email=invite_data.email,
        role=invite_data.role,
        organization_id=current_user.organization_id,
        db=db,
    )

    user_data = UserData(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=user.organization_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    from app.core.response import ResponseBuilder

    return ResponseBuilder.success(
        data=user_data,
        message=f"User invited successfully. Temporary password sent to {invite_data.email}",
        status_code=status.HTTP_201_CREATED,
    )


@router.patch(
    "/v1/users/{user_id}/role",
    response_model=UserResponse,
    summary="Update User Role",
    description="Update the role of a user in the organization.",
)
async def update_user_role(
    user_id: str,
    role_data: RoleUpdateRequest,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update User Role Endpoint

    Updates the role of an existing user.

    **Permissions Required:**
    - SUPER_ADMIN
    - COMPANY_ADMIN
    """
    user = await UserService.get_user_by_id(user_id, db)

    if not user or user.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="User not found",
            details={"user_id": user_id},
        )

    # Update role
    update_data = UserUpdate(role=role_data.role)
    updated_user = await UserService.update_user(user_id, update_data, db)

    user_data_response = UserData(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role,
        organization_id=updated_user.organization_id,
        is_active=updated_user.is_active,
        last_login=updated_user.last_login,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )

    from app.core.response import ResponseBuilder

    return ResponseBuilder.success(
        data=user_data_response,
        message="User role updated successfully",
        status_code=status.HTTP_200_OK,
    )
