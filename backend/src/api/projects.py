"""
Projects API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.project import Project, ProjectStatus
from services.project_service import ProjectService
from schemas.project_schemas import (
    ProjectResponse, 
    ProjectCreate, 
    ProjectUpdate,
    ProjectListResponse
)

router = APIRouter(prefix="/api/v1", tags=["Projects"])


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of projects per page"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    status: Optional[str] = Query(None, description="Filter by status (planning, in_progress, completed, on_hold)"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of projects with optional filtering.
    
    Public endpoint - no authentication required.
    Returns all projects for public access.
    """
    service = ProjectService()
    
    # Convert status string to enum if provided
    status_filter = None
    if status:
        try:
            status_filter = ProjectStatus(status.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status: {status}"
            )
    
    # Get paginated projects using the service method
    result = service.get_projects_list(
        db=db,
        page=page,
        per_page=limit,
        status=status_filter,
        tag_slug=tag,
        featured_only=featured or False
    )
    
    return ProjectListResponse(
        projects=result["items"],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
        has_next=result["has_next"],
        has_prev=result["has_prev"]
    )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    
    Requires authentication. Only authenticated users can create projects.
    """
    service = ProjectService()
    
    try:
        project = service.create_project(
            db=db,
            user_id=current_user.id,
            title=project_data.title,
            description=project_data.description,
            tech_stack=project_data.tech_stack,
            github_url=str(project_data.github_url) if project_data.github_url else None,
            live_url=str(project_data.live_url) if project_data.live_url else None,
            image_url=str(project_data.image_url) if project_data.image_url else None,
            status=project_data.status,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            featured=project_data.featured,
            tag_ids=project_data.tag_ids
        )
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A project with this slug already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/projects/{slug}", response_model=ProjectResponse)
async def get_project(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific project by slug.
    
    Public endpoint - no authentication required.
    """
    service = ProjectService()
    
    project = service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse.model_validate(project)


@router.put("/projects/{slug}", response_model=ProjectResponse)
async def update_project(
    slug: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific project.
    
    Requires authentication. Only the project owner can update the project.
    """
    service = ProjectService()
    
    project = service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if current user owns the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own projects"
        )
    
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = project_data.model_dump(exclude_none=True)
        
        # Convert HttpUrl fields to string if present
        for field in ['github_url', 'live_url', 'image_url']:
            if field in update_dict and update_dict[field]:
                update_dict[field] = str(update_dict[field])
        
        updated_project = service.update_project(
            db=db,
            project_id=project.id,
            user_id=current_user.id,
            update_data=update_dict
        )
        return ProjectResponse.model_validate(updated_project)
    except ValueError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A project with this slug already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/projects/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific project.
    
    Requires authentication. Only the project owner can delete the project.
    """
    service = ProjectService()
    
    project = service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if current user owns the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own projects"
        )
    
    try:
        result = service.delete_project(
            db=db,
            project_id=project.id,
            user_id=current_user.id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )