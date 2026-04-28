"""
Fleet Service

Handles fleet management operations including vehicle tracking and maintenance.
"""

import uuid
from datetime import datetime, date
from typing import List, Dict
from math import floor

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestException, NotFoundException
from app.models.fleet import FleetUnit, VehicleType, FleetUnitStatus
from app.models.user import User
from app.schemas.fleet import FleetUnitCreate, FleetUnitUpdate


class FleetService:
    """Service for fleet management operations."""

    @staticmethod
    async def create_fleet_unit(
        unit_data: FleetUnitCreate,
        organization_id: str,
        db: AsyncSession
    ) -> FleetUnit:
        """Create a new fleet unit.

        Args:
            unit_data: Fleet unit creation data
            organization_id: Organization ID
            db: Database session

        Returns:
            Created fleet unit

        Raises:
            BadRequestException: If unit_id already exists
        """
        # Check if unit_id already exists
        result = await db.execute(
            select(FleetUnit).where(
                and_(
                    FleetUnit.unit_id == unit_data.unit_id,
                    FleetUnit.organization_id == organization_id
                )
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestException(
                message="Unit ID already exists in organization",
                details={"unit_id": unit_data.unit_id}
            )

        # Create fleet unit
        fleet_unit = FleetUnit(
            id=str(uuid.uuid4()),
            unit_id=unit_data.unit_id,
            organization_id=organization_id,
            type=unit_data.type,
            battery_health=unit_data.battery_health,
            fuel_level=unit_data.fuel_level,
            last_maintenance=unit_data.last_maintenance,
            current_driver_id=None,
            status=FleetUnitStatus.ACTIVE,
        )

        db.add(fleet_unit)
        await db.commit()
        await db.refresh(fleet_unit)

        return fleet_unit

    @staticmethod
    async def get_fleet_unit_by_id(unit_id: str, db: AsyncSession) -> FleetUnit | None:
        """Get fleet unit by ID.

        Args:
            unit_id: Fleet unit ID
            db: Database session

        Returns:
            Fleet unit or None if not found
        """
        result = await db.execute(
            select(FleetUnit).where(FleetUnit.id == unit_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_fleet_units(
        organization_id: str,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: FleetUnitStatus | None = None,
        vehicle_type: VehicleType | None = None
    ) -> List[FleetUnit]:
        """List fleet units in an organization with filters.

        Args:
            organization_id: Organization ID
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            vehicle_type: Filter by vehicle type

        Returns:
            List of fleet units
        """
        query = select(FleetUnit).where(FleetUnit.organization_id == organization_id)

        if status:
            query = query.where(FleetUnit.status == status)

        if vehicle_type:
            query = query.where(FleetUnit.type == vehicle_type)

        query = query.order_by(FleetUnit.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_fleet_unit(
        unit_id: str,
        unit_data: FleetUnitUpdate,
        db: AsyncSession
    ) -> FleetUnit:
        """Update fleet unit.

        Args:
            unit_id: Fleet unit ID
            unit_data: Update data
            db: Database session

        Returns:
            Updated fleet unit

        Raises:
            NotFoundException: If fleet unit not found
        """
        fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)
        if not fleet_unit:
            raise NotFoundException(
                message="Fleet unit not found",
                details={"unit_id": unit_id}
            )

        # Update fields
        if unit_data.type is not None:
            fleet_unit.type = unit_data.type
        if unit_data.battery_health is not None:
            fleet_unit.battery_health = unit_data.battery_health
        if unit_data.fuel_level is not None:
            fleet_unit.fuel_level = unit_data.fuel_level
        if unit_data.last_maintenance is not None:
            fleet_unit.last_maintenance = unit_data.last_maintenance
        if unit_data.status is not None:
            fleet_unit.status = unit_data.status

        await db.commit()
        await db.refresh(fleet_unit)

        return fleet_unit

    @staticmethod
    async def assign_driver(
        unit_id: str,
        driver_id: str,
        db: AsyncSession
    ) -> FleetUnit:
        """Assign a driver to a fleet unit.

        Args:
            unit_id: Fleet unit ID
            driver_id: User ID of the driver
            db: Database session

        Returns:
            Updated fleet unit

        Raises:
            NotFoundException: If fleet unit or driver not found
            BadRequestException: If driver is not valid
        """
        fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)
        if not fleet_unit:
            raise NotFoundException(
                message="Fleet unit not found",
                details={"unit_id": unit_id}
            )

        # Check if driver exists
        from app.models.user import UserRole
        result = await db.execute(
            select(User).where(User.id == driver_id)
        )
        driver = result.scalar_one_or_none()

        if not driver:
            raise NotFoundException(
                message="Driver not found",
                details={"driver_id": driver_id}
            )

        if driver.role != UserRole.DRIVER:
            raise BadRequestException(
                message="User is not a driver",
                details={"user_role": driver.role.value}
            )

        fleet_unit.current_driver_id = driver_id
        await db.commit()
        await db.refresh(fleet_unit)

        return fleet_unit

    @staticmethod
    async def get_fleet_diagnostics(
        unit_id: str,
        db: AsyncSession
    ) -> Dict:
        """Get diagnostics for a fleet unit.

        Args:
            unit_id: Fleet unit ID
            db: Database session

        Returns:
            Diagnostics data

        Raises:
            NotFoundException: If fleet unit not found
        """
        fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)
        if not fleet_unit:
            raise NotFoundException(
                message="Fleet unit not found",
                details={"unit_id": unit_id}
            )

        # Calculate days since maintenance
        days_since_maintenance = None
        if fleet_unit.last_maintenance:
            days_since_maintenance = (date.today() - fleet_unit.last_maintenance).days

        # Determine if maintenance is needed
        needs_maintenance = False
        if fleet_unit.battery_health < 0.8 or fleet_unit.fuel_level < 0.2:
            needs_maintenance = True
        if days_since_maintenance and days_since_maintenance > 90:  # 90 days
            needs_maintenance = True

        # Get driver name if assigned
        current_driver = None
        if fleet_unit.current_driver_id:
            result = await db.execute(
                select(User).where(User.id == fleet_unit.current_driver_id)
            )
            driver = result.scalar_one_or_none()
            if driver:
                current_driver = driver.full_name

        return {
            "unit_id": fleet_unit.unit_id,
            "battery_health": fleet_unit.battery_health,
            "fuel_level": fleet_unit.fuel_level,
            "status": fleet_unit.status.value,
            "last_maintenance": fleet_unit.last_maintenance,
            "days_since_maintenance": days_since_maintenance,
            "needs_maintenance": needs_maintenance,
            "current_driver": current_driver,
        }

    @staticmethod
    async def schedule_maintenance(
        unit_id: str,
        db: AsyncSession
    ) -> FleetUnit:
        """Mark a fleet unit for maintenance.

        Args:
            unit_id: Fleet unit ID
            db: Database session

        Returns:
            Updated fleet unit

        Raises:
            NotFoundException: If fleet unit not found
        """
        fleet_unit = await FleetService.get_fleet_unit_by_id(unit_id, db)
        if not fleet_unit:
            raise NotFoundException(
                message="Fleet unit not found",
                details={"unit_id": unit_id}
            )

        fleet_unit.status = FleetUnitStatus.MAINTENANCE
        await db.commit()
        await db.refresh(fleet_unit)

        return fleet_unit
