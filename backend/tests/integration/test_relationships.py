"""
Database schema tests for entity relationships (junction tables).
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker

from src.config import settings


@pytest.fixture
def db_engine():
    """Create a database engine for testing."""
    # Use test database URL
    test_url = settings.database.database_url.replace("blog_db", "blog_db_test")
    engine = create_engine(test_url)
    return engine


@pytest.fixture  
def db_session(db_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


class TestRelationshipSchema:
    """Test database schema for entity relationships."""

    @pytest.mark.integration
    def test_blog_post_tags_table_exists(self, db_engine):
        """Test that blog_post_tags junction table exists."""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        assert "blog_post_tags" in tables, "blog_post_tags table should exist in database"

    @pytest.mark.integration
    def test_project_tags_table_exists(self, db_engine):
        """Test that project_tags junction table exists."""
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        assert "project_tags" in tables, "project_tags table should exist in database"

    @pytest.mark.integration
    def test_blog_post_tags_columns(self, db_engine):
        """Test that blog_post_tags table has correct columns."""
        inspector = inspect(db_engine)
        columns = inspector.get_columns("blog_post_tags")
        column_names = {col["name"] for col in columns}
        
        expected_columns = {
            "blog_post_id",
            "tag_id", 
            "created_at"
        }
        
        assert expected_columns.issubset(column_names), (
            f"Missing columns in blog_post_tags table. Expected: {expected_columns}, "
            f"Found: {column_names}"
        )

    @pytest.mark.integration
    def test_project_tags_columns(self, db_engine):
        """Test that project_tags table has correct columns."""
        inspector = inspect(db_engine)
        columns = inspector.get_columns("project_tags")
        column_names = {col["name"] for col in columns}
        
        expected_columns = {
            "project_id",
            "tag_id",
            "created_at"
        }
        
        assert expected_columns.issubset(column_names), (
            f"Missing columns in project_tags table. Expected: {expected_columns}, "
            f"Found: {column_names}"
        )

    @pytest.mark.integration
    def test_blog_post_tags_column_types(self, db_engine):
        """Test that blog_post_tags columns have correct types."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("blog_post_tags")}
        
        # Test UUID foreign key columns
        for fk_col in ["blog_post_id", "tag_id"]:
            assert columns[fk_col]["type"].python_type.__name__ in ("UUID", "str"), (
                f"{fk_col} column should be UUID type"
            )
            assert columns[fk_col]["nullable"] is False, (
                f"{fk_col} should not be nullable"
            )
        
        # Test timestamp column
        created_at_type = str(columns["created_at"]["type"]).upper()
        assert "TIMESTAMP" in created_at_type or "DATETIME" in created_at_type, (
            "created_at should be TIMESTAMP or DATETIME type"
        )

    @pytest.mark.integration
    def test_project_tags_column_types(self, db_engine):
        """Test that project_tags columns have correct types."""
        inspector = inspect(db_engine)
        columns = {col["name"]: col for col in inspector.get_columns("project_tags")}
        
        # Test UUID foreign key columns
        for fk_col in ["project_id", "tag_id"]:
            assert columns[fk_col]["type"].python_type.__name__ in ("UUID", "str"), (
                f"{fk_col} column should be UUID type"
            )
            assert columns[fk_col]["nullable"] is False, (
                f"{fk_col} should not be nullable"
            )
        
        # Test timestamp column
        created_at_type = str(columns["created_at"]["type"]).upper()
        assert "TIMESTAMP" in created_at_type or "DATETIME" in created_at_type, (
            "created_at should be TIMESTAMP or DATETIME type"
        )

    @pytest.mark.integration
    def test_blog_post_tags_primary_key(self, db_engine):
        """Test that blog_post_tags has composite primary key."""
        inspector = inspect(db_engine)
        pk_constraint = inspector.get_pk_constraint("blog_post_tags")
        
        expected_pk_columns = {"blog_post_id", "tag_id"}
        actual_pk_columns = set(pk_constraint["constrained_columns"])
        
        assert expected_pk_columns == actual_pk_columns, (
            f"Primary key should be composite (blog_post_id, tag_id). "
            f"Expected: {expected_pk_columns}, Found: {actual_pk_columns}"
        )

    @pytest.mark.integration
    def test_project_tags_primary_key(self, db_engine):
        """Test that project_tags has composite primary key."""
        inspector = inspect(db_engine)
        pk_constraint = inspector.get_pk_constraint("project_tags")
        
        expected_pk_columns = {"project_id", "tag_id"}
        actual_pk_columns = set(pk_constraint["constrained_columns"])
        
        assert expected_pk_columns == actual_pk_columns, (
            f"Primary key should be composite (project_id, tag_id). "
            f"Expected: {expected_pk_columns}, Found: {actual_pk_columns}"
        )

    @pytest.mark.integration
    def test_blog_post_tags_foreign_keys(self, db_engine):
        """Test that blog_post_tags has correct foreign key constraints."""
        inspector = inspect(db_engine)
        foreign_keys = inspector.get_foreign_keys("blog_post_tags")
        
        # Extract foreign key information
        fk_info = {}
        for fk in foreign_keys:
            constrained_col = fk["constrained_columns"][0]
            referenced_table = fk["referred_table"]
            referenced_col = fk["referred_columns"][0]
            fk_info[constrained_col] = (referenced_table, referenced_col)
        
        # Test blog_post_id foreign key
        assert "blog_post_id" in fk_info, "blog_post_id should have foreign key constraint"
        blog_post_fk = fk_info["blog_post_id"]
        assert blog_post_fk[0] == "blog_posts", "blog_post_id should reference blog_posts table"
        assert blog_post_fk[1] == "id", "blog_post_id should reference id column"
        
        # Test tag_id foreign key
        assert "tag_id" in fk_info, "tag_id should have foreign key constraint"
        tag_fk = fk_info["tag_id"]
        assert tag_fk[0] == "tags", "tag_id should reference tags table"
        assert tag_fk[1] == "id", "tag_id should reference id column"

    @pytest.mark.integration
    def test_project_tags_foreign_keys(self, db_engine):
        """Test that project_tags has correct foreign key constraints."""
        inspector = inspect(db_engine)
        foreign_keys = inspector.get_foreign_keys("project_tags")
        
        # Extract foreign key information
        fk_info = {}
        for fk in foreign_keys:
            constrained_col = fk["constrained_columns"][0]
            referenced_table = fk["referred_table"]
            referenced_col = fk["referred_columns"][0]
            fk_info[constrained_col] = (referenced_table, referenced_col)
        
        # Test project_id foreign key
        assert "project_id" in fk_info, "project_id should have foreign key constraint"
        project_fk = fk_info["project_id"]
        assert project_fk[0] == "projects", "project_id should reference projects table"
        assert project_fk[1] == "id", "project_id should reference id column"
        
        # Test tag_id foreign key
        assert "tag_id" in fk_info, "tag_id should have foreign key constraint"
        tag_fk = fk_info["tag_id"]
        assert tag_fk[0] == "tags", "tag_id should reference tags table"
        assert tag_fk[1] == "id", "tag_id should reference id column"

    @pytest.mark.integration
    def test_relationship_indexes(self, db_engine):
        """Test that junction tables have appropriate indexes."""
        inspector = inspect(db_engine)
        
        # Test blog_post_tags indexes
        blog_post_tags_indexes = inspector.get_indexes("blog_post_tags")
        blog_post_tags_indexed_columns = set()
        for index in blog_post_tags_indexes:
            blog_post_tags_indexed_columns.update(index["column_names"])
        
        # Should have indexes on foreign key columns for performance
        expected_blog_post_tags_indexes = {"blog_post_id", "tag_id"}
        assert expected_blog_post_tags_indexes.issubset(blog_post_tags_indexed_columns), (
            f"Missing indexes in blog_post_tags. Expected: {expected_blog_post_tags_indexes}, "
            f"Found: {blog_post_tags_indexed_columns}"
        )
        
        # Test project_tags indexes
        project_tags_indexes = inspector.get_indexes("project_tags")
        project_tags_indexed_columns = set()
        for index in project_tags_indexes:
            project_tags_indexed_columns.update(index["column_names"])
        
        expected_project_tags_indexes = {"project_id", "tag_id"}
        assert expected_project_tags_indexes.issubset(project_tags_indexed_columns), (
            f"Missing indexes in project_tags. Expected: {expected_project_tags_indexes}, "
            f"Found: {project_tags_indexed_columns}"
        )

    @pytest.mark.integration
    def test_cascade_behavior(self, db_engine):
        """Test that foreign keys have appropriate cascade behavior."""
        inspector = inspect(db_engine)
        
        # Test blog_post_tags foreign key cascades
        blog_post_tags_fks = inspector.get_foreign_keys("blog_post_tags")
        for fk in blog_post_tags_fks:
            # Should have cascade delete (when parent is deleted, junction records are deleted)
            # This might be implemented differently across databases
            ondelete = fk.get("ondelete", "").upper()
            # CASCADE or RESTRICT are both acceptable, depending on business logic
            assert ondelete in ["CASCADE", "RESTRICT", ""], (
                f"Foreign key {fk['constrained_columns'][0]} should have appropriate cascade behavior"
            )
        
        # Test project_tags foreign key cascades
        project_tags_fks = inspector.get_foreign_keys("project_tags")
        for fk in project_tags_fks:
            ondelete = fk.get("ondelete", "").upper()
            assert ondelete in ["CASCADE", "RESTRICT", ""], (
                f"Foreign key {fk['constrained_columns'][0]} should have appropriate cascade behavior"
            )