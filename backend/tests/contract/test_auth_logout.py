"""
Contract tests for POST /api/v1/auth/logout endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient


class TestAuthLogoutContract:
    """Contract tests for auth logout endpoint."""

    @pytest.mark.contract
    async def test_logout_success_contract(self):
        """Test successful logout with valid bearer token."""
        # Mock valid JWT token
        valid_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": valid_token}
            )
        
        # Should return 204 No Content
        assert response.status_code == 204
        
        # Should not return any content
        assert len(response.content) == 0

    @pytest.mark.contract
    async def test_logout_missing_token_contract(self):
        """Test logout without authentication token returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/api/v1/auth/logout")
        
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
    async def test_logout_invalid_token_contract(self):
        """Test logout with invalid token returns 401."""
        invalid_token = "Bearer invalid-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/logout",
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
    async def test_logout_expired_token_contract(self):
        """Test logout with expired token returns 401."""
        # Mock expired JWT token
        expired_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj_jkIzDhKlTKD_b4wJC7YLKRMkW7LYWnqX_z8gY"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/logout",
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
    async def test_logout_malformed_authorization_header_contract(self):
        """Test logout with malformed Authorization header returns 401."""
        malformed_headers = [
            "invalid-header-format",
            "Basic somebasictoken",  # Wrong auth type
            "Bearer",  # Missing token
            "Bearer token with spaces",  # Invalid token format
        ]
        
        for header_value in malformed_headers:
            async with AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.post(
                    "/api/v1/auth/logout",
                    headers={"Authorization": header_value}
                )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401, f"Failed for header: {header_value}"
            
            # Should return JSON content type
            assert response.headers["content-type"] == "application/json"

    @pytest.mark.contract
    async def test_logout_wrong_http_method_contract(self):
        """Test that other HTTP methods are not allowed on logout endpoint."""
        valid_token = "Bearer valid-test-token"
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test GET method
            response = await client.get(
                "/api/v1/auth/logout",
                headers={"Authorization": valid_token}
            )
            assert response.status_code == 405  # Method Not Allowed
            
            # Test PUT method
            response = await client.put(
                "/api/v1/auth/logout",
                headers={"Authorization": valid_token}
            )
            assert response.status_code == 405  # Method Not Allowed
            
            # Test DELETE method
            response = await client.delete(
                "/api/v1/auth/logout",
                headers={"Authorization": valid_token}
            )
            assert response.status_code == 405  # Method Not Allowed