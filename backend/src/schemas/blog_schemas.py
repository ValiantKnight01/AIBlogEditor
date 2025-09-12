"""
Blog post-related Pydantic schemas.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from models.blog_post import PostStatus


class BlogPostBase(BaseModel):
    """Base blog post schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content in markdown")
    excerpt: Optional[str] = Field(None, max_length=500, description="Post excerpt/summary")
    featured_image_url: Optional[HttpUrl] = Field(None, description="Featured image URL")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    status: PostStatus = Field(PostStatus.DRAFT, description="Post publication status")


class BlogPostCreate(BlogPostBase):
    """Schema for creating a new blog post."""
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="List of tag IDs")


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Post title")
    content: Optional[str] = Field(None, min_length=1, description="Post content in markdown")
    excerpt: Optional[str] = Field(None, max_length=500, description="Post excerpt/summary")
    featured_image_url: Optional[HttpUrl] = Field(None, description="Featured image URL")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    status: Optional[PostStatus] = Field(None, description="Post publication status")
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")


class BlogPostResponse(BaseModel):
    """Schema for blog post response."""
    id: str
    title: str
    slug: str
    content: str
    excerpt: Optional[str]
    featured_image_url: Optional[str]
    meta_description: Optional[str]
    status: PostStatus
    author_id: str
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []
    author: Optional["UserResponse"] = None
    read_time_minutes: Optional[int] = None

    class Config:
        from_attributes = True

    @validator('read_time_minutes', always=True)
    def calculate_read_time(cls, v, values):
        """Calculate estimated read time based on content."""
        if 'content' in values and values['content']:
            word_count = len(values['content'].split())
            return max(1, round(word_count / 200))  # Assume 200 WPM reading speed
        return None


class BlogPostSummary(BaseModel):
    """Schema for blog post summary (for lists)."""
    id: str
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image_url: Optional[str]
    status: PostStatus
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []
    author: Optional["UserResponse"] = None
    read_time_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class BlogPostListResponse(BaseModel):
    """Schema for paginated blog post list response."""
    posts: List[BlogPostSummary]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class BlogPostStatusUpdate(BaseModel):
    """Schema for updating only the post status."""
    status: PostStatus = Field(..., description="New post status")


class BlogPostSearchParams(BaseModel):
    """Schema for blog post search parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term")
    status: Optional[PostStatus] = Field(None, description="Filter by status")
    tag_slug: Optional[str] = Field(None, description="Filter by tag slug")
    author_id: Optional[str] = Field(None, description="Filter by author ID")


# Forward reference resolution
from .tag_schemas import TagResponse
from .user_schemas import UserResponse
BlogPostResponse.model_rebuild()
BlogPostSummary.model_rebuild()