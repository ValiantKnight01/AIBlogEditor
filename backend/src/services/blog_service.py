"""
BlogPost service with CRUD and slug generation.
Handles blog post management, content publishing, and slug operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status

from src.models.blog_post import BlogPost, PostStatus
from src.models.associations import blog_post_tags
from src.models.tag import Tag
from src.services.tag_service import TagService
from src.utils.slug_utils import SlugUtils
from src.utils.pagination import PaginationUtils, PageInfo
from src.database import get_db


class BlogPostService:
    """Service for blog post management operations."""
    
    def __init__(self):
        self.tag_service = TagService()
    
    def create_post(
        self,
        db: Session,
        user_id: str,
        title: str,
        content: str,
        excerpt: Optional[str] = None,
        status: PostStatus = PostStatus.DRAFT,
        featured_image_url: Optional[str] = None,
        meta_description: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
        tag_names: Optional[List[str]] = None
    ):
        """Create a new blog post."""
        # Generate unique slug from title
        slug = SlugUtils.create_unique_slug_from_title(
            db, title, self._check_slug_exists
        )
        
        # Generate excerpt if not provided
        if not excerpt and content:
            # Extract first 200 characters as excerpt, break at word boundary
            excerpt = content[:200].rsplit(' ', 1)[0]
            if len(content) > 200:
                excerpt += "..."
        
        # Ensure status is a proper string value for database
        if isinstance(status, PostStatus):
            status_value = status.value
        else:
            status_value = str(status).lower()
        
        # Create blog post
        post = BlogPost(
            title=title.strip(),
            slug=slug,
            content=content,
            excerpt=excerpt,
            author_id=user_id,
            status=status_value,
            featured_image_url=featured_image_url,
            meta_description=meta_description,
            published_at=datetime.utcnow() if status == PostStatus.PUBLISHED else None
        )
        
        try:
            db.add(post)
            db.flush()  # Get the post ID
            
            # Resolve and add tags if provided
            resolved_tag_ids = self.tag_service.resolve_tag_ids(db, tag_ids, tag_names)
            if resolved_tag_ids:
                self._add_tags_to_post(db, post.id, resolved_tag_ids)
            
            db.commit()
            db.refresh(post)
            return post
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A post with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Post creation failed due to conflict"
                )
    
    def get_post_by_id(self, db: Session, post_id: str) -> Optional[BlogPost]:
        """Get blog post by ID."""
        return db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    def get_post_by_slug(self, db: Session, slug: str) -> Optional[BlogPost]:
        """Get blog post by slug."""
        return db.query(BlogPost).filter(BlogPost.slug == slug).first()
    
    def get_published_post_by_slug(self, db: Session, slug: str) -> Optional[BlogPost]:
        """Get published blog post by slug (for public access)."""
        return db.query(BlogPost).filter(
            and_(BlogPost.slug == slug, BlogPost.status == PostStatus.PUBLISHED)
        ).first()
    
    def get_posts_list(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        status: Optional[PostStatus] = None,
        author_id: Optional[str] = None,
        search: Optional[str] = None,
        tag_slug: Optional[str] = None,
        published_only: bool = False
    ):
        """Get paginated list of blog posts with filtering."""
        query = db.query(BlogPost)
        
        # Apply filters
        if published_only or status == PostStatus.PUBLISHED:
            query = query.filter(BlogPost.status == PostStatus.PUBLISHED)
        elif status:
            query = query.filter(BlogPost.status == status)
        
        if author_id:
            query = query.filter(BlogPost.author_id == author_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term)
                )
            )
        
        if tag_slug:
            query = query.join(blog_post_tags).join(Tag).filter(Tag.slug == tag_slug)
        
        # Order by published date for published posts, created date otherwise
        if published_only or status == PostStatus.PUBLISHED:
            query = query.order_by(desc(BlogPost.published_at))
        else:
            query = query.order_by(desc(BlogPost.created_at))
        
        # Get paginated results using the utility
        items, page_info = PaginationUtils.create_paginated_response(query, page, per_page)
        
        # Return in the format expected by the API
        return {
            "items": items,
            "total": page_info.total_items,
            "page": page_info.current_page,
            "per_page": page_info.per_page,
            "total_pages": page_info.total_pages,
            "has_next": page_info.has_next,
            "has_prev": page_info.has_prev
        }
    
    def update_post(
        self,
        db: Session,
        post_id: str,
        user_id: str,
        update_data: Dict[str, Any],
        is_admin: bool = False
    ):
        """Update a blog post."""
        post = self.get_post_by_id(db, post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions
        if not is_admin and post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this post"
            )
        
        # Update fields
        updatable_fields = [
            "title", "content", "excerpt", "featured_image_url", 
            "meta_description", "status"
        ]
        
        try:
            # Handle title change (may require slug update)
            if "title" in update_data:
                new_title = update_data["title"].strip()
                if new_title != post.title:
                    post.title = new_title
                    # Update slug if title changed
                    post.slug = SlugUtils.update_slug_if_needed(
                        db, post.slug, new_title, 
                        lambda db, slug: self._check_slug_exists_excluding(db, slug, post_id)
                    )
            
            # Handle status change
            if "status" in update_data:
                new_status = update_data["status"]
                if new_status != post.status:
                    post.status = new_status
                    if new_status == PostStatus.PUBLISHED and not post.published_at:
                        post.published_at = datetime.utcnow()
                    elif new_status == PostStatus.DRAFT:
                        post.published_at = None
            
            # Update other fields
            for field, value in update_data.items():
                if field in updatable_fields and field not in ["title", "status"]:
                    setattr(post, field, value)
            
            # Handle tags update
            if "tag_ids" in update_data:
                self._update_post_tags(db, post.id, update_data["tag_ids"])
            
            post.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(post)
            return post
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A post with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Post update failed due to conflict"
                )
    
    def delete_post(
        self,
        db: Session,
        post_id: str,
        user_id: str,
        is_admin: bool = False
    ) -> bool:
        """Delete a blog post."""
        post = self.get_post_by_id(db, post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions
        if not is_admin and post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        # Remove tag associations first
        db.execute(blog_post_tags.delete().where(blog_post_tags.c.blog_post_id == post_id))
        
        # Delete the post
        db.delete(post)
        db.commit()
        return True
    
    def publish_post(self, db: Session, post_id: str, user_id: str):
        """Publish a draft post."""
        return self.update_post(
            db, post_id, user_id, {"status": PostStatus.PUBLISHED}
        )
    
    def unpublish_post(self, db: Session, post_id: str, user_id: str):
        """Unpublish a published post (revert to draft)."""
        return self.update_post(
            db, post_id, user_id, {"status": PostStatus.DRAFT}
        )
    
    def get_posts_count(
        self,
        db: Session,
        status: Optional[PostStatus] = None,
        author_id: Optional[str] = None
    ) -> int:
        """Get total count of blog posts with filtering."""
        query = db.query(BlogPost)
        
        if status:
            query = query.filter(BlogPost.status == status)
        
        if author_id:
            query = query.filter(BlogPost.author_id == author_id)
        
        return query.count()
    
    def get_featured_posts(self, db: Session, limit: int = 5):
        """Get featured published posts."""
        # This is a placeholder implementation
        # You might add a 'featured' boolean field to the BlogPost model
        return db.query(BlogPost).filter(
            BlogPost.status == PostStatus.PUBLISHED
        ).order_by(desc(BlogPost.published_at)).limit(limit).all()
    
    def _check_slug_exists(self, db: Session, slug: str) -> bool:
        """Check if a slug already exists."""
        return db.query(BlogPost).filter(BlogPost.slug == slug).first() is not None
    
    def _check_slug_exists_excluding(self, db: Session, slug: str, exclude_id: str) -> bool:
        """Check if slug exists excluding a specific post ID."""
        return db.query(BlogPost).filter(
            and_(BlogPost.slug == slug, BlogPost.id != exclude_id)
        ).first() is not None
    
    def _add_tags_to_post(self, db: Session, post_id: str, tag_ids: List[int]) -> None:
        """Add tags to a blog post."""
        # Verify tags exist
        existing_tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        existing_tag_ids = [tag.id for tag in existing_tags]
        
        # Add associations
        for tag_id in existing_tag_ids:
            db.execute(blog_post_tags.insert().values(
                blog_post_id=post_id, tag_id=tag_id
            ))
    
    def _update_post_tags(self, db: Session, post_id: str, tag_ids: List[int]) -> None:
        """Update tags for a blog post (replace all)."""
        # Remove existing associations
        db.execute(blog_post_tags.delete().where(blog_post_tags.c.blog_post_id == post_id))
        
        # Add new associations
        if tag_ids:
            self._add_tags_to_post(db, post_id, tag_ids)


# Global service instance
blog_post_service = BlogPostService()