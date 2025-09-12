"""
Common shared schemas and utilities.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime


T = TypeVar('T')


class PageInfo(BaseModel):
    """Pagination metadata."""
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    page_info: PageInfo


class ErrorDetail(BaseModel):
    """Error detail schema."""
    type: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Success response schema."""
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    environment: Optional[str] = None


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str
    message: str
    invalid_value: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: str = "Validation failed"
    validation_errors: List[ValidationErrorDetail]


class SearchParams(BaseModel):
    """Base search parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term")


class SortParams(BaseModel):
    """Base sort parameters."""
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Base filter parameters."""
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    updated_after: Optional[datetime] = Field(None, description="Filter by update date")
    updated_before: Optional[datetime] = Field(None, description="Filter by update date")


class BulkOperationRequest(BaseModel):
    """Base bulk operation request."""
    item_ids: List[str] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., description="Operation to perform")


class BulkOperationResponse(BaseModel):
    """Bulk operation response."""
    success_count: int
    error_count: int
    errors: List[ErrorDetail] = []
    processed_ids: List[str] = []


class StatsResponse(BaseModel):
    """Generic statistics response."""
    total_count: int
    stats: Dict[str, Any] = {}
    period: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ImportRequest(BaseModel):
    """Data import request."""
    data: List[Dict[str, Any]]
    options: Dict[str, Any] = {}
    dry_run: bool = False


class ImportResponse(BaseModel):
    """Data import response."""
    total_processed: int
    successful_imports: int
    failed_imports: int
    errors: List[ErrorDetail] = []
    warnings: List[str] = []
    dry_run: bool = False


class ExportRequest(BaseModel):
    """Data export request."""
    format: str = Field("json", pattern="^(json|csv|xml)$")
    filters: Optional[Dict[str, Any]] = None
    fields: Optional[List[str]] = None


class ExportResponse(BaseModel):
    """Data export response."""
    download_url: str
    filename: str
    format: str
    total_records: int
    expires_at: datetime