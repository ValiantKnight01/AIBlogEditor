"""
Contract tests for GET /api/v1/tags endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestTagsListContract:
    """Contract tests for tags list endpoint."""
    
    def test_list_tags_success_contract(self):
        """Test successful tags listing."""
        # This test MUST FAIL until endpoint is implemented
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return array of tag objects
        assert isinstance(data, list)
        
        if data:  # If there are tags
            tag = data[0]
            assert "id" in tag
            assert "name" in tag
            assert "slug" in tag
            assert "color" in tag
            assert "post_count" in tag
            assert "project_count" in tag
            assert "created_at" in tag

    def test_list_tags_empty_result_contract(self):
        """Test when no tags exist."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return empty array, not null

    def test_list_tags_structure_contract(self):
        """Test tag object structure."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            tag = data[0]
            # Verify data types
            assert isinstance(tag["id"], int)
            assert isinstance(tag["name"], str)
            assert isinstance(tag["slug"], str)
            assert isinstance(tag["color"], str)
            assert isinstance(tag["post_count"], int)
            assert isinstance(tag["project_count"], int)
            assert isinstance(tag["created_at"], str)

    def test_list_tags_color_format_contract(self):
        """Test that color field is in correct format."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for tag in data:
                color = tag["color"]
                # Color should be hex format
                assert color.startswith("#")
                assert len(color) == 7  # #RRGGBB format

    def test_list_tags_counts_contract(self):
        """Test that post and project counts are correct."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for tag in data:
                # Counts should be non-negative
                assert tag["post_count"] >= 0
                assert tag["project_count"] >= 0

    def test_list_tags_ordering_contract(self):
        """Test tags ordering."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        # Tags should be ordered by usage (total count) or alphabetically
        if len(data) > 1:
            # Check if ordered by total usage (desc) or name (asc)
            total_counts = [tag["post_count"] + tag["project_count"] for tag in data]
            names = [tag["name"].lower() for tag in data]
            
            # Should be either ordered by usage desc OR name asc
            usage_desc = total_counts == sorted(total_counts, reverse=True)
            name_asc = names == sorted(names)
            
            assert usage_desc or name_asc

    def test_list_tags_no_authentication_required_contract(self):
        """Test that tags endpoint doesn't require authentication."""
        # No Authorization header
        response = client.get("/api/v1/tags")
        
        # Should work without authentication
        assert response.status_code == 200

    def test_list_tags_slug_format_contract(self):
        """Test that slugs are properly formatted."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for tag in data:
                slug = tag["slug"]
                # Slug should be lowercase, no spaces, url-safe
                assert slug.islower()
                assert " " not in slug
                assert slug.replace("-", "").replace("_", "").isalnum()

    def test_list_tags_unique_names_contract(self):
        """Test that tag names are unique."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            names = [tag["name"].lower() for tag in data]
            # All names should be unique (case-insensitive)
            assert len(names) == len(set(names))

    def test_list_tags_wrong_http_method_contract(self):
        """Test wrong HTTP method."""
        response = client.post("/api/v1/tags")  # POST without auth
        
        # POST requires auth, so should return 401
        assert response.status_code == 401

    def test_list_tags_only_used_tags_contract(self):
        """Test that only tags with usage are returned."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned tags should have at least one post or project
        for tag in data:
            total_usage = tag["post_count"] + tag["project_count"]
            assert total_usage > 0

    def test_list_tags_date_format_contract(self):
        """Test that created_at is in correct format."""
        response = client.get("/api/v1/tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for tag in data:
                created_at = tag["created_at"]
                # Should be ISO format string
                assert isinstance(created_at, str)
                assert len(created_at) >= 10  # At least YYYY-MM-DD