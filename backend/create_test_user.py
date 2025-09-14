#!/usr/bin/env python3
"""
Script to create a test user for development and testing.
"""
import sys
import os
sys.path.append('/app/src')
sys.path.append('/app')

from sqlalchemy.orm import Session
from src.database import get_db
from src.services.user_service import UserService

def create_test_user():
    """Create a test user."""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        user_service = UserService()
        
        # Create test user
        test_user = user_service.create_user(
            db=db,
            email="test@example.com",
            username="testuser",
            password="SecureP@ssw0rd!",
            full_name="Test User",
            bio="A test user for development"
        )
        
        print(f"Created test user: {test_user.email} (ID: {test_user.id})")
        return test_user
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()