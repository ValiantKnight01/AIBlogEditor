"""
Contract tests for GET /api/v1/posts endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient


class TestPostsListContract:
    """Contract tests for posts list endpoint."""

    @pytest.mark.contract
    async def test_list_posts_success_contract(self):
        """Test successful listing of published blog posts."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match PaginatedBlogPosts schema
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        # Validate pagination data
        assert isinstance(data["items"], list)
        assert isinstance(data["page"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["total"], int)
        assert isinstance(data["pages"], int)
        assert isinstance(data["has_next"], bool)
        assert isinstance(data["has_prev"], bool)
        
        # Validate blog post items structure (if any)
        for post in data["items"]:
            assert "id" in post
            assert "title" in post
            assert "slug" in post
            assert "excerpt" in post
            assert "status" in post
            assert "published_at" in post
            assert "author" in post
            assert "tags" in post
            assert "view_count" in post
            
            # Only published posts should be returned
            assert post["status"] == "published"
            assert post["published_at"] is not None

    @pytest.mark.contract
    async def test_list_posts_pagination_contract(self):
        """Test posts list pagination parameters."""
        # Test with custom page and limit
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts?page=2&limit=5")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should respect pagination parameters
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 5
        assert len(data["items"]) <= 5

    @pytest.mark.contract
    async def test_list_posts_invalid_page_contract(self):
        """Test posts list with invalid page parameter."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts?page=0")  # Invalid page
        
        # Should return 422 Validation Error
        assert response.status_code == 422
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match validation error schema
        data = response.json()
        assert "detail" in data
        errors = data["detail"]
        
        # Should have validation error for page parameter
        page_error = next(
            (error for error in errors if error.get("field") == "page"), 
            None
        )
        assert page_error is not None

    @pytest.mark.contract
    async def test_list_posts_invalid_limit_contract(self):
        """Test posts list with invalid limit parameter."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test limit too high
            response = await client.get("/api/v1/posts?limit=100")  # Max is 50
        
        # Should return 422 Validation Error
        assert response.status_code == 422
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.contract
    async def test_list_posts_tag_filter_contract(self):
        """Test posts list filtered by tag."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts?tag=python")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match PaginatedBlogPosts schema
        data = response.json()
        assert "items" in data
        
        # All returned posts should have the specified tag
        for post in data["items"]:
            tag_slugs = [tag["slug"] for tag in post["tags"]]
            assert "python" in tag_slugs

    @pytest.mark.contract
    async def test_list_posts_empty_result_contract(self):
        """Test posts list when no posts match criteria."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts?tag=nonexistent-tag")
        
        # Should return 200 OK even with empty results
        assert response.status_code == 200
        
        # Should return empty list
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 0
        assert data["has_next"] is False
        assert data["has_prev"] is False

    @pytest.mark.contract
    async def test_list_posts_wrong_http_method_contract(self):
        """Test that only GET method is allowed on posts list endpoint."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test PUT method
            response = await client.put("/api/v1/posts")
            assert response.status_code == 405  # Method Not Allowed
            
            # Test DELETE method
            response = await client.delete("/api/v1/posts")
            assert response.status_code == 405  # Method Not Allowed

    @pytest.mark.contract
    async def test_list_posts_default_pagination_contract(self):
        """Test posts list with default pagination values."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should use default pagination values
        data = response.json()
        assert data["page"] == 1  # Default page
        assert data["limit"] == 10  # Default limit
        assert len(data["items"]) <= 10  # Should not exceed limit

    @pytest.mark.contract
    async def test_list_posts_author_info_contract(self):
        """Test that author information is included in posts list."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/posts")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate author information in posts
        for post in data["items"]:
            author = post["author"]
            assert "id" in author
            assert "username" in author
            assert "full_name" in author
            
            # Should not include sensitive information
            assert "password_hash" not in author
            assert "email" not in author  # Email might be sensitive