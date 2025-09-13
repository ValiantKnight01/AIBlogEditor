#!/usr/bin/env python3

import sys
import os
import asyncio

# Add backend src to path for imports
sys.path.insert(0, '/app/src')

from database import get_db
from models.user_models import User
from services.user_service import UserService

def create_test_user():
    """Create a test user for contract tests."""
    db = next(get_db())
    user_service = UserService()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "testuser@example.com").first()
    if existing_user:
        print("Test user already exists!")
        return
    
    # Create test user
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
        "bio": "Test user for contract tests",
        "is_active": True
    }
    
    try:
        user = user_service.create_user(db, user_data)
        print(f"Created test user: {user.email}")
        db.commit()
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()