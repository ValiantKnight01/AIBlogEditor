"""
Contract tests for PUT /api/v1/projects/{slug} endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestProjectsUpdateContract:
    """Contract tests for project update endpoint."""
    
    def test_update_project_success_contract(self):
        """Test successful project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        update_data = {
            "title": "Updated Awesome Project",
            "description": "This is my updated awesome project",
            "tech_stack": ["Python", "FastAPI", "React", "TypeScript"],
            "github_url": "https://github.com/user/updated-awesome-project",
            "live_url": "https://updated-awesome-project.com",
            "image_url": "https://example.com/updated-project-image.jpg",
            "status": "completed",
            "featured": True
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == project_slug
        assert data["title"] == "Updated Awesome Project"
        assert data["description"] == "This is my updated awesome project"
        assert data["tech_stack"] == ["Python", "FastAPI", "React", "TypeScript"]
        assert data["github_url"] == "https://github.com/user/updated-awesome-project"
        assert data["live_url"] == "https://updated-awesome-project.com"
        assert data["image_url"] == "https://example.com/updated-project-image.jpg"
        assert data["status"] == "completed"
        assert data["featured"] is True
        assert "updated_at" in data
        assert data["created_at"] is not None

    def test_update_project_partial_contract(self):
        """Test partial project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        partial_data = {
            "title": "Partially Updated Project",
            "status": "in_progress"
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=partial_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Partially Updated Project"
        assert data["status"] == "in_progress"

    def test_update_project_not_found_contract(self):
        """Test updating non-existent project."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        update_data = {
            "title": "Non-existent Project",
            "description": "This project does not exist"
        }
        
        response = client.put(
            "/api/v1/projects/non-existent-project",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_update_project_unauthorized_contract(self):
        """Test updating project without authentication."""
        # This test MUST FAIL until endpoint is implemented
        project_slug = "my-awesome-project"
        
        update_data = {
            "title": "Unauthorized Update",
            "description": "This should fail"
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_project_invalid_token_contract(self):
        """Test updating project with invalid token."""
        # This test MUST FAIL until endpoint is implemented
        invalid_token = "Bearer invalid_token"
        project_slug = "my-awesome-project"
        
        update_data = {
            "title": "Invalid Token Update",
            "description": "This should fail"
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": invalid_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_project_invalid_data_contract(self):
        """Test updating project with invalid data."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        invalid_data = {
            "title": "",  # Empty title should be invalid
            "tech_stack": "not a list",  # Should be a list
            "github_url": "not-a-valid-url",  # Invalid URL
            "status": "invalid_status"  # Invalid status
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=invalid_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_update_project_slug_conflict_contract(self):
        """Test updating project where generated slug conflicts."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        update_data = {
            "title": "Another Existing Project"  # This would generate an existing slug
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_update_project_tech_stack_validation_contract(self):
        """Test tech stack validation in project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        # Test empty tech stack array (should be valid)
        update_data = {
            "title": "Project with Empty Tech Stack",
            "tech_stack": []
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tech_stack"] == []

    def test_update_project_url_validation_contract(self):
        """Test URL validation in project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        # Test valid URLs
        update_data = {
            "github_url": "https://github.com/user/project",
            "live_url": "https://project.com",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200

    def test_update_project_status_validation_contract(self):
        """Test status field validation in project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        # Test all valid statuses
        valid_statuses = ["planning", "in_progress", "completed", "archived"]
        
        for status in valid_statuses:
            update_data = {"status": status}
            
            response = client.put(
                f"/api/v1/projects/{project_slug}",
                json=update_data,
                headers={"Authorization": valid_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == status

    def test_update_project_featured_flag_contract(self):
        """Test featured flag in project update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        project_slug = "my-awesome-project"
        
        # Test setting featured to true
        update_data = {"featured": True}
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["featured"] is True

    def test_update_project_forbidden_contract(self):
        """Test updating project that user doesn't own."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_token_different_user"
        project_slug = "someone-elses-project"
        
        update_data = {
            "title": "Trying to update someone else's project"
        }
        
        response = client.put(
            f"/api/v1/projects/{project_slug}",
            json=update_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 403
        assert "detail" in response.json()