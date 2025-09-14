"""
Contract tests for PUT /api/v1/posts/{slug} endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app


client = TestClient(app)


class TestPostsUpdateContract:
    """Contract tests for blog post update endpoint."""
    
    def test_update_post_success_contract(self):
        """Test successful blog post update."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Updated Blog Post Title",
            "content": "This is the updated content of the blog post.",
            "excerpt": "Updated excerpt",
            "published": True,
            "tags": ["updated-tag", "another-tag"]
        }
        
        response = client.put(
            "/api/v1/posts/existing-post-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Blog Post Title" 
        assert data["content"] == "This is the updated content of the blog post."
        assert data["published"] == True
        assert data["slug"] == "existing-post-slug"
        assert "updated_at" in data
        assert isinstance(data["tags"], list)
        assert len(data["tags"]) == 2

    def test_update_post_unauthorized_contract(self):
        """Test post update without authentication."""
        post_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        response = client.put(
            "/api/v1/posts/some-slug",
            json=post_data
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_post_invalid_token_contract(self):
        """Test post update with invalid token."""
        invalid_token = "Bearer invalid_token"
        post_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        response = client.put(
            "/api/v1/posts/some-slug",
            json=post_data,
            headers={"Authorization": invalid_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_post_not_found_contract(self):
        """Test updating non-existent post."""
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        response = client.put(
            "/api/v1/posts/non-existent-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_update_post_validation_error_contract(self):
        """Test post update with validation errors."""
        valid_token = "Bearer valid_jwt_token_here"
        # Missing required title
        post_data = {
            "content": "Content without title"
        }
        
        response = client.put(
            "/api/v1/posts/some-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_update_post_partial_update_contract(self):
        """Test partial post update."""
        valid_token = "Bearer valid_jwt_token_here"
        # Only update title, keep other fields unchanged
        post_data = {
            "title": "Only Updated Title"
        }
        
        response = client.put(
            "/api/v1/posts/existing-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Updated Title"
        assert "content" in data  # Should preserve existing content
        assert "updated_at" in data

    def test_update_post_slug_unchanged_contract(self):
        """Test that slug remains unchanged during update."""
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Completely Different Title",
            "content": "New content"
        }
        
        response = client.put(
            "/api/v1/posts/original-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Slug should remain unchanged even with new title
        assert data["slug"] == "original-slug"
        assert data["title"] == "Completely Different Title"

    def test_update_post_tag_management_contract(self):
        """Test tag management during post update."""
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Post with Tags",
            "tags": ["new-tag", "existing-tag"]
        }
        
        response = client.put(
            "/api/v1/posts/post-with-tags",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tags"], list)
        assert "new-tag" in [tag["name"] for tag in data["tags"]]
        assert "existing-tag" in [tag["name"] for tag in data["tags"]]

    def test_update_post_wrong_http_method_contract(self):
        """Test wrong HTTP method returns 405."""
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Updated Title"
        }
        
        response = client.patch(  # Using PATCH instead of PUT
            "/api/v1/posts/some-slug",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 405

    def test_update_post_invalid_json_contract(self):
        """Test post update with invalid JSON."""
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.put(
            "/api/v1/posts/some-slug",
            data="invalid json",  # Not JSON
            headers={"Authorization": valid_token, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_update_post_permission_denied_contract(self):
        """Test updating post owned by different user."""
        valid_token = "Bearer valid_jwt_token_different_user"
        post_data = {
            "title": "Trying to update someone else's post"
        }
        
        response = client.put(
            "/api/v1/posts/other-users-post",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 403
        assert "detail" in response.json()

    def test_update_post_preserve_metadata_contract(self):
        """Test that metadata is preserved during update."""
        valid_token = "Bearer valid_jwt_token_here"
        post_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        response = client.put(
            "/api/v1/posts/existing-post",
            json=post_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        # These fields should be preserved/managed by backend
        assert "created_at" in data
        assert "updated_at" in data
        assert "view_count" in data
        assert "author" in data
        assert data["author"]["id"] is not None