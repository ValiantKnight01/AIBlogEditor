"""
Blog Posts API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.middleware.auth_middleware import get_current_user
from src.models.user import User
from src.models.blog_post import BlogPost, PostStatus
from src.services.blog_service import BlogPostService
from src.schemas.blog_schemas import (
    BlogPostResponse, 
    BlogPostCreate, 
    BlogPostUpdate,
    BlogPostListResponse
)

router = APIRouter(prefix="/api/v1", tags=["Blog Posts"])


@router.get("/posts", response_model=BlogPostListResponse)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts per page"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (draft, published)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of blog posts with optional filtering.
    
    Public endpoint - no authentication required.
    Returns published posts for public, all posts for authenticated users.
    """
    service = BlogPostService()
    
    try:
        # For public access, only show published posts unless status filter is specified
        published_only = status_filter != "draft"
        post_status = PostStatus(status_filter) if status_filter and status_filter in ["draft", "published"] else None
        
        result = service.get_posts_list(
            db=db,
            page=page,
            per_page=limit,
            tag_slug=tag,
            status=post_status,
            published_only=published_only
        )
        
        posts = [BlogPostResponse.model_validate(post) for post in result["items"]]
        
        return BlogPostListResponse(
            items=posts,
            total=result["total"],
            page=page,
            limit=limit,
            pages=result["total_pages"],
            has_next=result["has_next"],
            has_prev=result["has_prev"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list posts: {str(e)}"
        )


@router.post("/posts", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: BlogPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new blog post.
    
    Requires authentication. Only authenticated users can create posts.
    """
    service = BlogPostService()
    
    try:
        post = service.create_post(
            db=db,
            user_id=current_user.id,
            title=post_data.title,
            content=post_data.content,
            excerpt=post_data.excerpt,
            status=post_data.status,
            featured_image_url=str(post_data.featured_image_url) if post_data.featured_image_url else None,
            meta_description=post_data.meta_description,
            tag_ids=post_data.tag_ids
        )
        return BlogPostResponse.model_validate(post)
    except ValueError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A post with this slug already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/posts/{slug}", response_model=BlogPostResponse)
async def get_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific blog post by slug.
    
    Public endpoint - no authentication required.
    Returns published posts for public access.
    """
    service = BlogPostService()
    
    post = service.get_published_post_by_slug(db, slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # TODO: Increment view count if needed
    # service.increment_view_count(post.id)
    
    return BlogPostResponse.model_validate(post)


@router.put("/posts/{slug}", response_model=BlogPostResponse)
async def update_post(
    slug: str,
    post_data: BlogPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific blog post.
    
    Requires authentication. Only the post author can update the post.
    """
    service = BlogPostService()
    
    post = service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if current user owns the post
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )
    
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = post_data.model_dump(exclude_none=True)
        
        # Convert HttpUrl to string if present
        if 'featured_image_url' in update_dict and update_dict['featured_image_url']:
            update_dict['featured_image_url'] = str(update_dict['featured_image_url'])
        
        updated_post = service.update_post(
            db=db,
            post_id=post.id,
            user_id=current_user.id,
            update_data=update_dict
        )
        return BlogPostResponse.model_validate(updated_post)
    except ValueError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A post with this slug already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update post: {str(e)}"
        )


@router.delete("/posts/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific blog post.
    
    Requires authentication. Only the post author can delete the post.
    """
    service = BlogPostService()
    
    post = service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if current user owns the post
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    try:
        result = service.delete_post(
            db=db,
            post_id=post.id,
            user_id=current_user.id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )