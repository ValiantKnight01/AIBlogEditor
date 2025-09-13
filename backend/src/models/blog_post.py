"""
BlogPost model for blog articles and content.
"""

import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class PostStatus(str, Enum):
    """Blog post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"


class BlogPost(Base):
    """BlogPost entity for blog articles."""
    
    __tablename__ = "blog_posts"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Content fields
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(300), nullable=True)
    
    # Status and publication  
    status = Column(String(20), default='draft', nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    
    # Author relationship
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metadata
    view_count = Column(Integer, default=0, nullable=False)
    featured_image_url = Column(String(500), nullable=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(300), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="blog_posts")
    tags = relationship("Tag", secondary="blog_post_tags", back_populates="blog_posts")

    def __repr__(self) -> str:
        return f"<BlogPost(id={self.id}, title='{self.title}', status={self.status})>"
    
    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    def publish(self) -> None:
        """Publish the blog post."""
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.utcnow()
    
    def unpublish(self) -> None:
        """Unpublish the blog post (set to draft)."""
        self.status = PostStatus.DRAFT
        self.published_at = None

    @property
    def is_published(self) -> bool:
        """Check if the blog post is published."""
        return self.status == PostStatus.PUBLISHED and self.published_at is not None