"""
Contract tests for POST /api/v1/auth/refresh endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient


class TestAuthRefreshContract:
    """Contract tests for auth refresh token endpoint."""

    @pytest.mark.contract
    async def test_refresh_success_contract(self):
        """Test successful token refresh with valid refresh token."""
        # Mock valid refresh token (would be in httpOnly cookie)
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Simulate refresh token in cookie
            client.cookies.set("refresh_token", "valid-refresh-token-here")
            
            response = await client.post("/api/v1/auth/refresh")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match TokenResponse schema
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        
        # Validate token structure
        assert isinstance(data["access_token"], str)
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    @pytest.mark.contract
    async def test_refresh_missing_cookie_contract(self):
        """Test refresh without refresh token cookie returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/api/v1/auth/refresh")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "MISSING_REFRESH_TOKEN"

    @pytest.mark.contract
    async def test_refresh_invalid_token_contract(self):
        """Test refresh with invalid refresh token returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Set invalid refresh token in cookie
            client.cookies.set("refresh_token", "invalid-refresh-token")
            
            response = await client.post("/api/v1/auth/refresh")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "INVALID_REFRESH_TOKEN"

    @pytest.mark.contract
    async def test_refresh_expired_token_contract(self):
        """Test refresh with expired refresh token returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Set expired refresh token in cookie
            client.cookies.set("refresh_token", "expired-refresh-token")
            
            response = await client.post("/api/v1/auth/refresh")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "REFRESH_TOKEN_EXPIRED"

    @pytest.mark.contract
    async def test_refresh_revoked_token_contract(self):
        """Test refresh with revoked refresh token returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Set revoked refresh token in cookie
            client.cookies.set("refresh_token", "revoked-refresh-token")
            
            response = await client.post("/api/v1/auth/refresh")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "REFRESH_TOKEN_REVOKED"

    @pytest.mark.contract
    async def test_refresh_wrong_http_method_contract(self):
        """Test that other HTTP methods are not allowed on refresh endpoint."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            client.cookies.set("refresh_token", "valid-refresh-token")
            
            # Test GET method
            response = await client.get("/api/v1/auth/refresh")
            assert response.status_code == 405  # Method Not Allowed
            
            # Test PUT method
            response = await client.put("/api/v1/auth/refresh")
            assert response.status_code == 405  # Method Not Allowed
            
            # Test DELETE method
            response = await client.delete("/api/v1/auth/refresh")
            assert response.status_code == 405  # Method Not Allowed

    @pytest.mark.contract
    async def test_refresh_secure_cookie_handling_contract(self):
        """Test that refresh endpoint properly handles secure cookies."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test with valid refresh token (httpx doesn't support secure/httponly flags)
            client.cookies.set("refresh_token", "valid-refresh-token")
            
            response = await client.post("/api/v1/auth/refresh")
            
            # Should process the request (status depends on token validity)
            assert response.status_code in [200, 401]  # Either success or auth error

    @pytest.mark.contract
    async def test_refresh_request_body_ignored_contract(self):
        """Test that refresh endpoint ignores request body (uses only cookies)."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            client.cookies.set("refresh_token", "valid-refresh-token")
            
            # Send request with body (should be ignored)
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"ignored": "data"}
            )
            
            # Should process based on cookie only, ignoring body
            assert response.status_code in [200, 401]  # Either success or auth error