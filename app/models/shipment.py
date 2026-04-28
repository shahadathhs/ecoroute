"""
Shipment and ShipmentEvent Models
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ShipmentStatus(str, Enum):
    """Shipment status values."""

    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ShipmentEventType(str, Enum):
    """Shipment event types."""

    CREATED = "CREATED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    CUSTOMS_CLEARANCE = "CUSTOMS_CLEARANCE"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    ISSUE_REPORTED = "ISSUE_REPORTED"


class Shipment(Base, TimestampMixin):
    """Shipment model for tracking cargo."""

    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tracking_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    status: Mapped[ShipmentStatus] = mapped_column(
        SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Origin information
    origin_city: Mapped[str] = mapped_column(String(255), nullable=False)
    origin_code: Mapped[str] = mapped_column(String(50), nullable=False)  # Airport/port code
    origin_coords: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"lat": 0, "lng": 0}

    # Destination information
    destination_city: Mapped[str] = mapped_column(String(255), nullable=False)
    destination_code: Mapped[str] = mapped_column(String(50), nullable=False)
    destination_coords: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Current location
    current_location: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # {"lat": 0, "lng": 0, "timestamp": "..."}

    # Cargo details
    carrier: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo_type: Mapped[str] = mapped_column(String(255), nullable=False)

    # Environmental impact
    environmental_impact: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # {"co2_estimate_kg": 450, "route_efficiency": 0.85}

    # Relationships
    organization = relationship("Organization", back_populates="shipments")
    events = relationship(
        "ShipmentEvent",
        back_populates="shipment",
        cascade="all, delete-orphan",
        order_by="ShipmentEvent.created_at.desc()",
    )


class ShipmentEvent(Base, TimestampMixin):
    """Shipment event log for tracking milestones."""

    __tablename__ = "shipment_events"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    shipment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shipments.id"), nullable=False, index=True
    )
    event_type: Mapped[ShipmentEventType] = mapped_column(
        SQLEnum(ShipmentEventType), nullable=False
    )
    location: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # {"city": "...", "lat": 0, "lng": 0}
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    shipment = relationship("Shipment", back_populates="events")
    creator = relationship("User", foreign_keys=[created_by])
