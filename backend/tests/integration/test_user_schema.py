"""
Database schema tests for User entity.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import settings


@pytest.fixture
def db_engine():
    """Create a database engine for testing."""
    # Use main database for integration tests since Docker environment is isolated
    engine = create_engine(settings.database.database_url)
    return engine


@pytest.fixture  
def db_session(db_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


class TestUserSchema:
    """Test database schema for User entity."""

    @pytest.mark.integration
    def test_user_table_exists(self, db_engine):
        """Test that users table exists in database."""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        assert "users" in tables, "users table should exist in database"

    @pytest.mark.integration
    def test_user_table_columns(self, db_engine):
        """Test that users table has all required columns."""
        inspector = inspect(db_engine)
        columns = inspector.get_columns("users")
        column_names = {col["name"] for col in columns}
        
        expected_columns = {
            "id",
            "email",
            "username", 
            "password_hash",
            "full_name",
            "bio",
            "avatar_url",
            "is_active",
            "created_at",
            "updated_at"
        }
        
        assert expected_columns.issubset(column_names), (
            f"Missing columns in users table. Expected: {expected_columns}, "
            f"Found: {column_names}"
        )

    @pytest.mark.integration
    def test_user_table_column_types(self, db_engine):
        """Test that users table columns have correct data types."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("users")}
        
        # Test UUID primary key
        assert columns["id"]["type"].python_type.__name__ in ("UUID", "str"), (
            "id column should be UUID type"
        )
        
        # Test string columns
        for col_name in ["email", "username", "password_hash"]:
            assert "VARCHAR" in str(columns[col_name]["type"]).upper(), (
                f"{col_name} should be VARCHAR type"
            )
        
        # Test nullable columns
        nullable_columns = ["full_name", "bio", "avatar_url"]
        for col_name in nullable_columns:
            assert columns[col_name]["nullable"] is True, (
                f"{col_name} should be nullable"
            )
        
        # Test non-nullable columns
        non_nullable_columns = ["email", "username", "password_hash", "is_active"]
        for col_name in non_nullable_columns:
            assert columns[col_name]["nullable"] is False, (
                f"{col_name} should not be nullable"
            )

    @pytest.mark.integration
    def test_user_table_constraints(self, db_engine):
        """Test that users table has proper constraints."""
        inspector = inspect(db_engine)
        
        # Test primary key
        pk_constraint = inspector.get_pk_constraint("users")
        assert pk_constraint["constrained_columns"] == ["id"], (
            "Primary key should be on id column"
        )
        
        # Test unique constraints
        unique_constraints = inspector.get_unique_constraints("users")
        unique_columns = set()
        for constraint in unique_constraints:
            unique_columns.update(constraint["column_names"])
        
        assert "email" in unique_columns, "email should have unique constraint"
        assert "username" in unique_columns, "username should have unique constraint"

    @pytest.mark.integration
    def test_user_table_indexes(self, db_engine):
        """Test that users table has proper indexes."""
        inspector = inspect(db_engine)
        indexes = inspector.get_indexes("users")
        
        index_columns = set()
        for index in indexes:
            index_columns.update(index["column_names"])
        
        # These indexes should exist for performance
        expected_indexed_columns = {"email", "username"}
        assert expected_indexed_columns.issubset(index_columns), (
            f"Missing indexes. Expected: {expected_indexed_columns}, "
            f"Found: {index_columns}"
        )

    @pytest.mark.integration
    def test_user_table_defaults(self, db_engine):
        """Test that users table has proper default values."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("users")}
        
        # Test boolean default
        is_active_default = columns["is_active"].get("default")
        assert is_active_default is not None, "is_active should have default value"
        
        # Test timestamp defaults (created_at, updated_at should have server defaults)
        created_at_default = columns["created_at"].get("server_default")
        updated_at_default = columns["updated_at"].get("server_default")
        
        assert created_at_default is not None, "created_at should have server default"
        assert updated_at_default is not None, "updated_at should have server default"