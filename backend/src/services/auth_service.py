"""
JWT token service with refresh logic.
Handles JWT token creation, validation, and refresh operations.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status


class AuthService:
    """Service for handling JWT authentication operations."""
    
    def __init__(self):
        # Configuration from environment variables
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, expected_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing expiration"
                )
                
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access token using refresh token."""
        # Verify refresh token
        payload = self.verify_token(refresh_token, "refresh")
        
        # Extract user data (exclude token metadata)
        user_data = {
            key: value for key, value in payload.items()
            if key not in ["exp", "type"]
        }
        
        # Create new access token
        new_access_token = self.create_access_token(user_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
    def create_login_tokens(self, user_id: int, email: str) -> Dict[str, str]:
        """Create both access and refresh tokens for login."""
        user_data = {
            "sub": str(user_id),
            "email": email,
            "user_id": user_id
        }
        
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """Extract user information from access token."""
        payload = self.verify_token(token, "access")
        
        return {
            "user_id": payload.get("sub") or payload.get("user_id"),  # Support both 'sub' and 'user_id' fields
            "email": payload.get("email"),
            "sub": payload.get("sub")
        }


# Global service instance
auth_service = AuthService()