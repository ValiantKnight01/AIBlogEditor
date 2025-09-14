"""
User profile API endpoints.
Handles user profile retrieval and updates.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from database import get_db
from models.user import User
from middleware.auth_middleware import get_current_user
from schemas.user_schemas import UserResponse

# Initialize router
router = APIRouter(prefix="/api/v1/users", tags=["users"])


# Request/Response models
class UserUpdateRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile information.
    
    Returns the authenticated user's profile data without sensitive information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information.
    
    Allows updating of profile fields like full_name, bio, avatar_url.
    Email and username updates are not allowed through this endpoint.
    """
    # Convert Pydantic model to dict, excluding None values
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        # Return current user if no valid updates provided
        return current_user
    
    # Update user attributes
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    # Save changes to database
    db.commit()
    db.refresh(current_user)
    
    return current_user