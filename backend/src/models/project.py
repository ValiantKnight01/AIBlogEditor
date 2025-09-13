"""
Project model for portfolio projects and showcases.
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from src.database import Base


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"


class Project(Base):
    """Project entity for portfolio projects."""
    
    __tablename__ = "projects"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information
    title = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(200), nullable=True)
    
    # Status and publication
    status = Column(String(20), default='draft', nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    
    # Creator relationship
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Project links and media
    project_url = Column(String(500), nullable=True)  # Live project URL
    github_url = Column(String(500), nullable=True)   # Source code URL
    image_url = Column(String(500), nullable=True)    # Project screenshot
    
    # Technical details
    tech_stack = Column(JSON, nullable=True)  # Array of technology names
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="projects")
    tags = relationship("Tag", secondary="project_tags", back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title='{self.title}', status={self.status})>"
    
    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    def publish(self) -> None:
        """Publish the project."""
        self.status = ProjectStatus.PUBLISHED
        self.published_at = datetime.utcnow()
    
    def unpublish(self) -> None:
        """Unpublish the project (set to draft)."""
        self.status = ProjectStatus.DRAFT
        self.published_at = None

    @property
    def is_published(self) -> bool:
        """Check if the project is published."""
        return self.status == ProjectStatus.PUBLISHED and self.published_at is not None
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calculate project duration in days."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    @property
    def is_ongoing(self) -> bool:
        """Check if the project is still ongoing."""
        if self.start_date and not self.end_date:
            return True
        return False

    def add_technology(self, technology: str) -> None:
        """Add a technology to the tech stack."""
        if self.tech_stack is None:
            self.tech_stack = []
        if technology not in self.tech_stack:
            self.tech_stack.append(technology)
    
    def remove_technology(self, technology: str) -> None:
        """Remove a technology from the tech stack."""
        if self.tech_stack and technology in self.tech_stack:
            self.tech_stack.remove(technology)

    def set_tech_stack(self, technologies: List[str]) -> None:
        """Set the complete tech stack."""
        self.tech_stack = list(set(technologies)) if technologies else []