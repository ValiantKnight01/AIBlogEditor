"""
Authentication API endpoints.
Handles user authentication (login, logout, refresh token).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

# Import exceptions
from src.utils.exceptions import AuthErrors

# Lazy imports to avoid circular dependencies
def get_database_session():
    from src.database import get_db
    return get_db

def get_auth_service():
    from src.services.auth_service import AuthService
    return AuthService()

def get_user_service():
    from src.services.user_service import UserService
    return UserService()

def get_auth_schemas():
    from src.schemas.auth_schemas import UserLogin, TokenResponse, LoginResponse
    return UserLogin, TokenResponse, LoginResponse

def get_user_schemas():
    from src.schemas.user_schemas import UserResponse
    return UserResponse

security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", status_code=200)
async def login(
    user_credentials: dict,
    response: Response,
    db: Session = Depends(get_database_session())
):
    """
    User login endpoint.
    
    Authenticates user credentials and returns access/refresh tokens.
    Sets refresh token as secure HTTP-only cookie.
    """
    # Get services and schemas
    auth_service = get_auth_service()
    user_service = get_user_service()
    UserLogin, TokenResponse, LoginResponse = get_auth_schemas()
    UserResponse = get_user_schemas()
    
    # Validate input
    try:
        user_login = UserLogin(**user_credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}"
        )
    
    # Authenticate user
    user = user_service.authenticate_user(
        db=db, 
        email=user_login.email, 
        password=user_login.password
    )
    
    if not user:
        raise AuthErrors.INVALID_CREDENTIALS
    
    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "username": user.username}
    )
    
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id, "email": user.email}
    )
    
    # Set refresh token as secure HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=auth_service.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    # Return login response with user info
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": auth_service.access_token_expire_minutes * 60,  # Convert to seconds
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }


@router.post("/logout", status_code=204)
async def logout():
    """Logout endpoint - placeholder for now.""" 
    return {"message": "Logout successful"}


@router.post("/refresh", status_code=200)
async def refresh():
    """Refresh endpoint - placeholder for now."""
    return {
        "access_token": "new_access_token",
        "token_type": "bearer",
        "expires_in": 1800
    }