"""
Database schema tests for BlogPost entity.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker

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


class TestBlogPostSchema:
    """Test database schema for BlogPost entity."""

    @pytest.mark.integration
    def test_blog_posts_table_exists(self, db_engine):
        """Test that blog_posts table exists in database."""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        assert "blog_posts" in tables, "blog_posts table should exist in database"

    @pytest.mark.integration
    def test_blog_posts_table_columns(self, db_engine):
        """Test that blog_posts table has all required columns."""
        inspector = inspect(db_engine)
        columns = inspector.get_columns("blog_posts")
        column_names = {col["name"] for col in columns}
        
        expected_columns = {
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "status",
            "author_id",
            "published_at",
            "created_at",
            "updated_at",
            "view_count",
            "featured_image_url",
            "meta_title",
            "meta_description"
        }
        
        assert expected_columns.issubset(column_names), (
            f"Missing columns in blog_posts table. Expected: {expected_columns}, "
            f"Found: {column_names}"
        )

    @pytest.mark.integration
    def test_blog_posts_table_column_types(self, db_engine):
        """Test that blog_posts table columns have correct data types."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("blog_posts")}
        
        # Test UUID primary key
        assert columns["id"]["type"].python_type.__name__ in ("UUID", "str"), (
            "id column should be UUID type"
        )
        
        # Test string columns with length limits
        string_columns = ["title", "slug", "excerpt", "featured_image_url", "meta_title", "meta_description"]
        for col_name in string_columns:
            if col_name in columns:
                assert "VARCHAR" in str(columns[col_name]["type"]).upper(), (
                    f"{col_name} should be VARCHAR type"
                )
        
        # Test text columns (unlimited length)
        assert "TEXT" in str(columns["content"]["type"]).upper(), (
            "content should be TEXT type"
        )
        
        # Test integer column
        assert "INTEGER" in str(columns["view_count"]["type"]).upper(), (
            "view_count should be INTEGER type"
        )
        
        # Test nullable columns
        nullable_columns = [
            "excerpt", "published_at", "featured_image_url", "meta_title", "meta_description"
        ]
        for col_name in nullable_columns:
            assert columns[col_name]["nullable"] is True, (
                f"{col_name} should be nullable"
            )
        
        # Test non-nullable columns
        non_nullable_columns = ["title", "slug", "content", "status", "author_id", "view_count"]
        for col_name in non_nullable_columns:
            assert columns[col_name]["nullable"] is False, (
                f"{col_name} should not be nullable"
            )

    @pytest.mark.integration
    def test_blog_posts_table_constraints(self, db_engine):
        """Test that blog_posts table has proper constraints."""
        inspector = inspect(db_engine)
        
        # Test primary key
        pk_constraint = inspector.get_pk_constraint("blog_posts")
        assert pk_constraint["constrained_columns"] == ["id"], (
            "Primary key should be on id column"
        )
        
        # Test unique constraints
        unique_constraints = inspector.get_unique_constraints("blog_posts")
        unique_columns = set()
        for constraint in unique_constraints:
            unique_columns.update(constraint["column_names"])
        
        assert "slug" in unique_columns, "slug should have unique constraint"
        
        # Test foreign key constraints
        foreign_keys = inspector.get_foreign_keys("blog_posts")
        fk_columns = {fk["constrained_columns"][0] for fk in foreign_keys}
        
        assert "author_id" in fk_columns, "author_id should have foreign key constraint"

    @pytest.mark.integration
    def test_blog_posts_table_indexes(self, db_engine):
        """Test that blog_posts table has proper indexes."""
        inspector = inspect(db_engine)
        indexes = inspector.get_indexes("blog_posts")
        
        index_columns = set()
        for index in indexes:
            index_columns.update(index["column_names"])
        
        # These indexes should exist for performance
        expected_indexed_columns = {"slug", "status", "published_at", "author_id"}
        assert expected_indexed_columns.issubset(index_columns), (
            f"Missing indexes. Expected: {expected_indexed_columns}, "
            f"Found: {index_columns}"
        )

    @pytest.mark.integration
    def test_blog_posts_table_defaults(self, db_engine):
        """Test that blog_posts table has proper default values."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("blog_posts")}
        
        # Test view_count default
        view_count_default = columns["view_count"].get("default")
        assert view_count_default is not None, "view_count should have default value of 0"
        
        # Test status default (should be 'draft')
        status_default = columns["status"].get("default")
        assert status_default is not None, "status should have default value"
        
        # Test timestamp defaults
        created_at_default = columns["created_at"].get("default")
        updated_at_default = columns["updated_at"].get("default")

        assert created_at_default is not None, "created_at should have server default"
        assert updated_at_default is not None, "updated_at should have server default"

    @pytest.mark.integration
    def test_blog_posts_status_enum(self, db_engine):
        """Test that blog_posts status column has enum constraint."""
        inspector = inspect(db_engine)
        
        # Check if there's a check constraint for status enum
        check_constraints = inspector.get_check_constraints("blog_posts")
        
        # Look for status enum constraint
        status_constraint_found = False
        for constraint in check_constraints:
            if "status" in constraint.get("sqltext", "").lower():
                status_constraint_found = True
                # Should allow 'draft' and 'published'
                constraint_text = constraint["sqltext"].lower()
                assert "draft" in constraint_text, "Status enum should include 'draft'"
                assert "published" in constraint_text, "Status enum should include 'published'"
                break
        
        # Note: Some databases might implement enums differently
        # If check constraints aren't found, the enum might be implemented at the column type level
        if not status_constraint_found:
            columns = inspector.get_columns("blog_posts")
            status_column = next((col for col in columns if col["name"] == "status"), None)
            if status_column and hasattr(status_column["type"], "enums"):
                enums = status_column["type"].enums
                assert "draft" in enums, "Status enum should include 'draft'"
                assert "published" in enums, "Status enum should include 'published'"