"""
Contract tests for POST /api/v1/auth/login endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from httpx import AsyncClient
import json

# Mock data for testing
valid_login_data = {
    "email": "test@example.com",
    "password": "SecureP@ssw0rd!"
}

invalid_login_data = {
    "email": "invalid@example.com", 
    "password": "wrongpassword"
}

incomplete_login_data = {
    "email": "test@example.com"
    # missing password
}


class TestAuthLoginContract:
    """Contract tests for auth login endpoint."""

    @pytest.mark.contract
    async def test_login_success_contract(self):
        """Test successful login returns proper response structure."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=valid_login_data
            )
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match AuthResponse schema
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        
        # Validate token structure
        assert isinstance(data["access_token"], str)
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0
        
        # Validate user data structure
        user_data = data["user"]
        assert "id" in user_data
        assert "email" in user_data
        assert "username" in user_data
        assert "full_name" in user_data
        assert isinstance(user_data["id"], str)
        assert user_data["email"] == valid_login_data["email"]

    @pytest.mark.contract
    async def test_login_invalid_credentials_contract(self):
        """Test login with invalid credentials returns 401."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=invalid_login_data
            )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match error schema
        data = response.json()
        assert "detail" in data
        assert "error_code" in data
        assert data["error_code"] == "INVALID_CREDENTIALS"

    @pytest.mark.contract
    async def test_login_validation_error_contract(self):
        """Test login with incomplete data returns 422."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=incomplete_login_data
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"
        
        # Response should match validation error schema
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        
        # Should have validation error for missing password
        errors = data["detail"]
        password_error = next(
            (error for error in errors if error.get("field") == "password"), 
            None
        )
        assert password_error is not None
        assert password_error["type"] == "missing"

    @pytest.mark.contract
    async def test_login_invalid_json_contract(self):
        """Test login with invalid JSON returns 422."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                content="invalid json",
                headers={"content-type": "application/json"}
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        
        # Should return JSON content type
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.contract
    async def test_login_missing_content_type_contract(self):
        """Test login without content-type header returns 422."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                data=json.dumps(valid_login_data)  # Send as data without JSON content-type
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    @pytest.mark.contract
    async def test_login_empty_body_contract(self):
        """Test login with empty body returns 422."""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={}
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        
        # Should have validation errors for both required fields
        data = response.json()
        assert "detail" in data
        errors = data["detail"]
        
        # Should have errors for both email and password
        error_fields = {error.get("field") for error in errors}
        assert "email" in error_fields
        assert "password" in error_fields

    @pytest.mark.contract 
    async def test_login_invalid_email_format_contract(self):
        """Test login with invalid email format returns 422."""
        invalid_email_data = {
            "email": "not-an-email",
            "password": "testpassword123"
        }
        
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json=invalid_email_data
            )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        
        # Should have validation error for email format
        data = response.json()
        errors = data["detail"]
        email_error = next(
            (error for error in errors if error.get("field") == "email"), 
            None
        )
        assert email_error is not None
        assert "email" in email_error.get("type", "").lower() or "format" in email_error.get("msg", "").lower()