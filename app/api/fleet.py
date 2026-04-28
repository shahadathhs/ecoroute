"""
Fleet Management API Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import get_current_user, require_manager
from app.core.response import ResponseBuilder
from app.db.session import get_db
from app.models.fleet import FleetUnitStatus, VehicleType
from app.models.user import User
from app.schemas.fleet import (
    FleetUnitData,
    FleetUnitCreate,
    FleetUnitUpdate,
    DriverAssignmentRequest,
    FleetDiagnostics,
    FleetUnitResponse,
    FleetDiagnosticsResponse,
)
from app.services.fleet import FleetService

router = APIRouter(
    tags=["Fleet Management"],
    responses={
        200: {"description": "Successful response"},
        403: {"description": "Forbidden - Insufficient permissions"},
    },
)


@router.get(
    "/v1/fleet",
    response_model=FleetUnitResponse,
    summary="List Fleet Units",
    description="List all fleet units in the organization with pagination and filters.",
)
async def get_fleet_units(
    current_user: Annotated[User, Depends(require_manager)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: FleetUnitStatus | None = Query(None, alias="status", description="Filter by status"),
    vehicle_type: VehicleType | None = Query(None, alias="type", description="Filter by vehicle type"),
    db: AsyncSession = Depends(get_db),
):
    """
    List Fleet Units Endpoint

    Returns a paginated list of fleet units in the organization.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    skip = (page - 1) * page_size

    fleet_units = await FleetService.get_fleet_units(
        organization_id=current_user.organization_id,
        db=db,
        skip=skip,
        limit=page_size,
        status=status_filter,
        vehicle_type=vehicle_type,
    )

    # Convert to FleetUnitData
    fleet_units_data = [
        FleetUnitData(
            id=unit.id,
            unit_id=unit.unit_id,
            organization_id=unit.organization_id,
            type=unit.type,
            battery_health=unit.battery_health,
            fuel_level=unit.fuel_level,
            last_maintenance=unit.last_maintenance,
            current_driver_id=unit.current_driver_id,
            status=unit.status,
            created_at=unit.created_at,
            updated_at=unit.updated_at,
        )
        for unit in fleet_units
    ]

    # TODO: Implement proper count query
    total = len(fleet_units_data)

    return ResponseBuilder.paginated(
        data=fleet_units_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Fleet units retrieved successfully",
    )


