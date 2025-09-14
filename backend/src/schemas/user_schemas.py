"""
User-related Pydantic schemas.
"""

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    website_url: Optional[HttpUrl] = Field(None, description="Personal website URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[HttpUrl] = Field(None, description="Twitter profile URL")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    location: Optional[str] = Field(None, max_length=100, description="User location")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    website_url: Optional[HttpUrl] = Field(None, description="Personal website URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[HttpUrl] = Field(None, description="Twitter profile URL")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    location: Optional[str] = Field(None, max_length=100, description="User location")


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string."""
        return str(v) if v else v


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserStats(BaseModel):
    """Schema for user statistics."""
    total_posts: int
    published_posts: int
    total_projects: int
    published_projects: int
    total_tags_created: int