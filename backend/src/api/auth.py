"""
Authentication API endpoints.
Handles user authentication (login, logout, refresh token).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

# Import exceptions
from utils.exceptions import AuthErrors, AuthenticationError

# Lazy imports to avoid circular dependencies
def get_database_session():
    from database import get_db
    return get_db

def get_auth_service():
    from services.auth_service import AuthService
    return AuthService()

def get_user_service():
    from services.user_service import UserService
    return UserService()

def get_auth_schemas():
    from schemas.auth_schemas import UserLogin, TokenResponse, LoginResponse
    return UserLogin, TokenResponse, LoginResponse

def get_user_schemas():
    from schemas.user_schemas import UserResponse
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
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session())
):
    """
    User logout endpoint.
    
    Clears the refresh token cookie and invalidates the session.
    Returns 204 No Content on success, 401 if no valid token provided.
    """
    # Check if authorization header is present
    if not credentials:
        raise AuthErrors.MISSING_TOKEN
    
    try:
        # Get auth service
        auth_service = get_auth_service()
        
        # Validate the access token (ensure user is authenticated)
        token = credentials.credentials
        user_data = auth_service.get_user_from_token(token)
        
        # Clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        # Return 204 No Content (no response body)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        # If token is invalid, still return 401 
        raise AuthErrors.INVALID_TOKEN


@router.post("/refresh", status_code=200) 
async def refresh(
    refresh_data: dict,
    response: Response,
    db: Session = Depends(get_database_session())
):
    """
    Refresh access token endpoint.
    
    Uses refresh token from request body to generate new access token.
    Returns new access token with token type and expiration info.
    """
    # Get auth service and schemas
    auth_service = get_auth_service()
    
    # Get refresh token from request body
    refresh_token = refresh_data.get("refresh_token") if refresh_data else None
    
    if not refresh_token:
        raise AuthenticationError(
            detail="Refresh token required",
            error_code="MISSING_REFRESH_TOKEN"
        )
    
    try:
        # Generate new access token using refresh token
        token_data = auth_service.refresh_access_token(refresh_token)
        
        # Return token response
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "expires_in": auth_service.access_token_expire_minutes * 60  # Convert to seconds
        }
        
    except Exception as e:
        raise AuthErrors.INVALID_REFRESH_TOKEN