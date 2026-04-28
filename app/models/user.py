"""
User and Organization Models
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class SubscriptionTier(str, Enum):
    """Organization subscription tiers."""

    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class UserRole(str, Enum):
    """User roles for RBAC."""

    SUPER_ADMIN = "SUPER_ADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    LOGISTICS_MANAGER = "LOGISTICS_MANAGER"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    SUSTAINABILITY_LEAD = "SUSTAINABILITY_LEAD"
    STANDARD_DISPATCHER = "STANDARD_DISPATCHER"
    DRIVER = "DRIVER"


class Organization(Base, TimestampMixin):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False
    )
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="organization", cascade="all, delete-orphan")
    fleet_units = relationship("FleetUnit", back_populates="organization", cascade="all, delete-orphan")


class User(Base, TimestampMixin):
    """User model with RBAC."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.STANDARD_DISPATCHER, nullable=False
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    assigned_fleet_units = relationship("FleetUnit", foreign_keys="FleetUnit.current_driver_id")
    created_shipment_events = relationship("ShipmentEvent", foreign_keys="ShipmentEvent.created_by")
