"""
Shipment Service

Handles shipment management operations including creation, tracking, and updates.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestException, NotFoundException
from app.models.shipment import Shipment, ShipmentEvent, ShipmentStatus, ShipmentEventType
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentEventCreate


class ShipmentService:
    """Service for shipment management operations."""

    @staticmethod
    async def _generate_tracking_number() -> str:
        """Generate a unique tracking number.

        Returns:
            Unique tracking number
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"ATLAS-{timestamp}-{random_suffix}"

    @staticmethod
    async def create_shipment(
        shipment_data: ShipmentCreate,
        organization_id: str,
        db: AsyncSession
    ) -> Shipment:
        """Create a new shipment.

        Args:
            shipment_data: Shipment creation data
            organization_id: Organization ID
            db: Database session

        Returns:
            Created shipment
        """
        # Generate tracking number
        tracking_number = await ShipmentService._generate_tracking_number()

        # Create shipment
        shipment = Shipment(
            id=str(uuid.uuid4()),
            tracking_number=tracking_number,
            status=ShipmentStatus.PENDING,
            organization_id=organization_id,
            origin_city=shipment_data.origin_city,
            origin_code=shipment_data.origin_code,
            origin_coords=shipment_data.origin_coords,
            destination_city=shipment_data.destination_city,
            destination_code=shipment_data.destination_code,
            destination_coords=shipment_data.destination_coords,
            carrier=shipment_data.carrier,
            cargo_type=shipment_data.cargo_type,
            current_location=None,
            environmental_impact=None,  # TODO: Calculate CO2 estimate
        )

        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)

        # Log creation event
        await ShipmentService.add_shipment_event(
            shipment.id,
            ShipmentEventCreate(
                event_type=ShipmentEventType.CREATED,
                location=shipment_data.origin_coords,
                notes="Shipment created"
            ),
            None,  # No user context for initial creation
            db
        )

        return shipment

    @staticmethod
    async def get_shipment_by_id(shipment_id: str, db: AsyncSession) -> Shipment | None:
        """Get shipment by ID.

        Args:
            shipment_id: Shipment ID
            db: Database session

        Returns:
            Shipment or None if not found
        """
        result = await db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_shipment_by_tracking_number(
        tracking_number: str,
        db: AsyncSession
    ) -> Shipment | None:
        """Get shipment by tracking number.

        Args:
            tracking_number: Tracking number
            db: Database session

        Returns:
            Shipment or None if not found
        """
        result = await db.execute(
            select(Shipment).where(Shipment.tracking_number == tracking_number)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_shipments(
        organization_id: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: ShipmentStatus | None = None,
        search: str | None = None
    ) -> List[Shipment]:
        """List shipments in an organization with pagination and filters.

        Args:
            organization_id: Organization ID
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            search: Search term for tracking number or carrier

        Returns:
            List of shipments
        """
        query = select(Shipment).where(Shipment.organization_id == organization_id)

        if status:
            query = query.where(Shipment.status == status)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Shipment.tracking_number.ilike(search_pattern),
                    Shipment.carrier.ilike(search_pattern)
                )
            )

        query = query.order_by(Shipment.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_shipment_status(
        shipment_id: str,
        status: ShipmentStatus,
        db: AsyncSession
    ) -> Shipment:
        """Update shipment status.

        Args:
            shipment_id: Shipment ID
            status: New status
            db: Database session

        Returns:
            Updated shipment

        Raises:
            NotFoundException: If shipment not found
        """
        shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)
        if not shipment:
            raise NotFoundException(
                message="Shipment not found",
                details={"shipment_id": shipment_id}
            )

        shipment.status = status
        await db.commit()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    async def add_shipment_event(
        shipment_id: str,
        event_data: ShipmentEventCreate,
        created_by: str | None,
        db: AsyncSession
    ) -> ShipmentEvent:
        """Add an event to a shipment.

        Args:
            shipment_id: Shipment ID
            event_data: Event creation data
            created_by: User ID who created the event
            db: Database session

        Returns:
            Created event

        Raises:
            NotFoundException: If shipment not found
        """
        shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)
        if not shipment:
            raise NotFoundException(
                message="Shipment not found",
                details={"shipment_id": shipment_id}
            )

        event = ShipmentEvent(
            id=str(uuid.uuid4()),
            shipment_id=shipment_id,
            event_type=event_data.event_type,
            location=event_data.location,
            notes=event_data.notes,
            created_by=created_by,
        )

        db.add(event)
        await db.commit()
        await db.refresh(event)

        # Update shipment status based on event type
        status_mapping = {
            ShipmentEventType.PICKED_UP: ShipmentStatus.IN_TRANSIT,
            ShipmentEventType.DELIVERED: ShipmentStatus.DELIVERED,
        }

        if event_data.event_type in status_mapping:
            shipment.status = status_mapping[event_data.event_type]
            await db.commit()

        return event

    @staticmethod
    async def update_location(
        shipment_id: str,
        location: dict,
        db: AsyncSession
    ) -> Shipment:
        """Update shipment current location.

        Args:
            shipment_id: Shipment ID
            location: GPS coordinates {lat, lng, timestamp}
            db: Database session

        Returns:
            Updated shipment

        Raises:
            NotFoundException: If shipment not found
        """
        shipment = await ShipmentService.get_shipment_by_id(shipment_id, db)
        if not shipment:
            raise NotFoundException(
                message="Shipment not found",
                details={"shipment_id": shipment_id}
            )

        shipment.current_location = location
        await db.commit()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    def calculate_co2_estimate(vehicle_type: str, distance_km: float) -> float:
        """Calculate estimated CO2 emissions for a shipment.

        Args:
            vehicle_type: Type of vehicle
            distance_km: Distance in kilometers

        Returns:
            Estimated CO2 emissions in kg
        """
        # Emission factors (kg CO2 per km)
        emission_factors = {
            "EV_SEMI": 0.05,       # Electric: emissions from electricity generation
            "DIESEL_TRUCK": 0.8,   # Diesel: high emissions
            "HYBRID_VAN": 0.4,     # Hybrid: moderate emissions
            "DRONE": 0.02,         # Drone: very low emissions
        }

        factor = emission_factors.get(vehicle_type, 0.5)  # Default to 0.5
        return round(distance_km * factor, 2)
