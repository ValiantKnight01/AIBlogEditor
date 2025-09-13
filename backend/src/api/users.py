"""
User profile API endpoints.
Handles user profile retrieval and updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import sys
import os

# Simple database connection to avoid circular imports
def get_db():
    """Simple database connection without circular imports."""
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple JWT validation to avoid circular imports
def get_current_user_simple(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        from jose import jwt, JWTError
        
        # JWT configuration
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        algorithm = "HS256"
        
        # Decode token
        token = credentials.credentials
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")  # JWT standard uses 'sub' for subject
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.execute(text("""
            SELECT id, email, username, full_name, bio, avatar_url, 
                   is_active, is_admin, created_at, updated_at
            FROM users WHERE id = :user_id AND is_active = true
        """), {"user_id": user_id}).fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Initialize router
router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
async def get_current_user(
    current_user = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    Get current user profile information.
    
    Returns the authenticated user's profile data without sensitive information.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }


@router.put("/me")
async def update_current_user(
    user_update: dict,
    current_user = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information.
    
    Allows updating of profile fields like full_name, bio, social links, etc.
    Email and username updates are not allowed through this endpoint.
    """
    # Allowed fields that can be updated
    updatable_fields = ["full_name", "bio", "avatar_url"]
    
    # Filter update data to only allowed fields
    update_data = {k: v for k, v in user_update.items() if k in updatable_fields}
    
    if not update_data:
        # Return current user if no valid updates provided
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "bio": current_user.bio,
            "avatar_url": current_user.avatar_url,
            "is_active": current_user.is_active,
            "is_admin": current_user.is_admin,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
        }
    
    # Build update SQL
    set_clauses = []
    params = {"user_id": current_user.id}
    
    for field, value in update_data.items():
        set_clauses.append(f"{field} = :{field}")
        params[field] = value
    
    # Add updated_at
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    
    # Execute update
    db.execute(text(f"""
        UPDATE users 
        SET {', '.join(set_clauses)}
        WHERE id = :user_id
    """), params)
    db.commit()
    
    # Get updated user
    updated_user = db.execute(text("""
        SELECT id, email, username, full_name, bio, avatar_url, 
               is_active, is_admin, created_at, updated_at
        FROM users WHERE id = :user_id
    """), {"user_id": current_user.id}).fetchone()
    
    return {
        "id": str(updated_user.id),
        "email": updated_user.email,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "bio": updated_user.bio,
        "avatar_url": updated_user.avatar_url,
        "is_active": updated_user.is_active,
        "is_admin": updated_user.is_admin,
        "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None,
        "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
    }