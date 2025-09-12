"""
User service with CRUD operations.
Handles user management, profile updates, and authentication-related operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from models.user import User
from services.security_service import security_service
from database import get_db


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        self.security_service = security_service
    
    def create_user(
        self,
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        bio: Optional[str] = None
    ) -> User:
        """Create a new user account."""
        # Validate password strength
        self.security_service.validate_password_for_registration(password)
        
        # Check if password is compromised
        if self.security_service.is_password_compromised(password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password is too common and easily compromised. Please choose a more secure password."
            )
        
        # Hash password
        password_hash = self.security_service.hash_password(password)
        
        # Create user instance
        user = User(
            email=email.lower().strip(),
            username=username.strip(),
            password_hash=password_hash,
            full_name=full_name.strip() if full_name else None,
            bio=bio.strip() if bio else None,
            is_active=True,
            is_admin=False
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email address already registered"
                )
            elif "username" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User registration failed due to conflict"
                )
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return db.query(User).filter(User.email == email.lower()).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(db, email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.security_service.verify_password(password, user.password_hash):
            return None
        
        # Check if password hash needs updating
        if self.security_service.needs_rehash(user.password_hash):
            user.password_hash = self.security_service.hash_password(password)
            db.commit()
        
        return user
    
    def update_user_profile(
        self,
        db: Session,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> User:
        """Update user profile information."""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Fields that can be updated
        updatable_fields = [
            "full_name", "bio", "website_url", "github_url", 
            "twitter_url", "linkedin_url", "location"
        ]
        
        try:
            for field, value in update_data.items():
                if field in updatable_fields and hasattr(user, field):
                    # Sanitize string inputs
                    if isinstance(value, str):
                        value = self.security_service.sanitize_input(value, 500)
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile update failed due to conflict"
            )
    
    def change_password(
        self,
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password."""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate password change
        self.security_service.validate_password_change(
            old_password, new_password, user.password_hash
        )
        
        # Update password
        user.password_hash = self.security_service.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    def deactivate_user(self, db: Session, user_id: str) -> bool:
        """Deactivate a user account."""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    def activate_user(self, db: Session, user_id: str) -> bool:
        """Activate a user account (admin only)."""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    def get_users_list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True
    ) -> List[User]:
        """Get paginated list of users (admin only)."""
        query = db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_users_count(self, db: Session, active_only: bool = True) -> int:
        """Get total count of users."""
        query = db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.count()
    
    def is_email_available(self, db: Session, email: str) -> bool:
        """Check if email address is available for registration."""
        user = self.get_user_by_email(db, email)
        return user is None
    
    def is_username_available(self, db: Session, username: str) -> bool:
        """Check if username is available for registration."""
        user = self.get_user_by_username(db, username)
        return user is None


# Global service instance
user_service = UserService()