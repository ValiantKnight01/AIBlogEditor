"""
Junction tables for many-to-many relationships between entities.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


# Blog Post Tags Junction Table
blog_post_tags = Table(
    "blog_post_tags",
    Base.metadata,
    Column(
        "blog_post_id", 
        UUID(as_uuid=True), 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    ),
    Column(
        "tag_id", 
        UUID(as_uuid=True), 
        ForeignKey("tags.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    ),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
)


# Project Tags Junction Table
project_tags = Table(
    "project_tags",
    Base.metadata,
    Column(
        "project_id", 
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    ),
    Column(
        "tag_id", 
        UUID(as_uuid=True), 
        ForeignKey("tags.id", ondelete="CASCADE"), 
        primary_key=True,
        index=True
    ),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
)