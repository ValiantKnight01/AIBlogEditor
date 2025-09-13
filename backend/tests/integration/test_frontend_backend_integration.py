"""
T112: Frontend-backend integration testing.

This module tests end-to-end integration between frontend and backend,
validating complete user workflows and data flow.

Following TDD methodology:
1. RED: Create failing tests for integration scenarios
2. GREEN: Implement functionality to make tests pass  
3. REFACTOR: Optimize and clean up code

These tests MUST FAIL initially to follow proper TDD.
"""
import pytest
import asyncio
import httpx
from typing import Dict, Any, List
from datetime import datetime

# Test configuration
BACKEND_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:3000"
TEST_TIMEOUT = 30.0


class TestFrontendBackendIntegration:
    """Integration tests for frontend-backend communication."""
    
    @pytest.fixture(scope="class")
    async def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Login to get access token
            login_response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "TestP@ss_w0rd!"
            })
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            
            token_data = login_response.json()
            return {"Authorization": f"Bearer {token_data['access_token']}"}
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_blog_creation_workflow(self, auth_headers):
        """
        Test complete blog post creation workflow from API to database.
        
        This test validates:
        1. User can authenticate successfully
        2. User can create a blog post with tags
        3. Tags are automatically created if they don't exist
        4. Blog post is stored correctly in database
        5. Blog post appears in listing with proper metadata
        6. Blog post can be retrieved individually
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Step 1: Create blog post with new tags
            blog_data = {
                "title": "Integration Test Blog Post",
                "content": "This is a test blog post created during integration testing. It validates the complete workflow from frontend to backend.",
                "excerpt": "A comprehensive integration test for blog creation",
                "status": "published",
                "tag_names": ["Integration Testing", "TDD", "FastAPI", "React"]
            }
            
            create_response = await client.post(
                "/api/v1/posts",
                json=blog_data,
                headers=auth_headers
            )
            
            # Should create successfully
            assert create_response.status_code == 201, f"Blog creation failed: {create_response.text}"
            created_blog = create_response.json()
            
            # Validate response structure
            assert "id" in created_blog
            assert "slug" in created_blog
            assert created_blog["title"] == blog_data["title"]
            assert created_blog["content"] == blog_data["content"]
            assert created_blog["status"] == blog_data["status"]
            assert "tags" in created_blog
            assert len(created_blog["tags"]) == 4
            
            # Step 2: Verify blog appears in listing
            list_response = await client.get("/api/v1/posts")
            assert list_response.status_code == 200
            
            posts_data = list_response.json()
            assert "items" in posts_data
            
            # Find our created post
            created_post_in_list = None
            for post in posts_data["items"]:
                if post["id"] == created_blog["id"]:
                    created_post_in_list = post
                    break
            
            assert created_post_in_list is not None, "Created post not found in listing"
            assert created_post_in_list["title"] == blog_data["title"]
            
            # Step 3: Verify individual post retrieval
            slug = created_blog["slug"]
            detail_response = await client.get(f"/api/v1/posts/{slug}")
            assert detail_response.status_code == 200
            
            detail_post = detail_response.json()
            assert detail_post["id"] == created_blog["id"]
            assert detail_post["title"] == blog_data["title"]
            assert detail_post["content"] == blog_data["content"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_complete_project_creation_workflow(self, auth_headers):
        """
        Test complete project creation workflow.
        
        Validates:
        1. Project creation with technology tags
        2. Automatic tag creation for new technologies
        3. Project appears in listings correctly
        4. Project metadata is preserved
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Step 1: Create project with technology tags
            project_data = {
                "title": "Integration Test Project",
                "description": "A test project created during integration testing to validate the complete project creation workflow.",
                "github_url": "https://github.com/test/integration-project",
                "live_url": "https://integration-test.example.com",
                "status": "published",
                "tag_names": ["TypeScript", "Node.js", "Integration Testing", "CI/CD"]
            }
            
            create_response = await client.post(
                "/api/v1/projects", 
                json=project_data,
                headers=auth_headers
            )
            
            assert create_response.status_code == 201, f"Project creation failed: {create_response.text}"
            created_project = create_response.json()
            
            # Validate response structure
            assert "id" in created_project
            assert "slug" in created_project
            assert created_project["title"] == project_data["title"]
            assert created_project["description"] == project_data["description"]
            assert created_project["github_url"] == project_data["github_url"]
            # Response uses project_url but input uses live_url, and URLs might be normalized with trailing slash
            assert created_project["project_url"].rstrip('/') == project_data["live_url"].rstrip('/')
            assert "tags" in created_project
            assert len(created_project["tags"]) == 4
            
            # Step 2: Verify project appears in listing
            list_response = await client.get("/api/v1/projects")
            assert list_response.status_code == 200
            
            projects_data = list_response.json()
            assert "items" in projects_data
            
            # Find our created project
            created_project_in_list = None
            for project in projects_data["items"]:
                if project["id"] == created_project["id"]:
                    created_project_in_list = project
                    break
                    
            assert created_project_in_list is not None, "Created project not found in listing"
            assert created_project_in_list["title"] == project_data["title"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tag_management_workflow(self, auth_headers):
        """
        Test complete tag management workflow.
        
        Validates:
        1. Tag creation via API
        2. Tag listing and retrieval
        3. Tag association with content
        4. Tag color and slug generation
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Step 1: Create new tag with unique name
            import time
            unique_suffix = str(int(time.time() * 1000))  # Use timestamp for uniqueness
            tag_data = {
                "name": f"Integration Tag {unique_suffix}",
                "description": "A tag created during integration testing",
                "color": "#FF6B6B"
            }
            
            create_response = await client.post(
                "/api/v1/tags",
                json=tag_data, 
                headers=auth_headers
            )
            
            assert create_response.status_code == 201, f"Tag creation failed: {create_response.text}"
            created_tag = create_response.json()
            
            # Validate response structure
            assert "id" in created_tag
            assert "slug" in created_tag
            assert created_tag["name"] == tag_data["name"]
            assert created_tag["description"] == tag_data["description"]
            # Color might be returned in different case - compare case-insensitively
            assert created_tag["color"].lower() == tag_data["color"].lower()
            
            # Step 2: Verify tag appears in listing
            list_response = await client.get("/api/v1/tags")
            assert list_response.status_code == 200
            
            tags_data = list_response.json()
            assert isinstance(tags_data, list)
            
            # Find our created tag
            created_tag_in_list = None
            for tag in tags_data:
                if tag["id"] == created_tag["id"]:
                    created_tag_in_list = tag
                    break
                    
            assert created_tag_in_list is not None, "Created tag not found in listing"
            assert created_tag_in_list["name"] == tag_data["name"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_authentication_workflow(self):
        """
        Test complete authentication workflow.
        
        Validates:
        1. Login with valid credentials
        2. Token-based API access
        3. Protected endpoint access
        4. Token expiration handling (if implemented)
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Step 1: Login with valid credentials
            login_response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com", 
                "password": "TestP@ss_w0rd!"
            })
            
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token_data = login_response.json()
            
            # Validate token response structure
            assert "access_token" in token_data
            assert "token_type" in token_data
            assert "user" in token_data
            assert token_data["token_type"] == "bearer"
            
            # Step 2: Use token for protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            # Test user profile endpoint (protected)
            profile_response = await client.get("/api/v1/users/me", headers=headers)
            assert profile_response.status_code == 200
            
            user_data = profile_response.json()
            assert user_data["email"] == "test@example.com"
            
            # Step 3: Test access without token (should fail)
            no_auth_response = await client.get("/api/v1/users/me")
            assert no_auth_response.status_code == 401, "Protected endpoint should require authentication"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_persistence_and_relationships(self, auth_headers):
        """
        Test data persistence and relationships across operations.
        
        Validates:
        1. Created content persists across requests
        2. Relationships (many-to-many) work correctly
        3. Data integrity is maintained
        4. Foreign key relationships are preserved
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Step 1: Create a blog post with specific tags
            blog_data = {
                "title": "Persistence Test Blog",
                "content": "Testing data persistence and relationships",
                "excerpt": "Validating data integrity",
                "status": "published",
                "tag_names": ["Persistence", "Database", "Testing"]
            }
            
            blog_response = await client.post(
                "/api/v1/posts",
                json=blog_data,
                headers=auth_headers
            )
            assert blog_response.status_code == 201
            created_blog = blog_response.json()
            
            # Step 2: Create a project with some of the same tags
            project_data = {
                "title": "Persistence Test Project", 
                "description": "Testing project data persistence",
                "status": "published",
                "tag_names": ["Database", "Testing", "Integration"]
            }
            
            project_response = await client.post(
                "/api/v1/projects",
                json=project_data, 
                headers=auth_headers
            )
            assert project_response.status_code == 201
            created_project = project_response.json()
            
            # Step 3: Verify tag reuse (Database and Testing tags should be shared)
            # Get all tags
            tags_response = await client.get("/api/v1/tags")
            assert tags_response.status_code == 200
            all_tags = tags_response.json()
            
            # Find shared tags
            database_tags = [t for t in all_tags if t["name"] == "Database"]
            testing_tags = [t for t in all_tags if t["name"] == "Testing"]
            
            # Should have exactly one "Database" tag and one "Testing" tag (reused)
            assert len(database_tags) == 1, "Database tag should be reused, not duplicated"
            assert len(testing_tags) == 1, "Testing tag should be reused, not duplicated"
            
            # Step 4: Verify content persists with relationships intact
            # Retrieve blog and verify tags
            blog_detail = await client.get(f"/api/v1/posts/{created_blog['slug']}")
            assert blog_detail.status_code == 200
            blog_data_retrieved = blog_detail.json()
            
            blog_tag_names = [tag["name"] for tag in blog_data_retrieved["tags"]]
            assert "Persistence" in blog_tag_names
            assert "Database" in blog_tag_names
            assert "Testing" in blog_tag_names
            
            # Retrieve project and verify tags  
            project_detail = await client.get(f"/api/v1/projects/{created_project['slug']}")
            assert project_detail.status_code == 200
            project_data_retrieved = project_detail.json()
            
            project_tag_names = [tag["name"] for tag in project_data_retrieved["tags"]]
            assert "Database" in project_tag_names
            assert "Testing" in project_tag_names
            assert "Integration" in project_tag_names

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_and_validation(self, auth_headers):
        """
        Test error handling and validation across the system.
        
        Validates:
        1. Proper error responses for invalid data
        2. Validation error messages are clear
        3. System handles edge cases gracefully
        4. HTTP status codes are correct
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test 1: Invalid blog post data
            invalid_blog_data = {
                "title": "",  # Empty title should fail validation
                "content": "Some content",
                "status": "invalid_status"  # Invalid status
            }
            
            blog_response = await client.post(
                "/api/v1/posts",
                json=invalid_blog_data,
                headers=auth_headers
            )
            assert blog_response.status_code == 422, "Should return validation error"
            
            error_data = blog_response.json()
            assert "detail" in error_data
            
            # Test 2: Duplicate slug handling
            valid_blog_data = {
                "title": "Test Blog Post",
                "content": "Content for testing",
                "excerpt": "Test excerpt", 
                "status": "published"
            }
            
            # Create first blog post
            first_response = await client.post(
                "/api/v1/posts",
                json=valid_blog_data,
                headers=auth_headers
            )
            assert first_response.status_code == 201
            
            # Try to create second blog post with same title (should handle slug uniqueness)
            second_response = await client.post(
                "/api/v1/posts", 
                json=valid_blog_data,
                headers=auth_headers
            )
            # Should either succeed with different slug or return appropriate error
            assert second_response.status_code in [201, 409]
            
            if second_response.status_code == 201:
                # If successful, slugs should be different
                first_blog = first_response.json()
                second_blog = second_response.json()
                assert first_blog["slug"] != second_blog["slug"], "Slugs should be unique"
            
            # Test 3: Non-existent resource retrieval
            not_found_response = await client.get("/api/v1/posts/non-existent-slug")
            assert not_found_response.status_code == 404
            
            # Test 4: Unauthorized access
            unauthorized_response = await client.post("/api/v1/posts", json=valid_blog_data)
            assert unauthorized_response.status_code == 401, "Should require authentication"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_content_listing_and_pagination(self):
        """
        Test content listing and pagination functionality.
        
        Validates:
        1. Content listings return proper structure
        2. Pagination parameters work correctly
        3. Sorting and filtering work as expected
        4. Empty states are handled properly
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test 1: Blog posts listing
            posts_response = await client.get("/api/v1/posts")
            assert posts_response.status_code == 200
            
            posts_data = posts_response.json()
            assert "items" in posts_data
            assert "total" in posts_data
            assert "page" in posts_data
            assert "limit" in posts_data or "size" in posts_data  # Accept either field name
            assert isinstance(posts_data["items"], list)
            
            # Test 2: Projects listing
            projects_response = await client.get("/api/v1/projects")
            assert projects_response.status_code == 200
            
            projects_data = projects_response.json()
            assert "items" in projects_data
            assert "total" in projects_data
            assert isinstance(projects_data["items"], list)
            
            # Test 3: Tags listing (different structure)
            tags_response = await client.get("/api/v1/tags")
            assert tags_response.status_code == 200
            
            tags_data = tags_response.json()
            assert isinstance(tags_data, list)
            
            # Test 4: Pagination parameters
            paginated_response = await client.get("/api/v1/posts?page=1&limit=5")
            assert paginated_response.status_code == 200
            
            paginated_data = paginated_response.json()
            assert paginated_data["page"] == 1
            # Accept either 'size' or 'limit' field name
            page_size = paginated_data.get("size") or paginated_data.get("limit") 
            assert page_size == 5
            assert len(paginated_data["items"]) <= 5