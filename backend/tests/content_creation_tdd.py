"""
TDD Test Suite: Content Creation with Tag Names Support

These tests MUST FAIL FIRST to follow TDD methodology.
They test backend support for creating content with tag names instead of IDs.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.main import app
from src.config import settings
from src.models.user import User
from src.models.tag import Tag
from src.services.user_service import UserService


@pytest.fixture
def db_engine():
    """Create a database engine for testing."""
    engine = create_engine(settings.database.database_url)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(db_session: Session):
    """Get the existing test user for authentication."""
    # Use the existing test user created by create_test_data.py
    user = db_session.query(User).filter_by(email="test@example.com").first()
    if user:
        return user
    
    # If not found, create a simple user directly without password validation
    user = User(
        email="test@example.com",
        username="testuser", 
        password_hash="$2b$12$dummy",  # Dummy hash for tests
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture 
def auth_headers(client: TestClient, test_user: User, db_session: Session):
    """Get authentication headers for requests."""
    # Login with existing test user credentials
    login_data = {
        "email": "test@example.com",
        "password": "TestP@ss_w0rd!"  # Password from create_test_data.py
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        # Fallback: create basic auth token manually for testing
        from src.services.auth_service import AuthService
        auth_service = AuthService()
        access_token = auth_service.create_access_token({"sub": str(test_user.id), "email": test_user.email})
        return {"Authorization": f"Bearer {access_token}"}
    
    token_data = response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


class TestBlogPostCreationWithTagNames:
    """Test blog post creation with tag names instead of tag IDs."""
    
    def test_create_post_with_new_tag_names(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test creating a blog post with new tag names.
        Backend should auto-create tags that don't exist.
        """
        post_data = {
            "title": "Test Post with New Tags",
            "content": "This is test content for a post with new tags.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_names": ["React", "TypeScript", "FastAPI"]  # New field to support
        }
        
        # This should work - backend should create missing tags
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # These assertions MUST FAIL initially
        assert response.status_code == 201
        
        post_response = response.json()
        assert post_response["title"] == "Test Post with New Tags"
        assert len(post_response["tags"]) == 3
        
        tag_names = [tag["name"] for tag in post_response["tags"]]
        assert "React" in tag_names
        assert "TypeScript" in tag_names
        assert "FastAPI" in tag_names
        
        # Verify tags were created in database
        react_tag = db_session.query(Tag).filter_by(name="React").first()
        assert react_tag is not None
        assert react_tag.slug == "react"
    
    def test_create_post_with_existing_tag_names(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test creating a blog post with existing tag names.
        Backend should use existing tags, not create duplicates.
        """
        # Create existing tags
        existing_tag = Tag(name="Python", slug="python", color="#3776ab")
        db_session.add(existing_tag)
        db_session.commit()
        
        post_data = {
            "title": "Test Post with Existing Tags",
            "content": "This is test content for a post with existing tags.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_names": ["Python", "Django"]  # Python exists, Django is new
        }
        
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        post_response = response.json()
        assert len(post_response["tags"]) == 2
        
        # Verify existing tag was reused
        python_tags = db_session.query(Tag).filter_by(name="Python").all()
        assert len(python_tags) == 1  # Should not create duplicate
        
        # Verify new tag was created
        django_tag = db_session.query(Tag).filter_by(name="Django").first()
        assert django_tag is not None
    
    def test_create_post_with_mixed_tag_formats(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test creating a blog post supporting both tag_names and legacy tag_ids.
        Backend should handle both formats gracefully.
        """
        # Create an existing tag to reference by ID
        existing_tag = Tag(name="JavaScript", slug="javascript", color="#f7df1e")
        db_session.add(existing_tag)
        db_session.commit()
        
        post_data = {
            "title": "Test Post with Mixed Tag Formats",
            "content": "This is test content with mixed tag formats.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_ids": [existing_tag.id],  # Legacy format
            "tag_names": ["Node.js", "Express"]  # New format
        }
        
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        post_response = response.json()
        assert len(post_response["tags"]) == 3  # 1 from ID + 2 from names
        
        tag_names = [tag["name"] for tag in post_response["tags"]]
        assert "JavaScript" in tag_names
        assert "Node.js" in tag_names
        assert "Express" in tag_names
    
    def test_create_post_with_empty_tag_names(self, client: TestClient, auth_headers: dict):
        """
        Test creating a blog post with empty tag names.
        Backend should handle empty arrays gracefully.
        """
        post_data = {
            "title": "Test Post with No Tags",
            "content": "This is test content with no tags.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_names": []
        }
        
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        post_response = response.json()
        assert post_response["title"] == "Test Post with No Tags"
        assert post_response["tags"] == []
    
    def test_create_post_with_duplicate_tag_names(self, client: TestClient, auth_headers: dict):
        """
        Test creating a blog post with duplicate tag names in the request.
        Backend should deduplicate tags.
        """
        post_data = {
            "title": "Test Post with Duplicate Tags",
            "content": "This is test content with duplicate tags.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_names": ["React", "TypeScript", "React", "TypeScript"]  # Duplicates
        }
        
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        post_response = response.json()
        assert len(post_response["tags"]) == 2  # Should deduplicate
        
        tag_names = [tag["name"] for tag in post_response["tags"]]
        assert "React" in tag_names
        assert "TypeScript" in tag_names
    
    def test_create_post_tag_names_validation(self, client: TestClient, auth_headers: dict):
        """
        Test tag name validation in blog post creation.
        Backend should validate tag names and return appropriate errors.
        """
        post_data = {
            "title": "Test Post with Invalid Tags",
            "content": "This is test content with invalid tags.",
            "excerpt": "Test excerpt",
            "status": "draft",
            "tag_names": ["Valid-Tag", "", "A" * 51, "Invalid@Tag"]  # Mix of valid/invalid
        }
        
        response = client.post("/api/v1/posts", json=post_data, headers=auth_headers)
        
        # This MUST FAIL initially - should validate tag names
        if response.status_code == 400:
            error_detail = response.json()["detail"]
            assert "tag" in error_detail.lower()
        else:
            # If it succeeds, should only create valid tags
            assert response.status_code == 201
            post_response = response.json()
            tag_names = [tag["name"] for tag in post_response["tags"]]
            assert "Valid-Tag" in tag_names
            assert "" not in tag_names  # Empty name should be filtered out
            assert len([name for name in tag_names if len(name) > 50]) == 0  # Long names filtered


class TestProjectCreationWithTagNames:
    """Test project creation with tag names instead of tag IDs."""
    
    def test_create_project_with_tag_names(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test creating a project with tag names.
        Backend should auto-create tags that don't exist.
        """
        project_data = {
            "title": "Test Project with Tags",
            "description": "This is a test project with tag names.",
            "status": "in-progress",
            "tech_stack": ["React", "Node.js"],
            "tag_names": ["Web Development", "Full Stack", "JavaScript"]  # New field
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        project_response = response.json()
        assert project_response["title"] == "Test Project with Tags"
        assert len(project_response["tags"]) == 3
        
        tag_names = [tag["name"] for tag in project_response["tags"]]
        assert "Web Development" in tag_names
        assert "Full Stack" in tag_names
        assert "JavaScript" in tag_names
    
    def test_create_project_with_existing_and_new_tags(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test creating a project with mix of existing and new tag names.
        """
        # Create existing tag
        existing_tag = Tag(name="React", slug="react", color="#61dafb")
        db_session.add(existing_tag)
        db_session.commit()
        
        project_data = {
            "title": "Mixed Tags Project",
            "description": "Project with existing and new tags.",
            "status": "completed",
            "tech_stack": ["React", "Vue.js"],
            "tag_names": ["React", "Vue.js", "Frontend"]  # React exists, others new
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        project_response = response.json()
        assert len(project_response["tags"]) == 3
        
        # Verify no duplicate React tag was created
        react_tags = db_session.query(Tag).filter_by(name="React").all()
        assert len(react_tags) == 1


class TestTagCreationEndpoint:
    """Test tag creation endpoint functionality."""
    
    def test_create_tag_with_name_only(self, client: TestClient, auth_headers: dict):
        """
        Test creating a tag with only name provided.
        Backend should generate slug and set defaults.
        """
        tag_data = {
            "name": "Machine Learning"
        }
        
        response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        tag_response = response.json()
        assert tag_response["name"] == "Machine Learning"
        assert tag_response["slug"] == "machine-learning"
        assert "id" in tag_response
    
    def test_create_tag_with_color_and_description(self, client: TestClient, auth_headers: dict):
        """
        Test creating a tag with color and description.
        """
        tag_data = {
            "name": "Data Science",
            "color": "#FF6B35",
            "description": "Data analysis and machine learning"
        }
        
        response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 201
        
        tag_response = response.json()
        assert tag_response["name"] == "Data Science"
        assert tag_response["color"] == "#ff6b35"  # Should normalize to lowercase
        assert tag_response["description"] == "Data analysis and machine learning"
    
    def test_create_duplicate_tag_fails(self, client: TestClient, auth_headers: dict, db_session: Session):
        """
        Test that creating a duplicate tag returns proper error.
        """
        # Create existing tag
        existing_tag = Tag(name="Python", slug="python")
        db_session.add(existing_tag)
        db_session.commit()
        
        tag_data = {
            "name": "Python"  # Same name as existing tag
        }
        
        response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        
        # This MUST FAIL initially - should prevent duplicates
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "already exists" in error_detail.lower()
    
    def test_create_tag_invalid_name_fails(self, client: TestClient, auth_headers: dict):
        """
        Test that creating a tag with invalid name returns proper error.
        """
        tag_data = {
            "name": ""  # Empty name should fail
        }
        
        response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        
        # This MUST FAIL initially
        assert response.status_code == 422
        
        # Test with too long name
        tag_data = {
            "name": "A" * 51  # Exceeds 50 character limit
        }
        
        response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        assert response.status_code == 422