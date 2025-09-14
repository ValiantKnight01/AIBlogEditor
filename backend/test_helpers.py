#!/usr/bin/env python3
"""
Helper functions for testing with authentication tokens.
"""
import sys
import os
sys.path.append('/app/src')
sys.path.append('/app')

from sqlalchemy.orm import Session
from src.database import get_db
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.config import settings

def get_test_auth_token():
    """Get a valid JWT token for the test user."""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        user_service = UserService()
        auth_service = AuthService()
        
        # Get the test user
        user = user_service.get_user_by_email(db, "test@example.com")
        if not user:
            print("Test user not found. Run create_test_user.py first.")
            return None
        
        # Generate token
        token_data = auth_service.create_login_tokens(str(user.id), user.email)
        return f"Bearer {token_data['access_token']}"
        
    except Exception as e:
        print(f"Error generating test token: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    token = get_test_auth_token()
    if token:
        print(f"Test token: {token}")
    else:
        print("Failed to generate test token")