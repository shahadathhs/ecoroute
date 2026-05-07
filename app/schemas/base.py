"""
Base Response Schemas
"""

from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaData(BaseModel):
    """Optional metadata for responses."""

    total: int | None = Field(None, description="Total count of items")
    page: int | None = Field(None, description="Current page number")
    page_size: int | None = Field(None, description="Items per page")
    has_next: bool | None = Field(None, description="Whether there's a next page")
    has_prev: bool | None = Field(None, description="Whether there's a previous page")


class BaseResponse(BaseModel):
    """Base response schema with common fields."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")

    class Config:
        """Pydantic config."""

        from_attributes = True


class DataResponse[T](BaseModel):
    """Standard response schema with data."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: T = Field(..., description="Response data")
    metadata: MetaData | None = Field(None, description="Optional metadata")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: list[Any] | None = Field(None, description="Detailed error list")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class PaginatedResponse[T](BaseModel):
    """Response schema for paginated data."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: list[T] = Field(..., description="List of items")
    metadata: MetaData = Field(..., description="Pagination metadata")

    class Config:
        """Pydantic config."""

        from_attributes = True
