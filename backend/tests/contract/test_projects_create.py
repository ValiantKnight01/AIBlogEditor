"""
Contract tests for POST /api/v1/projects endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestProjectsCreateContract:
    """Contract tests for project creation endpoint."""
    
    def test_create_project_success_contract(self):
        """Test successful project creation."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_data = {
            "title": "My Awesome Project",
            "description": "A comprehensive project description",
            "content": "This is the detailed content of my project with markdown support.",
            "status": "published",
            "github_url": "https://github.com/user/awesome-project",
            "demo_url": "https://awesome-project.demo.com",
            "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
            "tags": ["web-development", "api"]
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify returned data structure
        assert data["title"] == "My Awesome Project"
        assert data["description"] == "A comprehensive project description"
        assert data["content"] == "This is the detailed content of my project with markdown support."
        assert data["status"] == "published"
        assert data["github_url"] == "https://github.com/user/awesome-project"
        assert data["demo_url"] == "https://awesome-project.demo.com"
        assert data["tech_stack"] == ["Python", "FastAPI", "React", "PostgreSQL"]
        
        # Auto-generated fields
        assert "id" in data
        assert "slug" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "author" in data
        assert "tags" in data
        
        # Slug should be generated from title
        assert data["slug"] == "my-awesome-project"

    def test_create_project_unauthorized_contract(self):
        """Test project creation without authentication."""
        project_data = {
            "title": "Unauthorized Project",
            "description": "This should fail",
            "content": "Content"
        }
        
        response = client.post("/api/v1/projects", json=project_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_project_invalid_token_contract(self):
        """Test project creation with invalid token."""
        invalid_token = "Bearer invalid_token"
        project_data = {
            "title": "Invalid Token Project",
            "description": "This should fail",
            "content": "Content"
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": invalid_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_project_validation_error_contract(self):
        """Test project creation with validation errors."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Missing required fields
        invalid_data_sets = [
            {},  # Empty data
            {"description": "Missing title"},  # Missing title
            {"title": "Missing description"},  # Missing description
            {"title": "Test", "description": "Test"},  # Missing content
            {"title": "", "description": "Test", "content": "Test"},  # Empty title
        ]
        
        for invalid_data in invalid_data_sets:
            response = client.post(
                "/api/v1/projects",
                json=invalid_data,
                headers={"Authorization": valid_token}
            )
            
            assert response.status_code == 422
            assert "detail" in response.json()

    def test_create_project_minimal_data_contract(self):
        """Test project creation with minimal required data."""
        valid_token = "Bearer valid_jwt_token_here"
        minimal_data = {
            "title": "Minimal Project",
            "description": "Basic description",
            "content": "Basic content"
        }
        
        response = client.post(
            "/api/v1/projects",
            json=minimal_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Project"
        assert data["status"] == "draft"  # Should default to draft
        assert data["tech_stack"] == []  # Should default to empty array
        assert data["github_url"] is None or data["github_url"] == ""
        assert data["demo_url"] is None or data["demo_url"] == ""

    def test_create_project_slug_generation_contract(self):
        """Test automatic slug generation from title."""
        valid_token = "Bearer valid_jwt_token_here"
        project_data = {
            "title": "My Complex Project Title With Spaces & Special Characters!",
            "description": "Description",
            "content": "Content"
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        # Slug should be normalized
        expected_slug = "my-complex-project-title-with-spaces-special-characters"
        assert data["slug"] == expected_slug

    def test_create_project_duplicate_slug_handling_contract(self):
        """Test handling of duplicate slugs."""
        valid_token = "Bearer valid_jwt_token_here"
        project_data = {
            "title": "Duplicate Title Test",
            "description": "First project",
            "content": "Content"
        }
        
        # Create first project
        response1 = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        # Create second project with same title
        project_data["description"] = "Second project"
        response2 = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # Slugs should be different (second should have suffix)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["slug"] != data2["slug"]
        assert data2["slug"].startswith("duplicate-title-test")

    def test_create_project_invalid_json_contract(self):
        """Test project creation with invalid JSON."""
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.post(
            "/api/v1/projects",
            data="invalid json",
            headers={"Authorization": valid_token, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_create_project_tag_handling_contract(self):
        """Test tag creation and association during project creation."""
        valid_token = "Bearer valid_jwt_token_here"
        project_data = {
            "title": "Project with Tags",
            "description": "Description",
            "content": "Content",
            "tags": ["python", "web-development", "new-tag"]
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert isinstance(data["tags"], list)
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "python" in tag_names
        assert "web-development" in tag_names
        assert "new-tag" in tag_names

    def test_create_project_url_validation_contract(self):
        """Test URL validation for github_url and demo_url."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Invalid URLs should cause validation error
        invalid_url_data = [
            {
                "title": "Invalid GitHub URL",
                "description": "Test",
                "content": "Test",
                "github_url": "not-a-url"
            },
            {
                "title": "Invalid Demo URL",
                "description": "Test",
                "content": "Test",
                "demo_url": "invalid-url"
            }
        ]
        
        for data in invalid_url_data:
            response = client.post(
                "/api/v1/projects",
                json=data,
                headers={"Authorization": valid_token}
            )
            
            assert response.status_code == 422

    def test_create_project_tech_stack_validation_contract(self):
        """Test tech_stack field validation."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Tech stack should be array of strings
        project_data = {
            "title": "Tech Stack Test",
            "description": "Description",
            "content": "Content",
            "tech_stack": "Should be array, not string"  # Invalid type
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422

    def test_create_project_status_validation_contract(self):
        """Test status field validation."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Test valid statuses
        valid_statuses = ["draft", "published"]
        for status in valid_statuses:
            project_data = {
                "title": f"Project with {status} status",
                "description": "Description",
                "content": "Content",
                "status": status
            }
            
            response = client.post(
                "/api/v1/projects",
                json=project_data,
                headers={"Authorization": valid_token}
            )
            
            assert response.status_code == 201
            assert response.json()["status"] == status
        
        # Test invalid status
        invalid_project_data = {
            "title": "Invalid Status Project",
            "description": "Description",
            "content": "Content",
            "status": "invalid_status"
        }
        
        response = client.post(
            "/api/v1/projects",
            json=invalid_project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422

    def test_create_project_content_length_contract(self):
        """Test content length validation."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Very long content should be accepted (within reasonable limits)
        long_content = "A" * 10000  # 10KB content
        project_data = {
            "title": "Long Content Project",
            "description": "Project with long content",
            "content": long_content
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        assert len(response.json()["content"]) == 10000