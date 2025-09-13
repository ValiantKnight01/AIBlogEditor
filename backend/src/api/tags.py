"""
Tags API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.tag import Tag
from services.tag_service import TagService
from schemas.tag_schemas import (
    TagResponse, 
    TagCreate,
    TagListResponse
)

router = APIRouter(prefix="/api/v1", tags=["Tags"])


@router.get("/tags", response_model=TagListResponse)
async def list_tags(
    used_only: bool = Query(False, description="Only return tags that are used in posts or projects"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Number of tags per page"),
    search: Optional[str] = Query(None, description="Search term"),
    db: Session = Depends(get_db)
):
    """
    Get list of all tags with usage counts.
    
    Public endpoint - no authentication required.
    Returns all tags or only used tags based on query parameter.
    """
    service = TagService()
    
    try:
        result = service.get_tags_list(
            db=db,
            page=page,
            per_page=limit,
            search=search
        )
        
        # Filter for used tags only if requested
        if used_only:
            result["items"] = [tag for tag in result["items"] if tag.usage_count > 0]
        
        return TagListResponse(
            tags=result["items"],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            total_pages=result["total_pages"],
            has_next=result["has_next"],
            has_prev=result["has_prev"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tags: {str(e)}"
        )


@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag.
    
    Requires authentication. Only authenticated users can create tags.
    """
    service = TagService()
    
    try:
        tag = service.create_tag(
            db=db,
            name=tag_data.name,
            color=tag_data.color,
            description=tag_data.description
        )
        return TagResponse.model_validate(tag)
    except ValueError as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tag with this name already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tag: {str(e)}"
        )