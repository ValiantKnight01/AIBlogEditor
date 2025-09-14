#!/usr/bin/env python3
"""
Initialization script to set up the database with admin user and test data.
"""
import sys
import os
import time
sys.path.append('/app/src')
sys.path.append('/app')

from sqlalchemy.exc import OperationalError
from src.database import SessionLocal, engine

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready."""
    retries = 0
    while retries < max_retries:
        try:
            # Try to connect to the database
            db = SessionLocal()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
            print("Database is ready!")
            return True
        except OperationalError:
            retries += 1
            print(f"Database not ready, waiting... ({retries}/{max_retries})")
            time.sleep(delay)
    
    print("Database connection failed after max retries")
    return False

def init_database():
    """Initialize database with admin user and test data."""
    if not wait_for_db():
        print("Failed to connect to database, exiting...")
        sys.exit(1)
    
    try:
        # Run database migrations first
        print("Running database migrations...")
        import subprocess
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, cwd='/app')
        if result.returncode != 0:
            print(f"Migration failed: {result.stderr}")
            raise Exception(f"Migration failed: {result.stderr}")
        print("Database migrations completed successfully!")
        
        # Create admin user first
        print("Creating admin user...")
        from create_admin_user import create_admin_user
        create_admin_user()
        
        # Create test data
        print("Creating test data...")
        from create_test_data import create_test_data
        create_test_data()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    init_database()