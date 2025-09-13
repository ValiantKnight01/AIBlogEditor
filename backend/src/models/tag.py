"""
Tag model for content categorization and organization.
"""

import uuid
from datetime import datetime
from typing import Optional
import re

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class Tag(Base):
    """Tag entity for categorizing blog posts and projects."""
    
    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Tag information
    name = Column(String(50), unique=True, index=True, nullable=False)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code (#RRGGBB)
    description = Column(String(200), nullable=True)
    
    # Statistics (computed values)
    post_count = Column(Integer, default=0, nullable=False)
    project_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog_posts = relationship("BlogPost", secondary="blog_post_tags", back_populates="tags")
    projects = relationship("Project", secondary="project_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', posts={self.post_count}, projects={self.project_count})>"
    
    def __str__(self) -> str:
        return self.name

    @property
    def total_usage(self) -> int:
        """Get total usage count across posts and projects."""
        return self.post_count + self.project_count

    def validate_color(self) -> bool:
        """Validate that color is a valid hex color code."""
        if not self.color:
            return True  # Color is optional
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, self.color))

    def update_counts(self) -> None:
        """Update post and project counts (should be called after relationship changes)."""
        self.post_count = len(self.blog_posts)
        self.project_count = len(self.projects)

    @classmethod
    def create_slug(cls, name: str) -> str:
        """Create a URL-friendly slug from tag name."""
        import re
        from slugify import slugify
        return slugify(name.lower().strip())

    def set_color(self, color: Optional[str]) -> None:
        """Set tag color with validation."""
        if color is None:
            self.color = None
            return
        
        # Ensure color starts with #
        if not color.startswith('#'):
            color = f'#{color}'
        
        # Validate format
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError(f"Invalid color format: {color}. Must be #RRGGBB")
        
        self.color = color.upper()

    @property
    def display_color(self) -> str:
        """Get display color with fallback to default."""
        return self.color if self.color else "#6B7280"  # Default gray color