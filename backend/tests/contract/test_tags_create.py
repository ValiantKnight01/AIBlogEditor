"""
Contract tests for POST /api/v1/tags endpoint.
These tests MUST FAIL initially as part of TDD approach.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestTagsCreateContract:
    """Contract tests for tag creation endpoint."""
    
    def test_create_tag_success_contract(self):
        """Test successful tag creation."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "Python",
            "color": "#3776ab"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Python"
        assert data["color"] == "#3776ab"
        assert data["slug"] == "python"
        assert data["usage_count"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_create_tag_minimal_data_contract(self):
        """Test creating tag with minimal required data."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "JavaScript"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "JavaScript"
        assert data["slug"] == "javascript"
        assert data["usage_count"] == 0
        assert data["color"] is not None  # Should have default color

    def test_create_tag_with_special_characters_contract(self):
        """Test creating tag with special characters in name."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "C++",
            "color": "#00599c"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "C++"
        assert data["slug"] == "c-plus-plus"  # Should handle special characters

    def test_create_tag_duplicate_name_contract(self):
        """Test creating tag with duplicate name."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "Python",  # Assuming this already exists
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_create_tag_unauthorized_contract(self):
        """Test creating tag without authentication."""
        # This test MUST FAIL until endpoint is implemented
        tag_data = {
            "name": "Unauthorized Tag",
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_tag_invalid_token_contract(self):
        """Test creating tag with invalid token."""
        # This test MUST FAIL until endpoint is implemented
        invalid_token = "Bearer invalid_token"
        
        tag_data = {
            "name": "Invalid Token Tag",
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": invalid_token}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_tag_invalid_data_contract(self):
        """Test creating tag with invalid data."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        # Test empty name
        invalid_data = {
            "name": "",
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=invalid_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_tag_invalid_color_contract(self):
        """Test creating tag with invalid color format."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "Invalid Color Tag",
            "color": "not-a-hex-color"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_tag_missing_name_contract(self):
        """Test creating tag without required name field."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "color": "#ff0000"
            # Missing required "name" field
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_tag_name_too_long_contract(self):
        """Test creating tag with name that's too long."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "a" * 100,  # Very long name
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_tag_name_normalization_contract(self):
        """Test tag name normalization and whitespace handling."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "  React.js  ",  # Name with leading/trailing whitespace
            "color": "#61dafb"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "React.js"  # Should be trimmed
        assert data["slug"] == "react-js"

    def test_create_tag_case_insensitive_duplicate_contract(self):
        """Test case-insensitive duplicate detection."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "PYTHON",  # Different case of existing tag
            "color": "#ff0000"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_create_tag_unicode_characters_contract(self):
        """Test creating tag with unicode characters."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "Español",  # Unicode characters
            "color": "#ff6b6b"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Español"
        assert data["slug"] == "espanol"  # Should handle unicode in slug

    def test_create_tag_color_validation_contract(self):
        """Test various color format validations."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        # Test valid 6-digit hex color
        tag_data = {
            "name": "Valid Color Tag",
            "color": "#ff6b6b"
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201

    def test_create_tag_color_short_format_contract(self):
        """Test 3-digit hex color format."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "Short Color Tag",
            "color": "#f6b"  # 3-digit hex color
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        # Should either accept it or convert to full format
        assert response.status_code == 201
        data = response.json()
        assert len(data["color"]) == 7  # Should be converted to full format

    def test_create_tag_default_color_contract(self):
        """Test default color assignment when not provided."""
        # This test MUST FAIL until endpoint is implemented
        valid_token = "Bearer valid_jwt_token_here"
        
        tag_data = {
            "name": "No Color Tag"
            # No color provided
        }
        
        response = client.post(
            "/api/v1/tags",
            json=tag_data,
            headers={"Authorization": valid_token}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["color"] is not None
        assert data["color"].startswith("#")
        assert len(data["color"]) == 7