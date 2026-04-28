"""
Shipment Management Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.shipment import ShipmentStatus, ShipmentEventType
from app.schemas.base import DataResponse


class LocationData(BaseModel):
    """Location data schema."""

    city: str = Field(..., description="City name")
    code: str = Field(..., description="Airport/port code")
    coords: dict | None = Field(None, description="GPS coordinates {lat, lng}")


class EnvironmentalImpact(BaseModel):
    """Environmental impact data schema."""

    co2_estimate_kg: float = Field(..., description="Estimated CO2 emissions in kg")
    route_efficiency: float = Field(..., ge=0, le=1, description="Route efficiency score")


class ShipmentCreate(BaseModel):
    """Shipment creation schema."""

    origin_city: str = Field(..., description="Origin city name")
    origin_code: str = Field(..., description="Origin airport/port code")
    origin_coords: dict | None = Field(None, description="Origin GPS coordinates")
    destination_city: str = Field(..., description="Destination city name")
    destination_code: str = Field(..., description="Destination airport/port code")
    destination_coords: dict | None = Field(None, description="Destination GPS coordinates")
    carrier: str = Field(..., description="Carrier company name")
    cargo_type: str = Field(..., description="Cargo type description")


class ShipmentUpdate(BaseModel):
    """Shipment update schema."""

    status: ShipmentStatus | None = Field(None, description="Shipment status")
    carrier: str | None = Field(None, description="Carrier company name")
    cargo_type: str | None = Field(None, description="Cargo type description")


class ShipmentData(BaseModel):
    """Shipment data schema."""

    id: str = Field(..., description="Shipment ID")
    tracking_number: str = Field(..., description="Unique tracking number")
    status: ShipmentStatus = Field(..., description="Shipment status")
    organization_id: str = Field(..., description="Organization ID")
    origin_city: str = Field(..., description="Origin city")
    origin_code: str = Field(..., description="Origin airport/port code")
    origin_coords: dict | None = Field(None, description="Origin GPS coordinates")
    destination_city: str = Field(..., description="Destination city")
    destination_code: str = Field(..., description="Destination airport/port code")
    destination_coords: dict | None = Field(None, description="Destination GPS coordinates")
    current_location: dict | None = Field(None, description="Current GPS location")
    carrier: str = Field(..., description="Carrier company")
    cargo_type: str = Field(..., description="Cargo type")
    environmental_impact: dict | None = Field(None, description="Environmental impact data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ShipmentEventCreate(BaseModel):
    """Shipment event creation schema."""

    event_type: ShipmentEventType = Field(..., description="Event type")
    location: dict | None = Field(None, description="Event location")
    notes: str | None = Field(None, description="Event notes")


class ShipmentEventData(BaseModel):
    """Shipment event data schema."""

    id: str = Field(..., description="Event ID")
    shipment_id: str = Field(..., description="Shipment ID")
    event_type: ShipmentEventType = Field(..., description="Event type")
    location: dict | None = Field(None, description="Event location")
    notes: str | None = Field(None, description="Event notes")
    created_by: str | None = Field(None, description="Creator user ID")
    created_at: datetime = Field(..., description="Event timestamp")


class LocationUpdate(BaseModel):
    """Location update schema."""

    location: dict = Field(..., description="GPS coordinates {lat, lng, timestamp}")


# Response types
ShipmentResponse = DataResponse[ShipmentData]
ShipmentEventResponse = DataResponse[ShipmentEventData]
