"""
Password hashing and validation service.
Provides secure password hashing and verification functionality.
"""

import secrets
import re
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import HTTPException, status


class SecurityService:
    """Service for handling password security operations."""
    
    def __init__(self):
        # Password hashing context with bcrypt
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Password strength requirements
        self.min_password_length = 8
        self.max_password_length = 128
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")
        
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not plain_password or not hashed_password:
            return False
        
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if a password hash needs to be updated."""
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception:
            return True
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength and return detailed feedback.
        Returns dict with 'is_valid' boolean and 'errors' list.
        """
        errors = []
        
        # Check length
        if len(password) < self.min_password_length:
            errors.append(f"Password must be at least {self.min_password_length} characters long")
        
        if len(password) > self.max_password_length:
            errors.append(f"Password must be no more than {self.max_password_length} characters long")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{2,}',  # Three or more consecutive identical characters
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains weak patterns (avoid repeated or sequential characters)")
                break
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_password_for_registration(self, password: str) -> None:
        """
        Validate password for registration and raise HTTPException if invalid.
        """
        validation_result = self.validate_password_strength(password)
        
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": validation_result["errors"]
                }
            )
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    def generate_reset_token(self) -> str:
        """Generate a secure token for password reset."""
        return self.generate_secure_token(32)
    
    def is_password_compromised(self, password: str) -> bool:
        """
        Check if password is in common compromised password lists.
        This is a placeholder implementation - in production, you might
        want to integrate with services like HaveIBeenPwned API.
        """
        # Common weak passwords to reject
        common_passwords = {
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey",
            "dragon", "1234567890", "football", "iloveyou", "admin123",
            "welcome123", "password1", "qwerty123", "123123", "000000"
        }
        
        return password.lower() in common_passwords
    
    def validate_password_change(self, old_password: str, new_password: str, current_hash: str) -> None:
        """
        Validate password change request.
        Checks old password and validates new password strength.
        """
        # Verify old password
        if not self.verify_password(old_password, current_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Ensure new password is different
        if old_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Check if new password is compromised
        if self.is_password_compromised(new_password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password is too common and easily compromised. Please choose a more secure password."
            )
        
        # Validate new password strength
        self.validate_password_for_registration(new_password)
    
    def sanitize_input(self, input_string: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize user input by removing/escaping potentially dangerous characters.
        """
        if not input_string:
            return ""
        
        # Remove null bytes and control characters
        sanitized = input_string.replace('\x00', '').strip()
        
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized


# Global service instance
security_service = SecurityService()