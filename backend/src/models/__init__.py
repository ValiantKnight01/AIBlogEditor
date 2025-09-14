"""
Models package for the blog backend.

This module imports all models to ensure they are registered with SQLAlchemy.
"""

from .user import User
from .blog_post import BlogPost, PostStatus
from .project import Project, ProjectStatus
from .tag import Tag
from .associations import blog_post_tags, project_tags

# Export all models
__all__ = [
    "User",
    "BlogPost",
    "PostStatus", 
    "Project",
    "ProjectStatus",
    "Tag",
    "blog_post_tags",
    "project_tags",
]