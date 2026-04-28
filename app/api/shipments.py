"""
Shipment Management API Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import get_current_user, require_manager
from app.core.response import ResponseBuilder
from app.db.session import get_db
from app.models.shipment import ShipmentStatus
from app.models.user import User
from app.schemas.shipment import (
    ShipmentData,
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentEventCreate,
    ShipmentEventData,
    ShipmentResponse,
    ShipmentEventResponse,
    LocationUpdate,
)
from app.services.shipment import ShipmentService

router = APIRouter(
    tags=["Shipments"],
    responses={
        200: {"description": "Successful response"},
        403: {"description": "Forbidden - Insufficient permissions"},
    },
)


@router.get(
    "/v1/shipments",
    response_model=ShipmentResponse,
    summary="List Shipments",
    description="List all shipments in the organization with pagination and filters.",
)
async def get_shipments(
    current_user: Annotated[User, Depends(require_manager)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: ShipmentStatus | None = Query(None, alias="status", description="Filter by status"),
    search: str | None = Query(None, description="Search by tracking number or carrier"),
    db: AsyncSession = Depends(get_db),
):
    """
    List Shipments Endpoint

    Returns a paginated list of shipments in the organization.

    **Permissions Required:**
    - LOGISTICS_MANAGER
    - COMPLIANCE_OFFICER
    - SUSTAINABILITY_LEAD
    - STANDARD_DISPATCHER
    - DRIVER
    """
    skip = (page - 1) * page_size

    shipments = await ShipmentService.get_shipments(
        organization_id=current_user.organization_id,
        db=db,
        skip=skip,
        limit=page_size,
        status=status_filter,
        search=search,
    )

    # Convert to ShipmentData
    shipments_data = [
        ShipmentData(
            id=shipment.id,
            tracking_number=shipment.tracking_number,
            status=shipment.status,
            organization_id=shipment.organization_id,
            origin_city=shipment.origin_city,
            origin_code=shipment.origin_code,
            origin_coords=shipment.origin_coords,
            destination_city=shipment.destination_city,
            destination_code=shipment.destination_code,
            destination_coords=shipment.destination_coords,
            current_location=shipment.current_location,
            carrier=shipment.carrier,
            cargo_type=shipment.cargo_type,
            environmental_impact=shipment.environmental_impact,
            created_at=shipment.created_at,
            updated_at=shipment.updated_at,
        )
        for shipment in shipments
    ]

    # TODO: Implement proper count query
    total = len(shipments_data)

    return ResponseBuilder.paginated(
        data=shipments_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Shipments retrieved successfully",
    )


@router.post(
    "/v1/shipments",
    response_model=ShipmentResponse,
    summary="Create Shipment",
    description="Create a new shipment in the organization.",
)
async def create_shipment(
    shipment_data: ShipmentCreate,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create Shipment Endpoint

    Creates a new shipment with automatic tracking number generation.

    **Permissions Required:**
    - LOGISTICS_MANAGER
    - STANDARD_DISPATCHER
    """
    shipment = await ShipmentService.create_shipment(
        shipment_data=shipment_data,
        organization_id=current_user.organization_id,
        db=db,
    )

    shipment_data_response = ShipmentData(
        id=shipment.id,
        tracking_number=shipment.tracking_number,
        status=shipment.status,
        organization_id=shipment.organization_id,
        origin_city=shipment.origin_city,
        origin_code=shipment.origin_code,
        origin_coords=shipment.origin_coords,
        destination_city=shipment.destination_city,
        destination_code=shipment.destination_code,
        destination_coords=shipment.destination_coords,
        current_location=shipment.current_location,
        carrier=shipment.carrier,
        cargo_type=shipment.cargo_type,
        environmental_impact=shipment.environmental_impact,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )

    return ResponseBuilder.success(
        data=shipment_data_response,
        message="Shipment created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/v1/shipments/{shipment_id}",
    response_model=ShipmentResponse,
    summary="Get Shipment by ID",
    description="Get detailed information about a specific shipment.",
)
async def get_shipment(
    shipment_id: str,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get Shipment Endpoint

    Returns detailed information about a specific shipment.

    **Permissions Required:**
    - LOGISTICS_MANAGER+
    """
    shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)

    if not shipment or shipment.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Shipment not found",
            details={"shipment_id": shipment_id},
        )

    shipment_data = ShipmentData(
        id=shipment.id,
        tracking_number=shipment.tracking_number,
        status=shipment.status,
        organization_id=shipment.organization_id,
        origin_city=shipment.origin_city,
        origin_code=shipment.origin_code,
        origin_coords=shipment.origin_coords,
        destination_city=shipment.destination_city,
        destination_code=shipment.destination_code,
        destination_coords=shipment.destination_coords,
        current_location=shipment.current_location,
        carrier=shipment.carrier,
        cargo_type=shipment.cargo_type,
        environmental_impact=shipment.environmental_impact,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )

    return ResponseBuilder.success(
        data=shipment_data,
        message="Shipment retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/v1/shipments/{shipment_id}",
    response_model=ShipmentResponse,
    summary="Update Shipment",
    description="Update shipment information.",
)
async def update_shipment(
    shipment_id: str,
    shipment_data: ShipmentUpdate,
    current_user: Annotated[User, Depends(require_manager)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update Shipment Endpoint

    Updates information for an existing shipment.

    **Permissions Required:**
    - STANDARD_DISPATCHER+
    """
    shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)

    if not shipment or shipment.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Shipment not found",
            details={"shipment_id": shipment_id},
        )

    # Update basic fields
    if shipment_data.carrier:
        shipment.carrier = shipment_data.carrier
    if shipment_data.cargo_type:
        shipment.cargo_type = shipment_data.cargo_type

    # Update status if provided
    if shipment_data.status:
        shipment = await ShipmentService.update_shipment_status(
            shipment_id, shipment_data.status, db
        )
    else:
        await db.commit()
        await db.refresh(shipment)

    shipment_data_response = ShipmentData(
        id=shipment.id,
        tracking_number=shipment.tracking_number,
        status=shipment.status,
        organization_id=shipment.organization_id,
        origin_city=shipment.origin_city,
        origin_code=shipment.origin_code,
        origin_coords=shipment.origin_coords,
        destination_city=shipment.destination_city,
        destination_code=shipment.destination_code,
        destination_coords=shipment.destination_coords,
        current_location=shipment.current_location,
        carrier=shipment.carrier,
        cargo_type=shipment.cargo_type,
        environmental_impact=shipment.environmental_impact,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )

    return ResponseBuilder.success(
        data=shipment_data_response,
        message="Shipment updated successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/v1/shipments/{shipment_id}/events",
    response_model=ShipmentEventResponse,
    summary="Add Shipment Event",
    description="Log an event for a shipment (pickup, delivery, etc.).",
)
async def add_shipment_event(
    shipment_id: str,
    event_data: ShipmentEventCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Add Shipment Event Endpoint

    Logs a shipment event such as pickup, customs clearance, or delivery.

    **Permissions Required:**
    - DRIVER (for assigned shipments)
    - STANDARD_DISPATCHER+
    """
    shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)

    if not shipment or shipment.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Shipment not found",
            details={"shipment_id": shipment_id},
        )

    event = await ShipmentService.add_shipment_event(
        shipment_id=shipment_id,
        event_data=event_data,
        created_by=current_user.id,
        db=db,
    )

    event_data_response = ShipmentEventData(
        id=event.id,
        shipment_id=event.shipment_id,
        event_type=event.event_type,
        location=event.location,
        notes=event.notes,
        created_by=event.created_by,
        created_at=event.created_at,
    )

    return ResponseBuilder.success(
        data=event_data_response,
        message="Shipment event logged successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.patch(
    "/v1/shipments/{shipment_id}/location",
    response_model=ShipmentResponse,
    summary="Update Shipment Location",
    description="Update the current GPS location of a shipment.",
)
async def update_shipment_location(
    shipment_id: str,
    location_data: LocationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update Shipment Location Endpoint

    Updates the current GPS location of a shipment. Used by drivers and IoT devices.

    **Permissions Required:**
    - DRIVER (for assigned shipments)
    - STANDARD_DISPATCHER+
    """
    shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)

    if not shipment or shipment.organization_id != current_user.organization_id:
        from app.core.errors import NotFoundException
        raise NotFoundException(
            message="Shipment not found",
            details={"shipment_id": shipment_id},
        )

    updated_shipment = await ShipmentService.update_location(
        shipment_id=shipment_id,
        location=location_data.location,
        db=db,
    )

    shipment_data = ShipmentData(
        id=updated_shipment.id,
        tracking_number=updated_shipment.tracking_number,
        status=updated_shipment.status,
        organization_id=updated_shipment.organization_id,
        origin_city=updated_shipment.origin_city,
        origin_code=updated_shipment.origin_code,
        origin_coords=updated_shipment.origin_coords,
        destination_city=updated_shipment.destination_city,
        destination_code=updated_shipment.destination_code,
        destination_coords=updated_shipment.destination_coords,
        current_location=updated_shipment.current_location,
        carrier=updated_shipment.carrier,
        cargo_type=updated_shipment.cargo_type,
        environmental_impact=updated_shipment.environmental_impact,
        created_at=updated_shipment.created_at,
        updated_at=updated_shipment.updated_at,
    )

    return ResponseBuilder.success(
        data=shipment_data,
        message="Shipment location updated successfully",
        status_code=status.HTTP_200_OK,
    )
