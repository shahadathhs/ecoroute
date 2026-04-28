"""
Fleet Management Schemas
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.fleet import VehicleType, FleetUnitStatus
from app.schemas.base import DataResponse


class FleetUnitCreate(BaseModel):
    """Fleet unit creation schema."""

    unit_id: str = Field(..., min_length=1, max_length=100, description="Unique unit identifier")
    type: VehicleType = Field(..., description="Vehicle type")
    battery_health: float = Field(
        default=1.0, ge=0, le=1, description="Battery health (0.0 to 1.0)"
    )
    fuel_level: float = Field(
        default=1.0, ge=0, le=1, description="Fuel level (0.0 to 1.0)"
    )
    last_maintenance: date | None = Field(None, description="Last maintenance date")


class FleetUnitUpdate(BaseModel):
    """Fleet unit update schema."""

    type: VehicleType | None = Field(None, description="Vehicle type")
    battery_health: float | None = Field(None, ge=0, le=1, description="Battery health")
    fuel_level: float | None = Field(None, ge=0, le=1, description="Fuel level")
    last_maintenance: date | None = Field(None, description="Last maintenance date")
    status: FleetUnitStatus | None = Field(None, description="Unit status")


class FleetUnitData(BaseModel):
    """Fleet unit data schema."""

    id: str = Field(..., description="Unit ID")
    unit_id: str = Field(..., description="Unique unit identifier")
    organization_id: str = Field(..., description="Organization ID")
    type: VehicleType = Field(..., description="Vehicle type")
    battery_health: float = Field(..., description="Battery health (0.0 to 1.0)")
    fuel_level: float = Field(..., description="Fuel level (0.0 to 1.0)")
    last_maintenance: date | None = Field(None, description="Last maintenance date")
    current_driver_id: str | None = Field(None, description="Current driver ID")
    status: FleetUnitStatus = Field(..., description="Unit status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DriverAssignmentRequest(BaseModel):
    """Driver assignment request schema."""

    driver_id: str = Field(..., description="Driver user ID")


class FleetDiagnostics(BaseModel):
    """Fleet diagnostics data schema."""

    unit_id: str = Field(..., description="Unit identifier")
    battery_health: float = Field(..., description="Battery health percentage")
    fuel_level: float = Field(..., description="Fuel level percentage")
    status: FleetUnitStatus = Field(..., description="Current status")
    last_maintenance: date | None = Field(None, description="Last maintenance date")
    days_since_maintenance: int | None = Field(None, description="Days since last maintenance")
    needs_maintenance: bool = Field(..., description="Whether maintenance is needed")
    current_driver: str | None = Field(None, description="Current driver name")


# Response types
FleetUnitResponse = DataResponse[FleetUnitData]
FleetDiagnosticsResponse = DataResponse[FleetDiagnostics]
