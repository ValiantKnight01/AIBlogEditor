"""
User authentication middleware.
Handles JWT token validation and user authentication for protected endpoints.
"""

from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from services.auth_service import auth_service
from utils.exceptions import AuthErrors, AuthenticationError
from utils.security import CustomHTTPBearer


# Security scheme for JWT Bearer tokens
security = CustomHTTPBearer()


class AuthMiddleware:
    """Middleware for handling user authentication."""
    
    def __init__(self):
        self.auth_service = auth_service
    
    async def get_current_user_optional(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """
        Get current user from JWT token (optional - returns None if no token).
        Used for endpoints that work both with and without authentication.
        """
        if not credentials:
            return None
        
        try:
            # Extract token from Bearer scheme
            token = credentials.credentials
            
            # Verify and decode token
            user_data = self.auth_service.get_user_from_token(token)
            user_id = user_data.get("user_id")
            
            if not user_id:
                return None
            
            # Fetch user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Check if user account is active
            if not user.is_active:
                return None
            
            return user
            
        except HTTPException:
            return None
        except Exception:
            return None
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Get current user from JWT token (required - raises exception if invalid).
        Used for protected endpoints that require authentication.
        """
        if not credentials:
            raise AuthErrors.MISSING_TOKEN
        
        try:
            # Extract token from Bearer scheme
            token = credentials.credentials
            
            # Verify and decode token
            user_data = self.auth_service.get_user_from_token(token)
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise AuthenticationError(
                    detail="Invalid token payload",
                    error_code="INVALID_TOKEN_PAYLOAD"
                )
            
            # Fetch user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise AuthErrors.USER_NOT_FOUND
            
            # Check if user account is active
            if not user.is_active:
                raise AuthErrors.ACCOUNT_DEACTIVATED
            
            return user
            
        except AuthenticationError:
            raise
        except HTTPException as e:
            # Handle auth service HTTPExceptions and convert them
            if e.status_code == 401:
                if "expired" in e.detail.lower():
                    raise AuthErrors.EXPIRED_TOKEN
                elif "invalid" in e.detail.lower():
                    raise AuthErrors.INVALID_TOKEN
                else:
                    raise AuthenticationError(
                        detail=e.detail,
                        error_code="AUTHENTICATION_FAILED"
                    )
            raise e
        except Exception as e:
            raise AuthenticationError(
                detail="Token validation failed",
                error_code="TOKEN_VALIDATION_FAILED"
            )
    
    async def get_current_admin_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get current user and verify admin privileges.
        Used for admin-only endpoints.
        """
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return current_user
    
    async def verify_user_owns_resource(
        self,
        resource_user_id: int,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Verify that the current user owns a specific resource.
        Used for user-specific resource endpoints.
        """
        if current_user.id != resource_user_id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        
        return current_user


# Global middleware instance
auth_middleware = AuthMiddleware()

# Convenience dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user (required)."""
    return await auth_middleware.get_current_user(credentials, db)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated (optional)."""
    return await auth_middleware.get_current_user_optional(credentials, db)


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated admin user."""
    return await auth_middleware.get_current_admin_user(current_user)


def require_user_owns_resource(resource_user_id: int):
    """Dependency factory for resource ownership verification."""
    async def verify_ownership(
        current_user: User = Depends(get_current_user)
    ) -> User:
        return await auth_middleware.verify_user_owns_resource(resource_user_id, current_user)
    
    return verify_ownership


# Additional middleware functions for common patterns
async def validate_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate refresh token and return payload."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token, "refresh")
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def rate_limit_check(request: Request):
    """
    Basic rate limiting check (placeholder).
    In production, implement proper rate limiting with Redis or similar.
    """
    # Placeholder for rate limiting logic
    # You might integrate with libraries like slowapi or implement custom logic
    pass