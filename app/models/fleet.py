"""
Fleet Unit Model
"""

import uuid
from datetime import date
from enum import Enum

from sqlalchemy import Boolean, Date, Enum as SQLEnum, ForeignKey, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VehicleType(str, Enum):
    """Types of fleet vehicles."""

    EV_SEMI = "EV_SEMI"
    DIESEL_TRUCK = "DIESEL_TRUCK"
    HYBRID_VAN = "HYBRID_VAN"
    DRONE = "DRONE"


class FleetUnitStatus(str, Enum):
    """Fleet unit status values."""

    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class FleetUnit(Base, TimestampMixin):
    """Fleet unit model for vehicle tracking."""

    __tablename__ = "fleet_units"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    unit_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType), nullable=False
    )
    battery_health: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False
    )  # 0.0 to 1.0
    fuel_level: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False
    )  # 0.0 to 1.0
    last_maintenance: Mapped[date | None] = mapped_column(Date, nullable=True)
    current_driver_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[FleetUnitStatus] = mapped_column(
        SQLEnum(FleetUnitStatus), default=FleetUnitStatus.ACTIVE, nullable=False
    )

    # Relationships
    organization = relationship("Organization", back_populates="fleet_units")
    current_driver = relationship("User", foreign_keys=[current_driver_id])
