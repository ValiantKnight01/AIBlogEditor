"""
Tag service with CRUD and association management.
Handles tag management, color formatting, and usage tracking.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
import re

from models.tag import Tag
from models.associations import blog_post_tags, project_tags
from utils.slug_utils import SlugUtils
from utils.pagination import PaginationUtils, PageInfo
from database import get_db


class TagService:
    """Service for tag management operations."""
    
    def __init__(self):
        self.default_colors = [
            "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
            "#06b6d4", "#84cc16", "#f97316", "#ec4899", "#6b7280"
        ]
    
    def create_tag(
        self,
        db: Session,
        name: str,
        color: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Create a new tag."""
        # Validate and normalize name
        name = name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tag name cannot be empty"
            )
        
        if len(name) > 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tag name cannot exceed 50 characters"
            )
        
        # Check for duplicate name (case-insensitive)
        existing_tag = db.query(Tag).filter(
            func.lower(Tag.name) == name.lower()
        ).first()
        
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tag with this name already exists"
            )
        
        # Generate slug from name
        slug = SlugUtils.create_slug(name)
        
        # Ensure slug uniqueness
        slug = SlugUtils.ensure_unique_slug(db, slug, self._check_slug_exists)
        
        # Validate and set color
        if color:
            color = self._validate_and_normalize_color(color)
        else:
            color = self._get_next_default_color(db)
        
        # Create tag
        tag = Tag(
            name=name,
            slug=slug,
            color=color,
            description=description.strip() if description else None
        )
        
        try:
            db.add(tag)
            db.commit()
            db.refresh(tag)
            return tag
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A tag with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tag creation failed due to conflict"
                )
    
    def get_tag_by_id(self, db: Session, tag_id: int) -> Optional[Tag]:
        """Get tag by ID."""
        return db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_tag_by_slug(self, db: Session, slug: str) -> Optional[Tag]:
        """Get tag by slug."""
        return db.query(Tag).filter(Tag.slug == slug).first()
    
    def get_tag_by_name(self, db: Session, name: str) -> Optional[Tag]:
        """Get tag by name (case-insensitive)."""
        return db.query(Tag).filter(func.lower(Tag.name) == name.lower()).first()
    
    def get_tags_list(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        sort_by: str = "usage_count",
        order: str = "desc"
    ):
        """Get paginated list of tags with usage counts."""
        # Build base query with usage counts
        query = db.query(
            Tag,
            func.coalesce(
                func.count(blog_post_tags.c.tag_id) + 
                func.count(project_tags.c.tag_id), 0
            ).label('usage_count')
        ).outerjoin(
            blog_post_tags, Tag.id == blog_post_tags.c.tag_id
        ).outerjoin(
            project_tags, Tag.id == project_tags.c.tag_id
        ).group_by(Tag.id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Tag.name.ilike(search_term),
                    Tag.description.ilike(search_term)
                )
            )
        
        # Apply sorting
        if sort_by == "usage_count":
            if order == "desc":
                query = query.order_by(desc("usage_count"))
            else:
                query = query.order_by("usage_count")
        elif sort_by == "name":
            if order == "desc":
                query = query.order_by(desc(Tag.name))
            else:
                query = query.order_by(Tag.name)
        elif sort_by == "created_at":
            if order == "desc":
                query = query.order_by(desc(Tag.created_at))
            else:
                query = query.order_by(Tag.created_at)
        else:
            query = query.order_by(desc("usage_count"))  # Default sorting
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = PaginationUtils.calculate_offset(page, per_page)
        results = query.offset(offset).limit(per_page).all()
        
        # Extract tags and update usage counts
        tags = []
        for tag, usage_count in results:
            tag.usage_count = usage_count
            tags.append(tag)
        
        page_info = PageInfo.from_params(page, per_page, total_count)
        return tags, page_info
    
    def update_tag(
        self,
        db: Session,
        tag_id: int,
        update_data: Dict[str, Any]
    ):
        """Update a tag."""
        tag = self.get_tag_by_id(db, tag_id)
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        try:
            # Handle name change
            if "name" in update_data:
                new_name = update_data["name"].strip()
                if new_name != tag.name:
                    # Check for duplicate name
                    existing_tag = db.query(Tag).filter(
                        and_(
                            func.lower(Tag.name) == new_name.lower(),
                            Tag.id != tag_id
                        )
                    ).first()
                    
                    if existing_tag:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="A tag with this name already exists"
                        )
                    
                    tag.name = new_name
                    # Update slug based on new name
                    new_slug = SlugUtils.create_slug(new_name)
                    tag.slug = SlugUtils.ensure_unique_slug(
                        db, new_slug, 
                        lambda db, slug: self._check_slug_exists_excluding(db, slug, tag_id)
                    )
            
            # Handle color change
            if "color" in update_data:
                tag.color = self._validate_and_normalize_color(update_data["color"])
            
            # Handle description change
            if "description" in update_data:
                tag.description = update_data["description"].strip() if update_data["description"] else None
            
            tag.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(tag)
            return tag
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A tag with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tag update failed due to conflict"
                )
    
    def delete_tag(self, db: Session, tag_id: int) -> bool:
        """Delete a tag and remove all associations."""
        tag = self.get_tag_by_id(db, tag_id)
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        # Remove all associations first
        db.execute(blog_post_tags.delete().where(blog_post_tags.c.tag_id == tag_id))
        db.execute(project_tags.delete().where(project_tags.c.tag_id == tag_id))
        
        # Delete the tag
        db.delete(tag)
        db.commit()
        return True
    
    def get_tags_count(self, db: Session, search: Optional[str] = None) -> int:
        """Get total count of tags."""
        query = db.query(Tag)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Tag.name.ilike(search_term),
                    Tag.description.ilike(search_term)
                )
            )
        
        return query.count()
    
    def get_popular_tags(self, db: Session, limit: int = 20):
        """Get most popular tags by usage count."""
        query = db.query(
            Tag,
            func.coalesce(
                func.count(blog_post_tags.c.tag_id) + 
                func.count(project_tags.c.tag_id), 0
            ).label('usage_count')
        ).outerjoin(
            blog_post_tags, Tag.id == blog_post_tags.c.tag_id
        ).outerjoin(
            project_tags, Tag.id == project_tags.c.tag_id
        ).group_by(Tag.id).having(
            func.count(blog_post_tags.c.tag_id) + 
            func.count(project_tags.c.tag_id) > 0
        ).order_by(desc('usage_count')).limit(limit)
        
        tags = []
        for tag, usage_count in query.all():
            tag.usage_count = usage_count
            tags.append(tag)
        
        return tags
    
    def get_unused_tags(self, db: Session):
        """Get tags that are not associated with any posts or projects."""
        query = db.query(Tag).outerjoin(
            blog_post_tags, Tag.id == blog_post_tags.c.tag_id
        ).outerjoin(
            project_tags, Tag.id == project_tags.c.tag_id
        ).filter(
            and_(
                blog_post_tags.c.tag_id.is_(None),
                project_tags.c.tag_id.is_(None)
            )
        ).order_by(Tag.created_at)
        
        return query.all()
    
    def merge_tags(self, db: Session, source_tag_id: int, target_tag_id: int) -> bool:
        """Merge one tag into another (move all associations)."""
        source_tag = self.get_tag_by_id(db, source_tag_id)
        target_tag = self.get_tag_by_id(db, target_tag_id)
        
        if not source_tag or not target_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both tags not found"
            )
        
        if source_tag_id == target_tag_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot merge a tag with itself"
            )
        
        # Move blog post associations
        db.execute(
            blog_post_tags.update()
            .where(blog_post_tags.c.tag_id == source_tag_id)
            .values(tag_id=target_tag_id)
        )
        
        # Move project associations
        db.execute(
            project_tags.update()
            .where(project_tags.c.tag_id == source_tag_id)
            .values(tag_id=target_tag_id)
        )
        
        # Delete the source tag
        db.delete(source_tag)
        db.commit()
        
        return True
    
    def _validate_and_normalize_color(self, color: str) -> str:
        """Validate and normalize a hex color."""
        if not color:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Color cannot be empty"
            )
        
        # Remove whitespace and ensure it starts with #
        color = color.strip()
        if not color.startswith('#'):
            color = '#' + color
        
        # Validate hex format
        if not re.match(r'^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$', color):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid color format. Use hex format like #ff0000 or #f00"
            )
        
        # Convert 3-digit to 6-digit format
        if len(color) == 4:
            color = '#' + ''.join([c*2 for c in color[1:]])
        
        return color.lower()
    
    def _get_next_default_color(self, db: Session) -> str:
        """Get the next available default color."""
        # Get colors already in use
        used_colors = {tag.color for tag in db.query(Tag.color).all()}
        
        # Find first unused default color
        for color in self.default_colors:
            if color not in used_colors:
                return color
        
        # If all defaults are used, return the first one
        return self.default_colors[0]
    
    def _check_slug_exists(self, db: Session, slug: str) -> bool:
        """Check if a slug already exists."""
        return db.query(Tag).filter(Tag.slug == slug).first() is not None
    
    def _check_slug_exists_excluding(self, db: Session, slug: str, exclude_id: int) -> bool:
        """Check if slug exists excluding a specific tag ID."""
        return db.query(Tag).filter(
            and_(Tag.slug == slug, Tag.id != exclude_id)
        ).first() is not None


# Global service instance
tag_service = TagService()