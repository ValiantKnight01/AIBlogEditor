"""
Contract tests for GET /api/v1/projects endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestProjectsListContract:
    """Contract tests for projects list endpoint."""
    
    def test_list_projects_success_contract(self):
        """Test successful projects listing."""
        # This test MUST FAIL until endpoint is implemented
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        # Verify items structure
        assert isinstance(data["items"], list)
        if data["items"]:  # If there are projects
            project = data["items"][0]
            assert "id" in project
            assert "title" in project
            assert "slug" in project
            assert "description" in project
            assert "content" in project
            assert "status" in project
            assert "created_at" in project
            assert "updated_at" in project
            assert "author" in project
            assert "tags" in project

    def test_list_projects_pagination_contract(self):
        """Test projects pagination."""
        response = client.get("/api/v1/projects?page=1&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["items"]) <= 5

    def test_list_projects_invalid_page_contract(self):
        """Test invalid page parameter."""
        invalid_pages = [0, -1, "invalid"]
        
        for page in invalid_pages:
            response = client.get(f"/api/v1/projects?page={page}")
            assert response.status_code == 422, f"Failed for page: {page}"

    def test_list_projects_invalid_limit_contract(self):
        """Test invalid limit parameter."""
        invalid_limits = [0, -1, 51, "invalid"]  # 51 exceeds max of 50
        
        for limit in invalid_limits:
            response = client.get(f"/api/v1/projects?limit={limit}")
            assert response.status_code == 422, f"Failed for limit: {limit}"

    def test_list_projects_tag_filter_contract(self):
        """Test filtering projects by tag."""
        response = client.get("/api/v1/projects?tag=python")
        
        assert response.status_code == 200
        data = response.json()
        
        # If there are results, verify they contain the tag
        if data["items"]:
            for project in data["items"]:
                tag_names = [tag["name"].lower() for tag in project["tags"]]
                assert "python" in tag_names or any("python" in name for name in tag_names)

    def test_list_projects_empty_result_contract(self):
        """Test when no projects match criteria."""
        response = client.get("/api/v1/projects?tag=non-existent-tag")
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_projects_wrong_http_method_contract(self):
        """Test wrong HTTP method returns 405."""
        response = client.post("/api/v1/projects")  # POST instead of GET (without auth)
        
        # Should return 401 for unauthorized, not 405, because POST is valid but needs auth
        assert response.status_code == 401

    def test_list_projects_default_pagination_contract(self):
        """Test default pagination parameters."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10  # Default limit per API spec

    def test_list_projects_author_info_contract(self):
        """Test that author information is included."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            project = data["items"][0]
            assert "author" in project
            author = project["author"]
            assert "id" in author
            assert "name" in author
            assert "email" not in author  # Email should not be exposed

    def test_list_projects_published_only_contract(self):
        """Test that only published projects are returned."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned projects should be published
        for project in data["items"]:
            assert project["status"] == "published"

    def test_list_projects_tag_structure_contract(self):
        """Test the structure of tags in project responses."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            project = data["items"][0]
            if project["tags"]:
                tag = project["tags"][0]
                assert "id" in tag
                assert "name" in tag
                assert "slug" in tag
                assert "color" in tag

    def test_list_projects_date_format_contract(self):
        """Test that dates are in correct ISO format."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            project = data["items"][0]
            # Dates should be ISO format strings
            assert isinstance(project["created_at"], str)
            assert isinstance(project["updated_at"], str)
            # Basic ISO format check (YYYY-MM-DD)
            assert len(project["created_at"]) >= 10
            assert len(project["updated_at"]) >= 10

    def test_list_projects_ordering_contract(self):
        """Test that projects are ordered correctly."""
        response = client.get("/api/v1/projects?limit=50")
        
        assert response.status_code == 200
        data = response.json()
        
        # Projects should be ordered by created_at desc (newest first)
        if len(data["items"]) > 1:
            for i in range(len(data["items"]) - 1):
                current_date = data["items"][i]["created_at"]
                next_date = data["items"][i + 1]["created_at"]
                # Current should be newer than or equal to next
                assert current_date >= next_date

    def test_list_projects_content_preview_contract(self):
        """Test that content is provided (full or preview)."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            project = data["items"][0]
            # Content should be present and non-empty for published projects
            assert "content" in project
            assert isinstance(project["content"], str)