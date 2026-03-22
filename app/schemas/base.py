"""
Base Response Schemas
"""
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field


T = TypeVar("T")


class MetaData(BaseModel):
    """Optional metadata for responses."""

    total: Optional[int] = Field(None, description="Total count of items")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Items per page")
    has_next: Optional[bool] = Field(None, description="Whether there's a next page")
    has_prev: Optional[bool] = Field(None, description="Whether there's a previous page")


class BaseResponse(BaseModel):
    """Base response schema with common fields."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")

    class Config:
        """Pydantic config."""

        from_attributes = True


class DataResponse(BaseModel, Generic[T]):
    """Standard response schema with data."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: T = Field(..., description="Response data")
    metadata: Optional[MetaData] = Field(None, description="Optional metadata")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: Optional[list[Any]] = Field(None, description="Detailed error list")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """Response schema for paginated data."""

    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: list[T] = Field(..., description="List of items")
    metadata: MetaData = Field(..., description="Pagination metadata")

    class Config:
        """Pydantic config."""

        from_attributes = True
