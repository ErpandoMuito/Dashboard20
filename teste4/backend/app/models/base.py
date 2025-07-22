"""
Base models and mixins for Pydantic models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
    request_id: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, data: list, total: int, page: int, page_size: int, **kwargs):
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            data={"items": data},
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            **kwargs
        )