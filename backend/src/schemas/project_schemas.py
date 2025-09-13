"""
Project-related Pydantic schemas.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

from src.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    description: str = Field(..., min_length=1, description="Project description")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub repository URL")
    live_url: Optional[HttpUrl] = Field(None, description="Live project URL")
    image_url: Optional[HttpUrl] = Field(None, description="Project image URL")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="Project publication status")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    featured: bool = Field(False, description="Whether project is featured")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is not before start date."""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v

    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        """Validate tech stack items."""
        if len(v) > 20:  # Reasonable limit
            raise ValueError('Too many technologies specified (max 20)')
        
        # Clean up tech stack items
        cleaned = []
        for tech in v:
            if isinstance(tech, str) and tech.strip():
                tech_clean = tech.strip()[:50]  # Limit length
                if tech_clean not in cleaned:  # Remove duplicates
                    cleaned.append(tech_clean)
        
        return cleaned


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="List of tag IDs")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(None, min_length=1, description="Project description")
    tech_stack: Optional[List[str]] = Field(None, description="Technologies used")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub repository URL")
    live_url: Optional[HttpUrl] = Field(None, description="Live project URL")
    image_url: Optional[HttpUrl] = Field(None, description="Project image URL")
    status: Optional[ProjectStatus] = Field(None, description="Project publication status")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    featured: Optional[bool] = Field(None, description="Whether project is featured")
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is not before start date."""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v

    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        """Validate tech stack items."""
        if v is None:
            return v
            
        if len(v) > 20:  # Reasonable limit
            raise ValueError('Too many technologies specified (max 20)')
        
        # Clean up tech stack items
        cleaned = []
        for tech in v:
            if isinstance(tech, str) and tech.strip():
                tech_clean = tech.strip()[:50]  # Limit length
                if tech_clean not in cleaned:  # Remove duplicates
                    cleaned.append(tech_clean)
        
        return cleaned


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    title: str
    slug: str
    description: str
    content: Optional[str] = None  # Alias for description for contract compatibility
    tech_stack: List[str]
    github_url: Optional[str]
    project_url: Optional[str]  # Changed from live_url to project_url
    demo_url: Optional[str] = None  # Alias for project_url for contract compatibility
    image_url: Optional[str]
    status: ProjectStatus
    start_date: Optional[date]
    end_date: Optional[date]
    featured: bool  # Re-added as now in model
    creator_id: str  # Changed from author_id to creator_id
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None  # Add missing field from model
    tags: List["TagResponse"] = []
    creator: Optional["UserResponse"] = None  # Changed from author to creator
    author: Optional["UserResponse"] = None  # Alias for creator for contract compatibility

    @validator('id', 'creator_id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings."""
        return str(v) if v is not None else v

    def __init__(self, **data):
        """Initialize with aliases for contract compatibility."""
        # Set content as alias for description
        if 'description' in data and 'content' not in data:
            data['content'] = data['description']
        
        # Set demo_url as alias for project_url
        if 'project_url' in data and 'demo_url' not in data:
            data['demo_url'] = data['project_url']
            
        # Set author as alias for creator
        if 'creator' in data and 'author' not in data:
            data['author'] = data['creator']
            
        super().__init__(**data)

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    """Schema for project summary (for lists)."""
    id: str
    title: str
    slug: str
    description: str
    tech_stack: List[str]
    image_url: Optional[str]
    status: ProjectStatus
    featured: bool
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []
    author: Optional["UserResponse"] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response."""
    items: List[ProjectSummary]  # Changed from "projects" to "items"
    total: int
    page: int
    limit: int  # Changed from "per_page" to "limit"
    pages: int  # Changed from "total_pages" to "pages"
    has_next: bool
    has_prev: bool


class ProjectStatusUpdate(BaseModel):
    """Schema for updating only the project status."""
    status: ProjectStatus = Field(..., description="New project status")


class ProjectFeaturedUpdate(BaseModel):
    """Schema for updating featured status."""
    featured: bool = Field(..., description="Whether project should be featured")


class ProjectSearchParams(BaseModel):
    """Schema for project search parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term")
    status: Optional[ProjectStatus] = Field(None, description="Filter by status")
    tech_filter: Optional[str] = Field(None, description="Filter by technology")
    tag_slug: Optional[str] = Field(None, description="Filter by tag slug")
    featured_only: bool = Field(False, description="Show only featured projects")
    author_id: Optional[str] = Field(None, description="Filter by author ID")


class TechStackResponse(BaseModel):
    """Schema for technology stack statistics."""
    technology: str
    usage_count: int
    projects: List[ProjectSummary]


# Forward reference resolution
from .tag_schemas import TagResponse
from .user_schemas import UserResponse
ProjectResponse.model_rebuild()
ProjectSummary.model_rebuild()