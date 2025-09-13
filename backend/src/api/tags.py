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
    TagUpdate
)

router = APIRouter(prefix="/api/v1", tags=["Tags"])


@router.get("/tags", response_model=List[TagResponse])
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
        tags_result = service.get_tags_list(
            db=db,
            search=search,
            page=page,
            per_page=limit
        )
        
        # Handle tuple return format
        if isinstance(tags_result, tuple):
            tags, page_info = tags_result
        else:
            tags = tags_result
        
        return [TagResponse.model_validate(tag) for tag in tags]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tags: {str(e)}"
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


@router.get("/tags/{slug}", response_model=TagResponse)
async def get_tag(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by slug.
    
    Public endpoint - no authentication required.
    """
    service = TagService()
    
    try:
        tag = service.get_tag_by_slug(db=db, slug=slug)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return TagResponse.model_validate(tag)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tag: {str(e)}"
        )


@router.put("/tags/{slug}", response_model=TagResponse)
async def update_tag(
    slug: str,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a tag by slug.
    
    Requires authentication. Only authenticated users can update tags.
    """
    service = TagService()
    
    try:
        tag = service.update_tag(
            db=db,
            slug=slug,
            **tag_data.model_dump(exclude_unset=True)
        )
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return TagResponse.model_validate(tag)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
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
            detail=f"Failed to update tag: {str(e)}"
        )


@router.delete("/tags/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag by slug.
    
    Requires authentication. Only authenticated users can delete tags.
    """
    service = TagService()
    
    try:
        success = service.delete_tag(db=db, slug=slug)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return None  # 204 No Content
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tag: {str(e)}"
        )


@router.get("/tags/{slug}", response_model=TagResponse)
async def get_tag(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by slug.
    
    Public endpoint - no authentication required.
    """
    service = TagService()
    
    try:
        tag = service.get_tag_by_slug(db=db, slug=slug)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return TagResponse.model_validate(tag)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tag: {str(e)}"
        )


@router.put("/tags/{slug}", response_model=TagResponse)
async def update_tag(
    slug: str,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a tag by slug.
    
    Requires authentication. Only authenticated users can update tags.
    """
    service = TagService()
    
    try:
        tag = service.update_tag(
            db=db,
            slug=slug,
            **tag_data.model_dump(exclude_unset=True)
        )
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return TagResponse.model_validate(tag)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
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
            detail=f"Failed to update tag: {str(e)}"
        )


@router.delete("/tags/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag by slug.
    
    Requires authentication. Only authenticated users can delete tags.
    """
    service = TagService()
    
    try:
        success = service.delete_tag(db=db, slug=slug)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return None  # 204 No Content
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tag: {str(e)}"
        )