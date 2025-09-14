"""
Contract tests for GET /api/v1/projects/{slug} endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestProjectsGetContract:
    """Contract tests for project detail endpoint."""
    
    def test_get_project_success_contract(self):
        """Test successful project retrieval."""
        # This test MUST FAIL until endpoint is implemented
        response = client.get("/api/v1/projects/awesome-project-slug")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify project structure
        assert "id" in data
        assert "title" in data
        assert "slug" in data
        assert "description" in data
        assert "content" in data
        assert "status" in data
        assert "github_url" in data
        assert "demo_url" in data
        assert "tech_stack" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "author" in data
        assert "tags" in data
        
        # Verify data types
        assert isinstance(data["tech_stack"], list)
        assert isinstance(data["tags"], list)
        assert data["slug"] == "awesome-project-slug"

    def test_get_project_not_found_contract(self):
        """Test retrieving non-existent project."""
        response = client.get("/api/v1/projects/non-existent-slug")
        
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_get_project_published_only_contract(self):
        """Test that only published projects are accessible."""
        # Trying to access a draft project should return 404
        response = client.get("/api/v1/projects/draft-project-slug")
        
        assert response.status_code == 404

    def test_get_project_author_info_contract(self):
        """Test that author information is included."""
        response = client.get("/api/v1/projects/project-with-author")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "author" in data
        author = data["author"]
        assert "id" in author
        assert "name" in author
        # Email should not be exposed
        assert "email" not in author

    def test_get_project_tag_details_contract(self):
        """Test that tag details are included."""
        response = client.get("/api/v1/projects/project-with-tags")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["tags"]:
            tag = data["tags"][0]
            assert "id" in tag
            assert "name" in tag
            assert "slug" in tag
            assert "color" in tag

    def test_get_project_content_full_contract(self):
        """Test that full content is returned (not truncated)."""
        response = client.get("/api/v1/projects/project-with-long-content")
        
        assert response.status_code == 200
        data = response.json()
        
        # Content should be full, not truncated like in list view
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0

    def test_get_project_optional_fields_contract(self):
        """Test handling of optional fields."""
        response = client.get("/api/v1/projects/minimal-project")
        
        assert response.status_code == 200
        data = response.json()
        
        # Optional fields should be null or empty
        if "github_url" in data:
            assert data["github_url"] is None or isinstance(data["github_url"], str)
        if "demo_url" in data:
            assert data["demo_url"] is None or isinstance(data["demo_url"], str)

    def test_get_project_date_format_contract(self):
        """Test that dates are in correct format."""
        response = client.get("/api/v1/projects/project-with-dates")
        
        assert response.status_code == 200
        data = response.json()
        
        # Dates should be ISO format strings
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        # Basic ISO format check
        assert len(data["created_at"]) >= 10
        assert len(data["updated_at"]) >= 10

    def test_get_project_case_sensitivity_contract(self):
        """Test slug case sensitivity."""
        # Slugs should be case insensitive or consistently lowercase
        response1 = client.get("/api/v1/projects/Test-Project")
        response2 = client.get("/api/v1/projects/test-project")
        
        # Both should work or both should fail consistently
        assert response1.status_code == response2.status_code

    def test_get_project_special_characters_slug_contract(self):
        """Test handling of special characters in slug."""
        # Test URL encoding handling
        response = client.get("/api/v1/projects/project-with-special-chars")
        
        assert response.status_code in [200, 404]  # Should handle gracefully

    def test_get_project_tech_stack_structure_contract(self):
        """Test tech stack array structure."""
        response = client.get("/api/v1/projects/project-with-tech-stack")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["tech_stack"], list)
        if data["tech_stack"]:
            # Each item should be a string
            for tech in data["tech_stack"]:
                assert isinstance(tech, str)

    def test_get_project_status_published_contract(self):
        """Test that returned project has published status."""
        response = client.get("/api/v1/projects/published-project")
        
        assert response.status_code == 200
        data = response.json()
        
        # Only published projects should be accessible via this endpoint
        assert data["status"] == "published"

    def test_get_project_wrong_http_method_contract(self):
        """Test wrong HTTP method returns 405."""
        response = client.post("/api/v1/projects/some-slug")
        
        # POST without auth should return 401, not 405
        assert response.status_code == 401

    def test_get_project_urls_validation_contract(self):
        """Test URL fields are valid when present."""
        response = client.get("/api/v1/projects/project-with-urls")
        
        assert response.status_code == 200
        data = response.json()
        
        # If URLs are present, they should be valid
        if data.get("github_url"):
            assert data["github_url"].startswith(("http://", "https://"))
        if data.get("demo_url"):
            assert data["demo_url"].startswith(("http://", "https://"))