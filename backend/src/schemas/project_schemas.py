"""
Project-related Pydantic schemas.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

from models.project import ProjectStatus


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
    tech_stack: List[str]
    github_url: Optional[str]
    live_url: Optional[str]
    image_url: Optional[str]
    status: ProjectStatus
    start_date: Optional[date]
    end_date: Optional[date]
    featured: bool
    author_id: str
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []
    author: Optional["UserResponse"] = None

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