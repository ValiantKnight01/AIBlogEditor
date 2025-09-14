"""
Contract tests for GET /api/v1/users/me endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient


class TestUsersGetMeContract:
    """Contract tests for users/me get endpoint."""

    @pytest.mark.contract
    async def test_get_current_user_success_contract(self):
        """Test getting current user profile with valid token."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # First, login to get a valid token
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "TestP@ss_w0rd!"
                }
            )
            
            assert login_response.status_code == 200
            login_data = login_response.json()
            access_token = login_data["access_token"]
            
            # Now test the users/me endpoint with the valid token
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match UserProfile schema
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "full_name" in data
        assert "bio" in data
        assert "avatar_url" in data
        assert "created_at" in data
        
        # Validate data types
        assert isinstance(data["id"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["username"], str)
        assert isinstance(data["created_at"], str)
        
        # Nullable fields can be None
        assert data["full_name"] is None or isinstance(data["full_name"], str)
        assert data["bio"] is None or isinstance(data["bio"], str)
        assert data["avatar_url"] is None or isinstance(data["avatar_url"], str)

    @pytest.mark.contract
    async def test_get_current_user_unauthorized_contract(self):
        """Test getting current user without token returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/users/me")
        
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
    async def test_get_current_user_invalid_token_contract(self):
        """Test getting current user with invalid token returns 401."""
        invalid_token = "Bearer invalid-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": invalid_token}
            )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "INVALID_TOKEN"

    @pytest.mark.contract
    async def test_get_current_user_expired_token_contract(self):
        """Test getting current user with expired token returns 401."""
        expired_token = "Bearer expired-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": expired_token}
            )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "TOKEN_EXPIRED"

    @pytest.mark.contract
    async def test_get_current_user_wrong_http_method_contract(self):
        """Test that other HTTP methods are not allowed (except PUT)."""
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test POST method (should be 405 since only GET and PUT are allowed)
            response = await client.post(
                "/api/v1/users/me",
                headers={"Authorization": valid_token}
            )
            assert response.status_code == 405  # Method Not Allowed
            
            # Test DELETE method
            response = await client.delete(
                "/api/v1/users/me",
                headers={"Authorization": valid_token}
            )
            assert response.status_code == 405  # Method Not Allowed

    @pytest.mark.contract
    async def test_get_current_user_no_password_in_response_contract(self):
        """Test that password hash is never included in user profile response."""
        valid_token = "Bearer valid-access-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": valid_token}
            )
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Response should NOT contain sensitive fields
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "hashed_password" not in data

    @pytest.mark.contract
    async def test_get_current_user_malformed_auth_header_contract(self):
        """Test getting current user with malformed auth header returns 401."""
        malformed_headers = [
            "invalid-format",
            "Basic sometoken",  # Wrong auth type
            "Bearer",  # Missing token part
            "",  # Empty header
        ]
        
        for header_value in malformed_headers:
            async with AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.get(
                    "/api/v1/users/me",
                    headers={"Authorization": header_value}
                )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401, f"Failed for header: {header_value}"
            
            # Should return JSON content type
            assert response.headers["content-type"] == "application/json"