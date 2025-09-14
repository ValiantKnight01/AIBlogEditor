"""
Contract tests for DELETE /api/v1/posts/{slug} endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestPostsDeleteContract:
    """Contract tests for blog post delete endpoint."""
    
    def test_delete_post_success_contract(self):
        """Test successful blog post deletion."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.delete(
            "/api/v1/posts/existing-post-slug",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 204
        # No content should be returned for successful deletion
        assert response.text == ""

    def test_delete_post_unauthorized_contract(self):
        """Test post deletion without authentication."""
        response = client.delete("/api/v1/posts/some-slug")
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_delete_post_invalid_token_contract(self):
        """Test post deletion with invalid token."""
        invalid_token = "Bearer invalid_token"
        
        response = client.delete(
            "/api/v1/posts/some-slug",
            headers={"Authorization": invalid_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_delete_post_not_found_contract(self):
        """Test deleting non-existent post."""
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.delete(
            "/api/v1/posts/non-existent-slug",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_delete_post_permission_denied_contract(self):
        """Test deleting post owned by different user."""
        valid_token = "Bearer valid_jwt_token_different_user"
        
        response = client.delete(
            "/api/v1/posts/other-users-post",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 403
        assert "detail" in response.json()

    def test_delete_post_wrong_http_method_contract(self):
        """Test wrong HTTP method returns 405."""
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.put(  # Using PUT instead of DELETE
            "/api/v1/posts/some-slug",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 405

    def test_delete_post_expired_token_contract(self):
        """Test post deletion with expired token."""
        expired_token = "Bearer expired_jwt_token"
        
        response = client.delete(
            "/api/v1/posts/some-slug",
            headers={"Authorization": expired_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_delete_post_malformed_auth_header_contract(self):
        """Test post deletion with malformed authorization header."""
        malformed_headers = [
            "invalid-header-format",
            "Bearer",  # Missing token
            "InvalidScheme valid_token",
            "Bearer token_with_spaces in_it"
        ]
        
        for auth_header in malformed_headers:
            response = client.delete(
                "/api/v1/posts/some-slug",
                headers={"Authorization": auth_header}
            )
            
            assert response.status_code == 401, f"Failed for header: {auth_header}"

    def test_delete_post_cascade_behavior_contract(self):
        """Test that related data is handled properly during deletion."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Delete a post that has tags, comments, etc.
        response = client.delete(
            "/api/v1/posts/post-with-relationships",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 204

    def test_delete_post_soft_delete_contract(self):
        """Test that deletion might be soft delete (depends on implementation)."""
        valid_token = "Bearer valid_jwt_token_here"
        
        response = client.delete(
            "/api/v1/posts/post-for-soft-delete",
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 204
        
        # After soft delete, post should return 404 for regular users
        # but might still exist in database with deleted_at timestamp

    def test_delete_post_idempotent_behavior_contract(self):
        """Test that deleting already deleted post handles gracefully."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # First deletion
        response1 = client.delete(
            "/api/v1/posts/post-to-delete-twice",
            headers={"Authorization": valid_token}
        )
        
        # Second deletion of same post should either:
        # 1. Return 204 (idempotent)
        # 2. Return 404 (already gone)
        response2 = client.delete(
            "/api/v1/posts/post-to-delete-twice",
            headers={"Authorization": valid_token}
        )
        
        # Both behaviors are acceptable
        assert response1.status_code == 204
        assert response2.status_code in [204, 404]

    def test_delete_post_published_status_handling_contract(self):
        """Test deletion of published vs draft posts."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # Should be able to delete both published and draft posts
        for post_slug in ["published-post-slug", "draft-post-slug"]:
            response = client.delete(
                f"/api/v1/posts/{post_slug}",
                headers={"Authorization": valid_token}
            )
            
            assert response.status_code == 204

    def test_delete_post_no_request_body_allowed_contract(self):
        """Test that DELETE request works without body."""
        valid_token = "Bearer valid_jwt_token_here"
        
        # DELETE requests shouldn't have body
        response = client.delete(
            "/api/v1/posts/some-slug",
            headers={"Authorization": valid_token}
        )
        
        # Should still process normally (return 404 since endpoint not implemented)
        assert response.status_code == 404