@router.post(
    "/v1/fleet",
    response_model=FleetUnitResponse,
    summary="Create Fleet Unit",
    description="Add a new vehicle to the fleet.",
)
async def create_fleet_unit(
    unit_data: FleetUnitCreate,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create Fleet Unit Endpoint

    Adds a new vehicle to the organization's fleet.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    fleet_unit = await FleetService.create_fleet_unit(
        unit_data=unit_data,
        organization_id=current_user.organization_id,
        db=db,
    )

    fleet_unit_data = FleetUnitData(
        id=fleet_unit.id,
        unit_id=fleet_unit.unit_id,
        organization_id=fleet_unit.organization_id,
        type=fleet_unit.type,
        battery_health=fleet_unit.battery_health,
        fuel_level=fleet_unit.fuel_level,
        last_maintenance=fleet_unit.last_maintenance,
        current_driver_id=fleet_unit.current_driver_id,
        status=fleet_unit.status,
        created_at=fleet_unit.created_at,
        updated_at=fleet_unit.updated_at,
    )

    return ResponseBuilder.success(
        data=fleet_unit_data,
        message="Fleet unit created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/v1/fleet/{unit_id}",
    response_model=FleetUnitResponse,
    summary="Get Fleet Unit by ID",
    description="Get detailed information about a specific fleet unit.",
)
async def get_fleet_unit(
    unit_id: str,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get Fleet Unit Endpoint

    Returns detailed information about a specific fleet unit.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)

    if not fleet_unit or fleet_unit.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Fleet unit not found",
            details={"unit_id": unit_id},
        )

    fleet_unit_data = FleetUnitData(
        id=fleet_unit.id,
        unit_id=fleet_unit.unit_id,
        organization_id=fleet_unit.organization_id,
        type=fleet_unit.type,
        battery_health=fleet_unit.battery_health,
        fuel_level=fleet_unit.fuel_level,
        last_maintenance=fleet_unit.last_maintenance,
        current_driver_id=fleet_unit.current_driver_id,
        status=fleet_unit.status,
        created_at=fleet_unit.created_at,
        updated_at=fleet_unit.updated_at,
    )

    return ResponseBuilder.success(
        data=fleet_unit_data,
        message="Fleet unit retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/v1/fleet/{unit_id}",
    response_model=FleetUnitResponse,
    summary="Update Fleet Unit",
    description="Update fleet unit information.",
)
async def update_fleet_unit(
    unit_id: str,
    unit_data: FleetUnitUpdate,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update Fleet Unit Endpoint

    Updates information for an existing fleet unit.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)

    if not fleet_unit or fleet_unit.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Fleet unit not found",
            details={"unit_id": unit_id},
        )

    updated_unit = await FleetService.update_fleet_unit(unit_id, unit_data, db)

    fleet_unit_data = FleetUnitData(
        id=updated_unit.id,
        unit_id=updated_unit.unit_id,
        organization_id=updated_unit.organization_id,
        type=updated_unit.type,
        battery_health=updated_unit.battery_health,
        fuel_level=updated_unit.fuel_level,
        last_maintenance=updated_unit.last_maintenance,
        current_driver_id=updated_unit.current_driver_id,
        status=updated_unit.status,
        created_at=updated_unit.created_at,
        updated_at=updated_unit.updated_at,
    )

    return ResponseBuilder.success(
        data=fleet_unit_data,
        message="Fleet unit updated successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/v1/fleet/{unit_id}/diagnostics",
    response_model=FleetDiagnosticsResponse,
    summary="Get Fleet Unit Diagnostics",
    description="Get health metrics and diagnostics for a fleet unit.",
)
async def get_fleet_diagnostics(
    unit_id: str,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get Fleet Diagnostics Endpoint

    Returns detailed diagnostics including battery health, fuel level,
    maintenance status, and driver assignment.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)

    if not fleet_unit or fleet_unit.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Fleet unit not found",
            details={"unit_id": unit_id},
        )

    diagnostics = await FleetService.get_fleet_diagnostics(unit_id, db)

    diagnostics_data = FleetDiagnostics(
        unit_id=diagnostics["unit_id"],
        battery_health=diagnostics["battery_health"],
        fuel_level=diagnostics["fuel_level"],
        status=diagnostics["status"],
        last_maintenance=diagnostics["last_maintenance"],
        days_since_maintenance=diagnostics["days_since_maintenance"],
        needs_maintenance=diagnostics["needs_maintenance"],
        current_driver=diagnostics["current_driver"],
    )

    return ResponseBuilder.success(
        data=diagnostics_data,
        message="Fleet diagnostics retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/v1/fleet/{unit_id}/assign",
    response_model=FleetUnitResponse,
    summary="Assign Driver to Fleet Unit",
    description="Assign a driver to a vehicle.",
)
async def assign_driver(
    unit_id: str,
    assignment_data: DriverAssignmentRequest,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Assign Driver Endpoint

    Assigns a driver to a fleet unit.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)

    if not fleet_unit or fleet_unit.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Fleet unit not found",
            details={"unit_id": unit_id},
        )

    updated_unit = await FleetService.assign_driver(
        unit_id=unit_id,
        driver_id=assignment_data.driver_id,
        db=db,
    )

    fleet_unit_data = FleetUnitData(
        id=updated_unit.id,
        unit_id=updated_unit.unit_id,
        organization_id=updated_unit.organization_id,
        type=updated_unit.type,
        battery_health=updated_unit.battery_health,
        fuel_level=updated_unit.fuel_level,
        last_maintenance=updated_unit.last_maintenance,
        current_driver_id=updated_unit.current_driver_id,
        status=updated_unit.status,
        created_at=updated_unit.created_at,
        updated_at=updated_unit.updated_at,
    )

    return ResponseBuilder.success(
        data=fleet_unit_data,
        message="Driver assigned successfully",
        status_code=status.HTTP_200_OK,
    )
