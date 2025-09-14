#!/usr/bin/env python3
"""
Script to create admin user from environment variables.
"""
import sys
import os
sys.path.append('/app/src')
sys.path.append('/app')

from sqlalchemy.orm import Session

# Import database connection
from src.database import SessionLocal

# Import services
from src.services.user_service import UserService

def create_admin_user():
    """Create admin user from environment variables."""
    # Get database session
    db = SessionLocal()
    
    try:
        print("Creating admin user...")
        
        # Get admin credentials from environment variables
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'AdminP@ss_w0rd!')
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_full_name = os.getenv('ADMIN_FULL_NAME', 'Admin User')
        
        print(f"Admin email: {admin_email}")
        
        # Services
        user_service = UserService()
        
        # Check if admin user already exists
        admin_user = user_service.get_user_by_email(db, admin_email)
        if admin_user:
            print(f"Admin user already exists: {admin_user.email}")
            return admin_user
        
        # Create admin user
        admin_user = user_service.create_user(
            db=db,
            email=admin_email,
            username=admin_username,
            password=admin_password,
            full_name=admin_full_name,
            bio="Administrator user"
        )
        print(f"Created admin user: {admin_user.email}")
        
        return admin_user
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()