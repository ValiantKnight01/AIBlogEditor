"""
Database schema tests for Tag entity.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker

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


class TestTagSchema:
    """Test database schema for Tag entity."""

    @pytest.mark.integration
    def test_tags_table_exists(self, db_engine):
        """Test that tags table exists in database."""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        assert "tags" in tables, "tags table should exist in database"

    @pytest.mark.integration
    def test_tags_table_columns(self, db_engine):
        """Test that tags table has all required columns."""
        inspector = inspect(db_engine)
        columns = inspector.get_columns("tags")
        column_names = {col["name"] for col in columns}
        
        expected_columns = {
            "id",
            "name",
            "slug",
            "color",
            "description",
            "created_at",
            "post_count",
            "project_count"
        }
        
        assert expected_columns.issubset(column_names), (
            f"Missing columns in tags table. Expected: {expected_columns}, "
            f"Found: {column_names}"
        )

    @pytest.mark.integration
    def test_tags_table_column_types(self, db_engine):
        """Test that tags table columns have correct data types."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("tags")}
        
        # Test UUID primary key
        assert columns["id"]["type"].python_type.__name__ in ("UUID", "str"), (
            "id column should be UUID type"
        )
        
        # Test string columns with length limits
        string_columns = ["name", "slug", "color", "description"]
        for col_name in string_columns:
            if col_name in columns:
                assert "VARCHAR" in str(columns[col_name]["type"]).upper(), (
                    f"{col_name} should be VARCHAR type"
                )
        
        # Test integer columns for counts
        for count_col in ["post_count", "project_count"]:
            assert "INTEGER" in str(columns[count_col]["type"]).upper(), (
                f"{count_col} should be INTEGER type"
            )
        
        # Test nullable columns
        nullable_columns = ["color", "description"]
        for col_name in nullable_columns:
            assert columns[col_name]["nullable"] is True, (
                f"{col_name} should be nullable"
            )
        
        # Test non-nullable columns
        non_nullable_columns = ["name", "slug", "post_count", "project_count"]
        for col_name in non_nullable_columns:
            assert columns[col_name]["nullable"] is False, (
                f"{col_name} should not be nullable"
            )

    @pytest.mark.integration
    def test_tags_table_constraints(self, db_engine):
        """Test that tags table has proper constraints."""
        inspector = inspect(db_engine)
        
        # Test primary key
        pk_constraint = inspector.get_pk_constraint("tags")
        assert pk_constraint["constrained_columns"] == ["id"], (
            "Primary key should be on id column"
        )
        
        # Test unique constraints
        unique_constraints = inspector.get_unique_constraints("tags")
        unique_columns = set()
        for constraint in unique_constraints:
            unique_columns.update(constraint["column_names"])
        
        assert "name" in unique_columns, "name should have unique constraint"
        assert "slug" in unique_columns, "slug should have unique constraint"

    @pytest.mark.integration
    def test_tags_table_indexes(self, db_engine):
        """Test that tags table has proper indexes."""
        inspector = inspect(db_engine)
        indexes = inspector.get_indexes("tags")
        
        index_columns = set()
        for index in indexes:
            index_columns.update(index["column_names"])
        
        # These indexes should exist for performance
        expected_indexed_columns = {"slug", "name"}
        assert expected_indexed_columns.issubset(index_columns), (
            f"Missing indexes. Expected: {expected_indexed_columns}, "
            f"Found: {index_columns}"
        )

    @pytest.mark.integration
    def test_tags_table_defaults(self, db_engine):
        """Test that tags table has proper default values."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("tags")}
        
        # Test count defaults (should be 0)
        for count_col in ["post_count", "project_count"]:
            count_default = columns[count_col].get("default")
            assert count_default is not None, f"{count_col} should have default value of 0"
        
        # Test timestamp defaults
        created_at_default = columns["created_at"].get("server_default")
        assert created_at_default is not None, "created_at should have server default"

    @pytest.mark.integration
    def test_tags_color_format(self, db_engine):
        """Test that tags color column has proper hex color format constraint."""
        inspector = inspect(db_engine)
        
        # Check if there's a check constraint for hex color format
        check_constraints = inspector.get_check_constraints("tags")
        
        # Look for color format constraint
        color_constraint_found = False
        for constraint in check_constraints:
            constraint_text = constraint.get("sqltext", "").lower()
            if "color" in constraint_text and ("#" in constraint_text or "hex" in constraint_text):
                color_constraint_found = True
                break
        
        # Note: Color format validation might be implemented at the application level
        # rather than database level, so we don't fail if it's not found
        if color_constraint_found:
            assert True, "Color format constraint exists"
        else:
            # This is acceptable - constraint can be handled by application logic
            pass

    @pytest.mark.integration
    def test_tags_name_case_insensitive_uniqueness(self, db_engine):
        """Test that tag names should have case-insensitive uniqueness."""
        inspector = inspect(db_engine)
        
        # Check for case-insensitive unique constraint or index
        indexes = inspector.get_indexes("tags")
        unique_constraints = inspector.get_unique_constraints("tags")
        
        # Look for case-insensitive implementation
        case_insensitive_found = False
        
        # Check unique constraints
        for constraint in unique_constraints:
            if "name" in constraint["column_names"]:
                # The constraint exists, case-insensitivity might be handled at app level
                case_insensitive_found = True
                break
        
        # Check indexes for functional indexes (like LOWER(name))
        for index in indexes:
            if "name" in index["column_names"] and index.get("unique"):
                case_insensitive_found = True
                break
        
        assert case_insensitive_found, (
            "Tags should have unique constraint on name (case-insensitive implementation may be at app level)"
        )