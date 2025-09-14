"""
Contract tests for POST /api/v1/posts endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient

# Mock data for testing
valid_post_data = {
    "title": "Test Blog Post",
    "content": "This is the content of the test blog post. It should be at least 10 characters long.",
    "excerpt": "This is a test excerpt",
    "status": "draft",
    "tags": ["python", "testing"]
}

invalid_post_data = {
    "title": "",  # Invalid empty title
    "content": "Short"  # Invalid short content
}


class TestPostsCreateContract:
    """Contract tests for posts create endpoint."""

    @pytest.mark.contract
    async def test_create_post_success_contract(self):
        """Test successful blog post creation with valid data."""
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=valid_post_data,
                headers={"Authorization": valid_token}
            )
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match BlogPost schema
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "slug" in data
        assert "content" in data
        assert "excerpt" in data
        assert "status" in data
        assert "author" in data
        assert "tags" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Validate returned data matches input
        assert data["title"] == valid_post_data["title"]
        assert data["content"] == valid_post_data["content"]
        assert data["excerpt"] == valid_post_data["excerpt"]
        assert data["status"] == valid_post_data["status"]
        
        # Slug should be auto-generated
        assert isinstance(data["slug"], str)
        assert len(data["slug"]) > 0
        
        # Tags should be resolved
        assert isinstance(data["tags"], list)
        assert len(data["tags"]) == len(valid_post_data["tags"])

    @pytest.mark.contract
    async def test_create_post_unauthorized_contract(self):
        """Test creating post without authentication returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=valid_post_data
            )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "MISSING_TOKEN"

    @pytest.mark.contract
    async def test_create_post_validation_error_contract(self):
        """Test creating post with invalid data returns 422."""
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=invalid_post_data,
                headers={"Authorization": valid_token}
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match validation error schema
        data = response.json()
        assert "detail" in data
        errors = data["detail"]
        
        # Should have validation errors for invalid fields
        error_fields = {error.get("field") for error in errors}
        assert "title" in error_fields  # Empty title
        assert "content" in error_fields  # Short content

    @pytest.mark.contract
    async def test_create_post_minimal_data_contract(self):
        """Test creating post with minimal required data."""
        minimal_post_data = {
            "title": "Minimal Post",
            "content": "This is the minimal content for a blog post that meets the requirements."
        }
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=minimal_post_data,
                headers={"Authorization": valid_token}
            )
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Should fill in default values
        data = response.json()
        assert data["title"] == minimal_post_data["title"]
        assert data["content"] == minimal_post_data["content"]
        assert data["status"] == "draft"  # Default status
        assert data["excerpt"] is None  # Optional field
        assert isinstance(data["tags"], list)  # Default empty list

    @pytest.mark.contract
    async def test_create_post_slug_generation_contract(self):
        """Test that slug is auto-generated from title."""
        post_with_special_title = {
            "title": "My Special Blog Post With Spaces & Symbols!",
            "content": "Content for testing slug generation functionality."
        }
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=post_with_special_title,
                headers={"Authorization": valid_token}
            )
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Slug should be URL-friendly version of title
        data = response.json()
        slug = data["slug"]
        assert isinstance(slug, str)
        assert " " not in slug  # No spaces
        assert "&" not in slug  # No special chars
        assert "!" not in slug  # No special chars
        assert slug.lower() == slug  # Should be lowercase

    @pytest.mark.contract
    async def test_create_post_duplicate_slug_handling_contract(self):
        """Test handling of duplicate slug scenarios."""
        post_data = {
            "title": "Duplicate Title Test",
            "content": "Testing duplicate slug handling in the API."
        }
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Create first post
            response1 = await client.post(
                "/api/v1/posts",
                json=post_data,
                headers={"Authorization": valid_token}
            )
            assert response1.status_code == 201
            
            # Create second post with same title
            response2 = await client.post(
                "/api/v1/posts",
                json=post_data,
                headers={"Authorization": valid_token}
            )
            
            # Should either succeed with different slug or return conflict
            assert response2.status_code in [201, 409]
            
            if response2.status_code == 201:
                # Slugs should be different
                slug1 = response1.json()["slug"]
                slug2 = response2.json()["slug"]
                assert slug1 != slug2

    @pytest.mark.contract
    async def test_create_post_invalid_json_contract(self):
        """Test creating post with invalid JSON returns 422."""
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                content="invalid json",
                headers={
                    "Authorization": valid_token,
                    "content-type": "application/json"
                }
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    @pytest.mark.contract
    async def test_create_post_tag_handling_contract(self):
        """Test that tags are properly handled in post creation."""
        post_with_tags = {
            "title": "Post with Tags",
            "content": "Testing tag handling in post creation.",
            "tags": ["python", "fastapi", "new-tag-that-does-not-exist"]
        }
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/posts",
                json=post_with_tags,
                headers={"Authorization": valid_token}
            )
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Tags should be processed (created if needed)
        data = response.json()
        returned_tags = [tag["name"] for tag in data["tags"]]
        
        # All requested tags should be present
        for requested_tag in post_with_tags["tags"]:
            assert requested_tag in returned_tags