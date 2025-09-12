"""
Tag-related Pydantic schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class TagBase(BaseModel):
    """Base tag schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, description="Tag color in hex format")
    description: Optional[str] = Field(None, max_length=200, description="Tag description")

    @validator('name')
    def validate_name(cls, v):
        """Validate tag name."""
        if not v.strip():
            raise ValueError('Tag name cannot be empty')
        
        # Remove extra whitespace
        name = ' '.join(v.strip().split())
        
        if len(name) < 1:
            raise ValueError('Tag name must be at least 1 character')
        if len(name) > 50:
            raise ValueError('Tag name cannot exceed 50 characters')
            
        return name

    @validator('color')
    def validate_color(cls, v):
        """Validate hex color format."""
        if v is None:
            return v
            
        color = v.strip()
        if not color:
            return None
            
        # Add # if missing
        if not color.startswith('#'):
            color = '#' + color
        
        # Validate hex format
        if not re.match(r'^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$', color):
            raise ValueError('Color must be in hex format (e.g., #ff0000 or #f00)')
        
        # Convert 3-digit to 6-digit format
        if len(color) == 4:
            color = '#' + ''.join([c*2 for c in color[1:]])
        
        return color.lower()

    @validator('description')
    def validate_description(cls, v):
        """Validate tag description."""
        if v is None:
            return v
        
        desc = v.strip()
        if not desc:
            return None
            
        if len(desc) > 200:
            raise ValueError('Description cannot exceed 200 characters')
            
        return desc


class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, description="Tag color in hex format")
    description: Optional[str] = Field(None, max_length=200, description="Tag description")

    @validator('name')
    def validate_name(cls, v):
        """Validate tag name."""
        if v is None:
            return v
            
        if not v.strip():
            raise ValueError('Tag name cannot be empty')
        
        # Remove extra whitespace
        name = ' '.join(v.strip().split())
        
        if len(name) < 1:
            raise ValueError('Tag name must be at least 1 character')
        if len(name) > 50:
            raise ValueError('Tag name cannot exceed 50 characters')
            
        return name

    @validator('color')
    def validate_color(cls, v):
        """Validate hex color format."""
        if v is None:
            return v
            
        color = v.strip()
        if not color:
            return None
            
        # Add # if missing
        if not color.startswith('#'):
            color = '#' + color
        
        # Validate hex format
        if not re.match(r'^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$', color):
            raise ValueError('Color must be in hex format (e.g., #ff0000 or #f00)')
        
        # Convert 3-digit to 6-digit format
        if len(color) == 4:
            color = '#' + ''.join([c*2 for c in color[1:]])
        
        return color.lower()

    @validator('description')
    def validate_description(cls, v):
        """Validate tag description."""
        if v is None:
            return v
        
        desc = v.strip()
        if not desc:
            return None
            
        if len(desc) > 200:
            raise ValueError('Description cannot exceed 200 characters')
            
        return desc


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: int
    name: str
    slug: str
    color: str
    description: Optional[str]
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagSummary(BaseModel):
    """Schema for tag summary (minimal info)."""
    id: int
    name: str
    slug: str
    color: str
    usage_count: int = 0

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for paginated tag list response."""
    tags: List[TagResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class TagSearchParams(BaseModel):
    """Schema for tag search parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(50, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term")
    sort_by: str = Field("usage_count", description="Sort field")
    order: str = Field("desc", description="Sort order (asc/desc)")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Validate sort_by field."""
        allowed_fields = ['usage_count', 'name', 'created_at']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(allowed_fields)}')
        return v

    @validator('order')
    def validate_order(cls, v):
        """Validate order field."""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('order must be "asc" or "desc"')
        return v.lower()


class TagUsageStats(BaseModel):
    """Schema for tag usage statistics."""
    tag: TagResponse
    blog_post_count: int
    project_count: int
    total_usage: int


class TagMergeRequest(BaseModel):
    """Schema for merging tags."""
    source_tag_id: int = Field(..., description="ID of tag to merge from")
    target_tag_id: int = Field(..., description="ID of tag to merge into")

    @validator('target_tag_id')
    def validate_different_tags(cls, v, values):
        """Ensure source and target are different."""
        if 'source_tag_id' in values and v == values['source_tag_id']:
            raise ValueError('Source and target tags must be different')
        return v