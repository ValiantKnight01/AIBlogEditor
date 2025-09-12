"""
Authentication API endpoints.
Handles user authentication (login, logout, refresh token).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.schemas.auth_schemas import UserLogin, TokenResponse, LoginResponse
from src.schemas.user_schemas import UserResponse

# Initialize services
auth_service = AuthService()
user_service = UserService()
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Authenticates user credentials and returns access/refresh tokens.
    Sets refresh token as secure HTTP-only cookie.
    """
    # Authenticate user
    user = user_service.authenticate_user(
        db=db, 
        email=user_credentials.email, 
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,  # Convert to seconds
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )