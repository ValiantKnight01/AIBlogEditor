"""
Project service with CRUD and slug generation.
Handles project portfolio management, status updates, and slug operations.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status

from src.models.project import Project, ProjectStatus
from src.models.associations import project_tags
from src.models.tag import Tag
from src.utils.slug_utils import SlugUtils
from src.utils.pagination import PaginationUtils, PageInfo
from src.database import get_db


class ProjectService:
    """Service for project management operations."""
    
    def __init__(self):
        pass
    
    def create_project(
        self,
        db: Session,
        user_id: str,
        title: str,
        description: str,
        tech_stack: Optional[List[str]] = None,
        github_url: Optional[str] = None,
        live_url: Optional[str] = None,
        image_url: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.DRAFT,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        featured: bool = False,
        tag_ids: Optional[List[int]] = None
    ):
        """Create a new project."""
        # Generate unique slug from title
        slug = SlugUtils.create_unique_slug_from_title(
            db, title, self._check_slug_exists
        )
        
        # Create project
        project = Project(
            title=title.strip(),
            slug=slug,
            description=description,
            tech_stack=tech_stack or [],
            github_url=github_url,
            project_url=live_url,  # Use project_url instead of live_url
            image_url=image_url,
            creator_id=user_id,  # Use creator_id instead of author_id
            status=status,
            start_date=start_date,
            end_date=end_date,
            featured=featured  # Now included since it's in the model
        )
        
        try:
            db.add(project)
            db.flush()  # Get the project ID
            
            # Add tags if provided
            if tag_ids:
                self._add_tags_to_project(db, project.id, tag_ids)
            
            db.commit()
            db.refresh(project)
            return project
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A project with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project creation failed due to conflict"
                )
    
    def get_project_by_id(self, db: Session, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()
    
    def get_project_by_slug(self, db: Session, slug: str) -> Optional[Project]:
        """Get project by slug."""
        return db.query(Project).filter(Project.slug == slug).first()
    
    def get_published_project_by_slug(self, db: Session, slug: str) -> Optional[Project]:
        """Get published project by slug (for public access)."""
        return db.query(Project).filter(
            and_(Project.slug == slug, Project.status == ProjectStatus.PUBLISHED)
        ).first()
    
    def get_projects_list(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        status: Optional[ProjectStatus] = None,
        author_id: Optional[str] = None,
        search: Optional[str] = None,
        tech_filter: Optional[str] = None,
        tag_slug: Optional[str] = None,
        featured_only: bool = False,
        published_only: bool = False
    ):
        """Get paginated list of projects with filtering."""
        query = db.query(Project)
        
        # Apply filters
        if published_only or status == ProjectStatus.PUBLISHED:
            query = query.filter(Project.status == ProjectStatus.PUBLISHED)
        elif status:
            query = query.filter(Project.status == status)
        
        if author_id:
            query = query.filter(Project.author_id == author_id)
        
        if featured_only:
            query = query.filter(Project.featured == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Project.title.ilike(search_term),
                    Project.description.ilike(search_term)
                )
            )
        
        if tech_filter:
            # Search in JSON tech_stack array
            query = query.filter(Project.tech_stack.contains([tech_filter]))
        
        if tag_slug:
            query = query.join(project_tags).join(Tag).filter(Tag.slug == tag_slug)
        
        # Order by featured first, then created date
        query = query.order_by(desc(Project.featured), desc(Project.created_at))
        
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
    
    def update_project(
        self,
        db: Session,
        project_id: str,
        user_id: str,
        update_data: Dict[str, Any],
        is_admin: bool = False
    ):
        """Update a project."""
        project = self.get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check permissions
        if not is_admin and project.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this project"
            )
        
        # Update fields
        updatable_fields = [
            "title", "description", "tech_stack", "github_url", "live_url",
            "image_url", "status", "start_date", "end_date", "featured"
        ]
        
        try:
            # Handle title change (may require slug update)
            if "title" in update_data:
                new_title = update_data["title"].strip()
                if new_title != project.title:
                    project.title = new_title
                    # Update slug if title changed
                    project.slug = SlugUtils.update_slug_if_needed(
                        db, project.slug, new_title, 
                        lambda db, slug: self._check_slug_exists_excluding(db, slug, project_id)
                    )
            
            # Update other fields
            for field, value in update_data.items():
                if field in updatable_fields and field != "title":
                    setattr(project, field, value)
            
            # Handle tags update
            if "tag_ids" in update_data:
                self._update_project_tags(db, project.id, update_data["tag_ids"])
            
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            return project
            
        except IntegrityError as e:
            db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A project with this slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project update failed due to conflict"
                )
    
    def delete_project(
        self,
        db: Session,
        project_id: str,
        user_id: str,
        is_admin: bool = False
    ) -> bool:
        """Delete a project."""
        project = self.get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check permissions
        if not is_admin and project.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )
        
        # Remove tag associations first
        db.execute(project_tags.delete().where(project_tags.c.project_id == project_id))
        
        # Delete the project
        db.delete(project)
        db.commit()
        return True
    
    def publish_project(self, db: Session, project_id: str, user_id: str):
        """Publish a draft project."""
        return self.update_project(
            db, project_id, user_id, {"status": ProjectStatus.PUBLISHED}
        )
    
    def unpublish_project(self, db: Session, project_id: str, user_id: str):
        """Unpublish a published project (revert to draft)."""
        return self.update_project(
            db, project_id, user_id, {"status": ProjectStatus.DRAFT}
        )
    
    def set_featured_status(
        self, 
        db: Session, 
        project_id: str, 
        featured: bool, 
        user_id: str,
        is_admin: bool = False
    ):
        """Set or unset project as featured."""
        return self.update_project(
            db, project_id, user_id, {"featured": featured}, is_admin
        )
    
    def get_projects_count(
        self,
        db: Session,
        status: Optional[ProjectStatus] = None,
        author_id: Optional[str] = None,
        featured_only: bool = False
    ) -> int:
        """Get total count of projects with filtering."""
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        
        if author_id:
            query = query.filter(Project.author_id == author_id)
        
        if featured_only:
            query = query.filter(Project.featured == True)
        
        return query.count()
    
    def get_featured_projects(self, db: Session, limit: int = 6):
        """Get featured published projects."""
        return db.query(Project).filter(
            and_(Project.status == ProjectStatus.PUBLISHED, Project.featured == True)
        ).order_by(desc(Project.created_at)).limit(limit).all()
    
    def get_projects_by_tech_stack(
        self, 
        db: Session, 
        tech: str, 
        limit: int = 10
    ):
        """Get projects that use a specific technology."""
        return db.query(Project).filter(
            and_(
                Project.status == ProjectStatus.PUBLISHED,
                Project.tech_stack.contains([tech])
            )
        ).order_by(desc(Project.created_at)).limit(limit).all()
    
    def get_unique_tech_stack_items(self, db: Session) -> List[str]:
        """Get all unique technologies used across projects."""
        # This is a simplified version - in PostgreSQL you might use jsonb_array_elements
        projects = db.query(Project).filter(
            Project.status == ProjectStatus.PUBLISHED
        ).all()
        
        tech_set = set()
        for project in projects:
            if project.tech_stack:
                tech_set.update(project.tech_stack)
        
        return sorted(list(tech_set))
    
    def _check_slug_exists(self, db: Session, slug: str) -> bool:
        """Check if a slug already exists."""
        return db.query(Project).filter(Project.slug == slug).first() is not None
    
    def _check_slug_exists_excluding(self, db: Session, slug: str, exclude_id: str) -> bool:
        """Check if slug exists excluding a specific project ID."""
        return db.query(Project).filter(
            and_(Project.slug == slug, Project.id != exclude_id)
        ).first() is not None
    
    def _add_tags_to_project(self, db: Session, project_id: str, tag_ids: List[int]) -> None:
        """Add tags to a project."""
        # Verify tags exist
        existing_tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        existing_tag_ids = [tag.id for tag in existing_tags]
        
        # Add associations
        for tag_id in existing_tag_ids:
            db.execute(project_tags.insert().values(
                project_id=project_id, tag_id=tag_id
            ))
    
    def _update_project_tags(self, db: Session, project_id: str, tag_ids: List[int]) -> None:
        """Update tags for a project (replace all)."""
        # Remove existing associations
        db.execute(project_tags.delete().where(project_tags.c.project_id == project_id))
        
        # Add new associations
        if tag_ids:
            self._add_tags_to_project(db, project_id, tag_ids)


# Global service instance
project_service = ProjectService()